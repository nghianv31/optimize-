import 'dart:async';
import 'dart:collection';
import 'dart:developer';

import '../config/run_config.dart';
import '../workload/synthetic.dart';
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
      burn(t.iters);
      t.endUs = Timeline.now;
      _pending--;
    }
    _running = false;
  }
}

/// "Naive": mỗi tác vụ một Isolate.run, không giới hạn, không ưu tiên.
/// Dùng làm bằng chứng vấn đề (A7), không nằm trong dãy P0-P4.
class NaiveIsolateScheduler extends Scheduler {
  int _pending = 0;

  @override
  int get pending => _pending;

  @override
  void submit(Task t) {
    _pending++;
    t.startUs = Timeline.now;
    burnInIsolate(t.iters).then((_) {
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
      final chunkIters = (chunking && t.chunkable) ? cfg.chunkMs * Burner.itersPerMs : t.remainingIters;
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
