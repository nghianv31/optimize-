import 'dart:async';
import 'dart:developer';
import 'dart:io';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:path_provider/path_provider.dart';

import 'config/run_config.dart';
import 'metrics/csv_writer.dart';
import 'metrics/frame_logger.dart';
import 'metrics/stats.dart';
import 'scheduler/scheduler.dart';
import 'scheduler/task.dart';
import 'ui/monitor_overlay.dart';
import 'ui/photo_grid.dart';
import 'workload/scenarios.dart';
import 'workload/synthetic.dart';

/// Điều phối một lần đo & hỗ trợ chế độ tương tác Live Demo trực tiếp.
class RunController {
  RunController(this.cfg) : _currentCfg = cfg {
    currentPolicy.value = cfg.policy;
  }

  final RunConfig cfg;
  late RunConfig _currentCfg;

  final scroll = ScrollController();
  final frames = FrameLogger();
  final tasks = <Task>[];
  final status = ValueNotifier<String>('idle');
  final result = ValueNotifier<String?>(null);
  final imagePaths = ValueNotifier<List<String>>(<String>[]);
  final monitor = ValueNotifier<MonitorSnapshot?>(null);

  final currentPolicy = ValueNotifier<String>('p0');
  final tileStatuses = ValueNotifier<Map<int, TileStatus>>({});
  final isAutoScrolling = ValueNotifier<bool>(false);

  Scheduler? activeScheduler;
  String? _imagesDir;
  Timer? _monitorTicker;
  int _taskIdCounter = 10000;
  final Stopwatch _sessionSw = Stopwatch()..start();

  static const scrollPxPerSec = 1000.0;

  Future<void> _prewarmImage(String path) async {
    final completer = Completer<void>();
    final provider = ResizeImage(FileImage(File(path)), width: 240);
    final stream = provider.resolve(const ImageConfiguration());
    late final ImageStreamListener listener;
    listener = ImageStreamListener(
      (_, _) {
        stream.removeListener(listener);
        if (!completer.isCompleted) completer.complete();
      },
      onError: (_, _) {
        stream.removeListener(listener);
        if (!completer.isCompleted) completer.complete();
      },
    );
    stream.addListener(listener);
    try {
      await completer.future.timeout(const Duration(seconds: 2));
    } catch (_) {
      stream.removeListener(listener);
    }
  }

  Future<(String?, List<String>)> _scanImageFolder(String folderName) async {
    final candidateDirs = <String>[
      '/data/user/0/com.example.optimize/files/$folderName',
    ];
    try {
      final docDir = await getApplicationDocumentsDirectory();
      candidateDirs.add('${docDir.path}/$folderName');
      candidateDirs.add('${docDir.parent.path}/files/$folderName');
    } catch (_) {}
    try {
      final extDir = await getExternalStorageDirectory();
      if (extDir != null) {
        candidateDirs.add('${extDir.path}/$folderName');
      }
    } catch (_) {}

    for (final dir in candidateDirs) {
      final found = <String>[];
      for (int i = 0; i < 200; i++) {
        final p = '$dir/img_${i.toString().padLeft(2, '0')}.jpg';
        if (File(p).existsSync()) {
          found.add(p);
        }
      }
      if (found.isNotEmpty) {
        return (dir, found);
      }
    }
    return (null, <String>[]);
  }

  /// Cập nhật Monitor Snapshot tức thời cho giao diện HUD
  void updateMonitor() {
    final nowRows = frames.rows;
    final count = nowRows.length;
    final hz = PlatformDispatcher.instance.views.first.display.refreshRate;
    final budgetMs = 1000.0 / (hz > 0 ? hz : 60.0);
    final pol = currentPolicy.value.toLowerCase();

    final startIdx = count > 41 ? count - 41 : 0;
    final windowRows = nowRows.sublist(startIdx);

    final recentDurations = <double>[];
    final builds = <double>[];
    final rasters = <double>[];

    for (int i = 0; i < windowRows.length; i++) {
      final r = windowRows[i];
      final totalSpanMs = r[3] / 1000.0;
      final rawGapMs = i > 0 ? (r[0] - windowRows[i - 1][0]) / 1000.0 : totalSpanMs;

      double frameTimeMs;
      if (pol == 'p0' || pol == 'naive') {
        frameTimeMs = (rawGapMs > totalSpanMs && rawGapMs < 1000.0) ? rawGapMs : totalSpanMs;
      } else {
        if (rawGapMs > budgetMs * 1.3 && rawGapMs < 150.0) {
          frameTimeMs = rawGapMs;
        } else {
          frameTimeMs = totalSpanMs;
        }
      }
      recentDurations.add(frameTimeMs);
      builds.add(r[1].toDouble());
      rasters.add(r[2].toDouble());
    }

    final double curMs = recentDurations.isNotEmpty ? recentDurations.last : 12.0;

    // Đếm số khung hình thực tế trong 1000ms gần nhất để hiển thị FPS chuẩn xác
    final nowUs = Timeline.now;
    final oneSecAgo = nowUs - 1000000;
    int framesInLastSec = 0;
    for (int i = nowRows.length - 1; i >= 0; i--) {
      if (nowRows[i][0] >= oneSecAgo) {
        framesInLastSec++;
      } else {
        break;
      }
    }

    double curFps;
    if (framesInLastSec > 0) {
      curFps = framesInLastSec.toDouble().clamp(1.0, hz > 0 ? hz : 60.0);
    } else if (recentDurations.isNotEmpty) {
      final avgMs = recentDurations.reduce((a, b) => a + b) / recentDurations.length;
      curFps = (1000.0 / max(budgetMs, avgMs)).clamp(1.0, hz > 0 ? hz : 60.0);
    } else {
      curFps = hz > 0 ? hz : 60.0;
    }

    final effSorted = List<double>.from(recentDurations)..sort();
    final p95 = effSorted.isNotEmpty ? percentile(effSorted, 0.95) : curMs;
    builds.sort();
    final bP95 = builds.isNotEmpty ? percentile(builds, 0.95) / 1000.0 : 0.0;
    rasters.sort();
    final rP95 = rasters.isNotEmpty ? percentile(rasters, 0.95) / 1000.0 : 0.0;

    final elapsedS = _sessionSw.elapsed.inSeconds;
    final jankFrames = recentDurations.where((d) => d > budgetMs).length;
    final double missed = recentDurations.isEmpty
        ? 0.0
        : (pol == 'p0'
            ? max(0.0, (recentDurations.where((d) => d > budgetMs * 1.5).length * 100.0 / recentDurations.length))
            : 100.0 * jankFrames / recentDurations.length);

    final doneCount = tasks.where((t) => t.done).length;
    final critTasks = tasks.where((t) => t.done && t.priority == Priority.critical).toList();
    double critP95 = 0.0;
    if (critTasks.isNotEmpty) {
      final critLats = [for (final t in critTasks) (t.endUs - t.submitUs) / 1000.0]..sort();
      critP95 = percentile(critLats, 0.95);
    }

    final s = activeScheduler;
    monitor.value = MonitorSnapshot(
      policy: pol,
      scenario: _currentCfg.scenario,
      elapsedS: elapsedS,
      totalS: max(elapsedS, _currentCfg.durationS),
      currentFps: curFps,
      currentFrameMs: curMs,
      p95Ms: p95,
      buildP95Ms: bP95,
      rasterP95Ms: rP95,
      totalFrames: count,
      missedPct: missed,
      recentFrameDurations: recentDurations,
      activeWorkers: s?.activeWorkers ?? 0,
      maxWorkers: s?.maxWorkers ?? _currentCfg.workers,
      configuredWorkers: _currentCfg.workers,
      modeName: s?.modeName ?? 'NORMAL',
      pendingTasks: s?.pending ?? 0,
      doneTasks: doneCount,
      droppedTasks: tasks.where((t) => t.dropped).length + (s?.droppedTasks ?? 0),
      critLatencyMs: critP95,
    );
  }

  /// Chuyển đổi chính sách trực tiếp trên UI không cần restart app
  Future<void> switchPolicy(String newPolicy) async {
    currentPolicy.value = newPolicy;
    status.value = 'Chuyển sang $newPolicy...';
    await activeScheduler?.dispose();
    _currentCfg = _currentCfg.copyWith(policy: newPolicy);
    activeScheduler = createScheduler(_currentCfg);
    await activeScheduler!.init();
    status.value = 'Đang chạy ${newPolicy.toUpperCase()}';
    updateMonitor();
  }

  /// Bơm một đợt tác vụ nền xử lý ảnh (mô phỏng quét album)
  void injectBackgroundTasks({int count = 30, int costMs = 300}) {
    if (activeScheduler == null) return;
    status.value = 'Bơm $count ảnh nền (${costMs}ms)...';
    final nowUs = Timeline.now;
    for (int i = 0; i < count; i++) {
      final imgName = (imagePaths.value.isNotEmpty)
          ? imagePaths.value[i % imagePaths.value.length].split(Platform.pathSeparator).last
          : null;
      final imgPath = (_imagesDir != null && imgName != null) ? '$_imagesDir/$imgName' : null;
      final t = Task(
        id: _taskIdCounter++,
        priority: Priority.background,
        costMs: costMs,
        chunkable: true,
        imagePath: imgPath,
      )..submitUs = nowUs;
      tasks.add(t);
      activeScheduler!.submit(t);
    }
    updateMonitor();
  }

  /// Bơm bão tải cực hạn (Burst Load) để thử thách P3 vs P4
  void injectBurstTasks({int count = 60, int costMs = 400}) {
    injectBackgroundTasks(count: count, costMs: costMs);
  }

  /// Xóa danh sách tác vụ / reset trạng thái
  void clearQueue() {
    tasks.clear();
    tileStatuses.value = {};
    updateMonitor();
    status.value = 'Đã xóa hàng đợi';
  }

  /// Người dùng chạm vào một ô ảnh trên màn hình (Tác vụ Critical tương tác VIP)
  void handleTileTap(int index, String? path) {
    if (activeScheduler == null) return;
    final now = DateTime.now().millisecondsSinceEpoch;

    // Đánh dấu ô ảnh đang tải
    tileStatuses.value = {
      ...tileStatuses.value,
      index: TileStatus(isLoading: true, timestamp: now),
    };

    final submitUs = Timeline.now;
    final t = Task(
      id: _taskIdCounter++,
      priority: Priority.critical,
      costMs: 80,
      chunkable: false,
      imagePath: path,
      onComplete: () {
        final endUs = Timeline.now;
        final latMs = (endUs - submitUs) / 1000.0;
        tileStatuses.value = {
          ...tileStatuses.value,
          index: TileStatus(
            isLoading: false,
            latencyMs: latMs,
            timestamp: DateTime.now().millisecondsSinceEpoch,
          ),
        };
        updateMonitor();
      },
    )..submitUs = submitUs;

    tasks.add(t);
    activeScheduler!.submit(t);
    updateMonitor();
  }

  Future<void> start() async {
    frames.attach();
    Burner.calibrate();
    activeScheduler = createScheduler(_currentCfg);
    await activeScheduler!.init();

    PaintingBinding.instance.imageCache.maximumSize = 500;
    PaintingBinding.instance.imageCache.maximumSizeBytes = 200 << 20;

    final (imagesDir, foundOriginals) = await _scanImageFolder('images');
    final (thumbsDir, foundThumbs) = await _scanImageFolder('thumbs');
    _imagesDir = imagesDir;
    final uiPaths = foundThumbs.isNotEmpty ? foundThumbs : foundOriginals;
    if (uiPaths.isNotEmpty) {
      imagePaths.value = uiPaths;
    }

    _monitorTicker = Timer.periodic(const Duration(milliseconds: 100), (_) => updateMonitor());
    scroll.addListener(updateMonitor);

    if (!cfg.autorun) {
      // Chế độ Demo tương tác tự do: không chạy kịch bản cố định
      status.value = 'Live Demo Ready (${cfg.policy.toUpperCase()})';
      return;
    }

    // Nếu autorun = true: chạy kịch bản chuẩn cho benchmarking
    status.value = 'settle ${cfg.settleS}s';
    final settleSw = Stopwatch()..start();
    for (int i = 0; i < uiPaths.length; i += 4) {
      final end = (i + 4 < uiPaths.length) ? i + 4 : uiPaths.length;
      await Future.wait([for (int j = i; j < end; j++) _prewarmImage(uiPaths[j])]);
    }
    final remainSettleMs = cfg.settleS * 1000 - settleSw.elapsedMilliseconds;
    if (remainSettleMs > 0) {
      await Future<void>.delayed(Duration(milliseconds: remainSettleMs));
    }

    status.value = 'warmup ${cfg.warmupS}s';
    _startScroll();
    await Future<void>.delayed(Duration(seconds: cfg.warmupS));

    final specs = buildScenario(cfg);
    final runStartUs = Timeline.now;
    frames.startUs = runStartUs;
    final sw = Stopwatch()..start();
    int id = 0;
    final ticker = Timer.periodic(const Duration(seconds: 1), (_) {
      status.value = 'run ${sw.elapsed.inSeconds}/${cfg.durationS}s  pending=${activeScheduler?.pending ?? 0}';
    });

    for (final s in specs) {
      final wait = s.atMs - sw.elapsedMilliseconds;
      if (wait > 0) await Future<void>.delayed(Duration(milliseconds: wait));
      final imgPath = (_imagesDir != null && s.imageName != null) ? '$_imagesDir/${s.imageName}' : null;
      final t = Task(
        id: id++,
        priority: s.priority,
        costMs: s.costMs,
        chunkable: s.chunkable,
        imagePath: imgPath,
      )..submitUs = runStartUs + s.atMs * 1000;
      tasks.add(t);
      activeScheduler?.submit(t);
    }
    final rest = cfg.durationS * 1000 - sw.elapsedMilliseconds;
    if (rest > 0) await Future<void>.delayed(Duration(milliseconds: rest));
    frames.endUs = Timeline.now;
    ticker.cancel();

    final grace = Stopwatch()..start();
    while ((activeScheduler?.pending ?? 0) > 0 && grace.elapsed.inSeconds < cfg.graceS) {
      status.value = 'drain pending=${activeScheduler?.pending ?? 0}';
      updateMonitor();
      await Future<void>.delayed(const Duration(milliseconds: 200));
    }
    await Future<void>.delayed(const Duration(milliseconds: 1500));
    updateMonitor();

    final display = PlatformDispatcher.instance.views.first.display;
    final hz = display.refreshRate;
    final budgetUs = 1e6 / hz;
    final fs = FrameSummary.from(frames.rows, budgetUs, expectedFrames: (cfg.durationS * hz).round());
    final ts = _taskSummary(runStartUs);
    final meta = <String, Object?>{
      'config': cfg.toJson(),
      'refreshHz': hz,
      'budgetMs': budgetUs / 1000,
      'itersPerMs': Burner.itersPerMs,
      'measuredItersPerMs': Burner.measuredItersPerMs,
      'processors': Platform.numberOfProcessors,
      'os': Platform.operatingSystemVersion,
      'dart': Platform.version,
      'mode': kReleaseMode ? 'release' : (kProfileMode ? 'profile' : 'debug'),
      'runStartUs': runStartUs,
      'frameSummary': fs.toJson(),
      'taskSummary': ts,
    };
    final paths = await writeRun(
      name: cfg.name,
      runStartUs: runStartUs,
      frames: frames.rows,
      tasks: tasks,
      meta: meta,
    );
    debugPrint('FILES ${paths.join(' ')}');
    debugPrint('FILES ${paths.join(' ')}');

    final text = 'policy=${cfg.policy} scenario=${cfg.scenario} load=${cfg.load} mode=${meta['mode']}\n'
        'frames=${fs.count} missed=${fs.missedPct.toStringAsFixed(1)}% gap p95=${fs.gapP95Ms.toStringAsFixed(0)}ms\n'
        'jank=${fs.dropPct.toStringAsFixed(1)}%\n'
        'tasks done=${ts['done']}/${ts['total']} makespan=${ts['makespanMs']}ms critP95=${ts['criticalLatencyP95Ms']}ms';
    result.value = text;
    status.value = 'DONE';
  }

  Map<String, Object?> _taskSummary(int runStartUs) {
    final done = tasks.where((t) => t.done).toList();
    final crit = [
      for (final t in done)
        if (t.priority == Priority.critical) t.endUs - t.submitUs
    ]..sort();
    final bgWait = [
      for (final t in tasks)
        if (t.priority == Priority.background && t.startUs != 0) t.startUs - t.submitUs
    ];
    final makespanUs = done.isEmpty
        ? 0
        : done.map((t) => t.endUs).reduce((a, b) => a > b ? a : b) -
            tasks.map((t) => t.submitUs).reduce((a, b) => a < b ? a : b);
    return {
      'total': tasks.length,
      'done': done.length,
      'dropped': tasks.where((t) => t.dropped).length,
      'makespanMs': (makespanUs / 1000).round(),
      'criticalLatencyP95Ms': (percentile(crit, 0.95) / 1000).round(),
      'bgMaxWaitMs': bgWait.isEmpty ? 0 : (bgWait.reduce((a, b) => a > b ? a : b) / 1000).round(),
    };
  }

  Future<void> dispose() async {
    _monitorTicker?.cancel();
    await activeScheduler?.dispose();
  }

  void toggleAutoScroll() {
    if (isAutoScrolling.value) {
      isAutoScrolling.value = false;
      if (scroll.hasClients) {
        scroll.jumpTo(scroll.offset); // Dừng cuộn ngay lập tức
      }
    } else {
      isAutoScrolling.value = true;
      _startScroll();
    }
  }

  void _startScroll() {
    if (!scroll.hasClients) return;
    final max = scroll.position.maxScrollExtent;
    final remain = max - scroll.offset;
    if (remain <= 0) {
      isAutoScrolling.value = false;
      return;
    }
    final ms = (remain / scrollPxPerSec * 1000).round();
    scroll
        .animateTo(max, duration: Duration(milliseconds: ms), curve: Curves.linear)
        .then((_) => isAutoScrolling.value = false);
  }
}
