import 'dart:async';
import 'dart:collection';
import 'dart:developer';
import 'dart:math';

import '../config/run_config.dart';
import '../workload/image_workload.dart';
import '../workload/synthetic.dart';
import 'aimd.dart';
import 'mode_machine.dart';
import 'priority_queue.dart';
import 'signals.dart';
import 'task.dart';
import 'worker_pool.dart';

abstract class Scheduler {
  /// Số tác vụ đã gửi nhưng chưa xong.
  int get pending;
  void submit(Task t);
  Future<void> init() async {}
  Future<void> dispose() async {}

  int get activeWorkers => 0;
  int get maxWorkers => 0;
  int get droppedTasks => 0;
  String get modeName => 'Normal';
}

Scheduler createScheduler(RunConfig cfg) {
  switch (cfg.policy) {
    case 'p0':
      return P0Scheduler();
    case 'naive':
      return NaiveIsolateScheduler();
    case 'p1':
      return PoolScheduler(cfg, usePriority: false);
    case 'p2':
      return PoolScheduler(cfg, usePriority: true);
    // P3 và các biến thể để tách đóng góp từng cơ chế (ablation):
    case 'p3c': // P2 + chunking
      return PoolScheduler(cfg, usePriority: true, chunking: true);
    case 'p3r': // P2 + chunking + dành 1 worker cho critical
      return PoolScheduler(cfg, usePriority: true, chunking: true, reserveCritical: true);
    case 'p3': // P2 + chunking + dành worker + nhường frame
      return PoolScheduler(cfg, usePriority: true, chunking: true, reserveCritical: true, yieldToFrames: true);
    // P4: Lập lịch thích ứng với AIMD + Mode Machine suy giảm + Backpressure
    case 'p4':
      return P4Scheduler(cfg, useAimd: true, useModes: true, useBackpressure: true);
    case 'p4_aimd': // Ablation: chỉ dùng AIMD thích ứng worker, không dùng chế độ suy giảm
      return P4Scheduler(cfg, useAimd: true, useModes: false, useBackpressure: false);
    case 'none':
      return NoneScheduler();
    default:
      throw UnimplementedError('Policy "${cfg.policy}" chưa được cài');
  }
}

/// Baseline: bỏ qua mọi tác vụ, chỉ đo UI thuần (nền để so sánh jank).
class NoneScheduler extends Scheduler {
  @override
  int get pending => 0;
  @override
  void submit(Task t) {}
}

/// P0: mọi tác vụ chạy tuần tự trên main isolate (mốc thấp nhất).
class P0Scheduler extends Scheduler {
  final _q = Queue<Task>();
  bool _running = false;
  int _pending = 0;

  @override
  int get pending => _pending;

  @override
  int get activeWorkers => _running ? 1 : 0;

  @override
  int get maxWorkers => 1;

  @override
  int get droppedTasks => 0;

  @override
  String get modeName => 'MAIN_ISOLATE';

  @override
  void submit(Task t) {
    _pending++;
    _q.add(t);
    _pump();
  }

  Future<void> _pump() async {
    if (_running) return;
    _running = true;
    while (_q.isNotEmpty) {
      // Nhường event loop giữa các tác vụ để frame còn cơ hội chạy
      await Future<void>.delayed(Duration.zero);
      final t = _q.removeFirst();
      t.startUs = Timeline.now;
      if (t.imagePath != null) {
        processImageChunk(t.imagePath, t.iters, 0, t.iters);
      } else {
        burn(t.iters);
      }
      t.endUs = Timeline.now;
      _pending--;
    }
    _running = false;
  }

  @override
  Future<void> dispose() async {
    _q.clear();
    _pending = 0;
  }
}

/// "Naive": mỗi tác vụ một Isolate.run, không giới hạn, không ưu tiên.
/// Dùng làm bằng chứng vấn đề (A7), không nằm trong dãy P0-P4.
class NaiveIsolateScheduler extends Scheduler {
  int _pending = 0;

  @override
  int get pending => _pending;

  @override
  int get activeWorkers => _pending;

  @override
  int get maxWorkers => 999;

  @override
  int get droppedTasks => 0;

  @override
  String get modeName => 'NAIVE';

  @override
  void submit(Task t) {
    _pending++;
    t.startUs = Timeline.now;
    final fut = t.imagePath != null
        ? processImageInIsolate(t.imagePath, t.iters)
        : burnInIsolate(t.iters);
    fut.then((_) {
      t.endUs = Timeline.now;
      _pending--;
    });
  }
}

/// P1 (FIFO), P2 (3 mức + aging), P3* (thêm chunking / reserve / nhường frame).
class PoolScheduler extends Scheduler {
  PoolScheduler(
    this.cfg, {
    required this.usePriority,
    this.chunking = false,
    this.reserveCritical = false,
    this.yieldToFrames = false,
  })  : _pool = WorkerPool(cfg.workers),
        _queue = TaskQueue(usePriority: usePriority);

  final RunConfig cfg;
  final bool usePriority;
  final bool chunking; // cắt tác vụ chunkable thành chunk cfg.chunkMs
  final bool reserveCritical; // luôn chừa 1 worker cho critical
  final bool yieldToFrames; // UI bận => hoãn background
  final WorkerPool _pool;
  final TaskQueue _queue;
  final _running = <int, Task>{};
  final _frames = FrameSignal();
  Timer? _tick;
  bool _busy = false;
  int _runningNonCritical = 0;
  int _pending = 0;

  /// Số lần chuyển trạng thái UI bận/rảnh (để kiểm tra không chập chờn).
  int busyToggles = 0;

  @override
  int get pending => _pending;

  @override
  int get activeWorkers => _running.length;

  @override
  int get maxWorkers => cfg.workers;

  @override
  int get droppedTasks => 0;

  @override
  String get modeName => yieldToFrames && _busy ? 'YIELDING' : 'NORMAL';

  @override
  Future<void> init() async {
    await _pool.start();
    for (final w in _pool.workers) {
      w.onDone = _onDone;
    }
    if (yieldToFrames) {
      _frames.attach();
      // Vòng quyết định mỗi 100 ms: cập nhật cờ UI bận (có hysteresis) rồi dispatch lại
      _tick = Timer.periodic(const Duration(milliseconds: 100), (_) {
        final g = _frames.gapP95Ms();
        final was = _busy;
        if (!_busy && g > cfg.yieldMs) _busy = true;
        if (_busy && g < cfg.yieldMs * 0.8) _busy = false;
        if (was != _busy) busyToggles++;
        _dispatch();
      });
    }
  }

  @override
  void submit(Task t) {
    _pending++;
    _queue.add(t);
    _dispatch();
  }

  void _onDone(int id) {
    final t = _running.remove(id)!;
    if (t.priority != Priority.critical) _runningNonCritical--;
    t.doneIters += t.inFlight;
    if (t.remainingIters > 0) {
      _queue.addFront(t); // chunk kế tiếp; ranh giới chunk = điểm chen ngang
    } else {
      t.endUs = Timeline.now;
      _pending--;
    }
    _dispatch();
  }

  bool Function(Task) _eligible(int now) => (t) {
        if (t.priority == Priority.critical) return true;
        if (reserveCritical && cfg.workers > 1 && _runningNonCritical >= cfg.workers - 1) return false;
        if (yieldToFrames &&
            _busy &&
            t.priority == Priority.background &&
            now - t.submitUs < cfg.deferCapMs * 1000) {
          return false; // quá deferCapMs thì không hoãn nữa (chống đói)
        }
        return true;
      };

  void _dispatch() {
    while (true) {
      final w = _pool.acquire();
      if (w == null) return;
      final now = Timeline.now;
      final t = _queue.popNext(now, agingMs: cfg.agingMs, eligible: _eligible(now));
      if (t == null) return;
      if (t.startUs == 0) t.startUs = now;
      final chunkIters = (chunking && t.chunkable) ? cfg.chunkMs * Burner.effectiveItersPerMs : t.remainingIters;
      t.inFlight = chunkIters < t.remainingIters ? chunkIters : t.remainingIters;
      _running[t.id] = t;
      if (t.priority != Priority.critical) _runningNonCritical++;
      w.run(t, t.inFlight);
    }
  }

  @override
  Future<void> dispose() async {
    _tick?.cancel();
    _pool.dispose();
  }
}

/// P4: Bộ lập lịch thích ứng tự động (Adaptive Scheduler).
/// Tích hợp đầy đủ:
///  - D1: AIMD (+1 khi UI tốt, ×0.5 khi UI quá tải) điều chỉnh số lượng worker.
///  - D2: SignalSource (tín hiệu giả lập S4 hoặc nhiệt độ/pin thật từ Android).
///  - D3: ModeMachine (Normal, Conserve, Critical) kèm trễ hysteresis chống chập chờn.
///  - D4: Backpressure (Load shedding tác vụ nền khi hàng đợi dồn ứ).
///  - Kế thừa cơ chế chunking 80ms và worker dự phòng (reserve) cho critical từ P3.
class P4Scheduler extends Scheduler {
  P4Scheduler(
    this.cfg, {
    this.useAimd = true,
    this.useModes = true,
    this.useBackpressure = true,
  })  : _pool = WorkerPool(cfg.workers),
        _queue = TaskQueue(usePriority: true),
        aimd = AimdController(
          minWorkers: 1,
          maxWorkers: cfg.workers,
          targetGapMs: cfg.yieldMs.toDouble(),
          initialWorkers: min(2.0, cfg.workers.toDouble()),
        ),
        modeMachine = ModeMachine(hysteresisMs: 5000),
        signalSource = cfg.scenario == 's4' ? ScriptedSignalSource() : DeviceSignalSource();

  final RunConfig cfg;
  final bool useAimd;
  final bool useModes;
  final bool useBackpressure;

  final WorkerPool _pool;
  final TaskQueue _queue;
  final AimdController aimd;
  final ModeMachine modeMachine;
  final SignalSource signalSource;
  final FrameSignal _frames = FrameSignal();

  final _running = <int, Task>{};
  Timer? _tick;
  bool _busy = false;
  int _runningNonCritical = 0;
  int _pending = 0;
  int _droppedTasks = 0;
  final Stopwatch _uptime = Stopwatch();

  DegradeMode get currentMode => modeMachine.currentMode;

  /// Giới hạn số worker đang chạy được cấp phép tại thời điểm hiện tại.
  int get currentWorkerCap {
    if (!useAimd) return cfg.workers;
    int cap = aimd.workerCount;
    if (useModes) {
      if (currentMode == DegradeMode.critical) {
        // Chế độ nguy cấp: chỉ giữ 1 worker tối thiểu để bảo vệ hệ thống
        cap = 1;
      } else if (currentMode == DegradeMode.conserve) {
        // Chế độ tiết kiệm: cắt bớt 25% trần worker
        cap = max(1, (cap * 0.75).round());
      }
    }
    return cap.clamp(1, cfg.workers);
  }

  @override
  int get pending => _pending;

  @override
  int get activeWorkers => _running.length;

  @override
  int get maxWorkers => currentWorkerCap;

  @override
  int get droppedTasks => _droppedTasks;

  @override
  String get modeName => currentMode.name.toUpperCase();

  @override
  Future<void> init() async {
    _uptime.start();
    await _pool.start();
    for (final w in _pool.workers) {
      w.onDone = _onDone;
    }
    await signalSource.init();
    _frames.attach();

    // Vòng lặp điều phối thích ứng mỗi 100 ms
    _tick = Timer.periodic(const Duration(milliseconds: 100), (_) {
      final nowUs = Timeline.now;
      final g = _frames.gapP95Ms();

      // Nhận diện UI bận với hysteresis chống rung
      if (!_busy && g > cfg.yieldMs) _busy = true;
      if (_busy && g < cfg.yieldMs * 0.8) _busy = false;

      // D1: Cập nhật AIMD theo khoảng cách frame (epoch pacing 500ms)
      if (useAimd) {
        aimd.update(g, nowUs);
      }

      // D2 & D3: Lấy mẫu tín hiệu môi trường và cập nhật Mode Machine
      if (useModes) {
        final targetMode = signalSource.sample(_uptime.elapsedMilliseconds);
        modeMachine.update(targetMode, nowUs);
      }

      _dispatch();
    });
  }

  @override
  void submit(Task t) {
    final now = Timeline.now;

    // D4: Backpressure & Load shedding
    // 1. Nếu đang ở DegradeMode.critical, loại bỏ ngay tác vụ nền & visible
    if (useModes && currentMode == DegradeMode.critical && t.priority != Priority.critical) {
      _droppedTasks++;
      t.dropped = true;
      t.startUs = now;
      t.endUs = now;
      return;
    }

    // 2. Nếu hàng đợi quá dài, loại bỏ tác vụ nền đến muộn
    if (useBackpressure && t.priority == Priority.background) {
      final backpressureCap = max(20, cfg.workers * 10);
      if (_queue.length >= backpressureCap) {
        _droppedTasks++;
        t.dropped = true;
        t.startUs = now;
        t.endUs = now;
        return;
      }
    }

    _pending++;
    _queue.add(t);
    _dispatch();
  }

  void _onDone(int id) {
    final t = _running.remove(id)!;
    if (t.priority != Priority.critical) _runningNonCritical--;
    t.doneIters += t.inFlight;
    if (t.remainingIters > 0) {
      _queue.addFront(t);
    } else {
      t.endUs = Timeline.now;
      _pending--;
    }
    _dispatch();
  }

  bool Function(Task) _eligible(int now) => (t) {
        // Tác vụ Critical luôn luôn hợp lệ để chạy ngay lập tức nếu có bất kỳ worker nào rảnh
        if (t.priority == Priority.critical) return true;

        final cap = currentWorkerCap;
        // Tác vụ thông thường (non-critical) bị giới hạn bởi:
        // 1. Worker cap của AIMD / DegradeMode
        // 2. Không được chiếm worker cuối cùng (luôn chừa ít nhất 1 worker trong pool cho Critical khi pool > 1)
        final nonCriticalLimit = min(cap, max(1, cfg.workers - 1));
        if (_runningNonCritical >= nonCriticalLimit) return false;

        // Nhường frame: Tạm hoãn tác vụ background khi UI đang bận
        if (_busy && t.priority == Priority.background && now - t.submitUs < cfg.deferCapMs * 1000) {
          return false;
        }

        // Ở chế độ Conserve: kéo dài thời gian hoãn của tác vụ background
        if (useModes && currentMode == DegradeMode.conserve && t.priority == Priority.background) {
          if (now - t.submitUs < cfg.deferCapMs * 2000) {
            return false;
          }
        }

        return true;
      };

  void _dispatch() {
    while (true) {
      final w = _pool.acquire();
      if (w == null) return;
      final now = Timeline.now;
      final t = _queue.popNext(now, agingMs: cfg.agingMs, eligible: _eligible(now));
      if (t == null) return;
      if (t.startUs == 0) t.startUs = now;
      final chunkIters = t.chunkable ? cfg.chunkMs * Burner.effectiveItersPerMs : t.remainingIters;
      t.inFlight = chunkIters < t.remainingIters ? chunkIters : t.remainingIters;
      _running[t.id] = t;
      if (t.priority != Priority.critical) _runningNonCritical++;
      w.run(t, t.inFlight);
    }
  }

  @override
  Future<void> dispose() async {
    _tick?.cancel();
    await signalSource.dispose();
    _pool.dispose();
  }
}
