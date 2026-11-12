import 'dart:async';
import 'dart:developer';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';

import 'config/run_config.dart';
import 'metrics/csv_writer.dart';
import 'metrics/frame_logger.dart';
import 'metrics/stats.dart';
import 'scheduler/scheduler.dart';
import 'scheduler/task.dart';
import 'workload/scenarios.dart';
import 'workload/synthetic.dart';

/// Điều phối một lần đo: settle → warm-up → kịch bản → drain → ghi CSV.
class RunController {
  RunController(this.cfg);

  final RunConfig cfg;
  final scroll = ScrollController();
  final frames = FrameLogger();
  final tasks = <Task>[];
  final status = ValueNotifier<String>('idle');
  final result = ValueNotifier<String?>(null);

  static const scrollPxPerSec = 1000.0;

  Future<void> start() async {
    frames.attach();
    Burner.calibrate();
    final scheduler = createScheduler(cfg);
    await scheduler.init(); // spawn worker trước khi đo
    final specs = buildScenario(cfg);

    status.value = 'settle ${cfg.settleS}s';
    await Future<void>.delayed(Duration(seconds: cfg.settleS));

    status.value = 'warmup ${cfg.warmupS}s';
    _startScroll();
    await Future<void>.delayed(Duration(seconds: cfg.warmupS));

    // ---- Kịch bản được ghi ----
    final runStartUs = Timeline.now;
    frames.startUs = runStartUs;
    final sw = Stopwatch()..start();
    int id = 0;
    final ticker = Timer.periodic(const Duration(seconds: 1), (_) {
      status.value = 'run ${sw.elapsed.inSeconds}/${cfg.durationS}s  pending=${scheduler.pending}';
    });

    for (final s in specs) {
      final wait = s.atMs - sw.elapsedMilliseconds;
      if (wait > 0) await Future<void>.delayed(Duration(milliseconds: wait));
      final t = Task(id: id++, priority: s.priority, costMs: s.costMs, chunkable: s.chunkable)
        // Dùng thời điểm đến dự kiến để độ trễ gồm cả thời gian main bị chặn
        ..submitUs = runStartUs + s.atMs * 1000;
      tasks.add(t);
      scheduler.submit(t);
    }
    final rest = cfg.durationS * 1000 - sw.elapsedMilliseconds;
    if (rest > 0) await Future<void>.delayed(Duration(milliseconds: rest));
    frames.endUs = Timeline.now;
    ticker.cancel();

    // ---- Drain ----
    final grace = Stopwatch()..start();
    while (scheduler.pending > 0 && grace.elapsed.inSeconds < cfg.graceS) {
      status.value = 'drain pending=${scheduler.pending}';
      await Future<void>.delayed(const Duration(milliseconds: 200));
    }
    await Future<void>.delayed(const Duration(milliseconds: 1500)); // chờ FrameTiming gom lô
    await scheduler.dispose();

    // ---- Tổng hợp & ghi ----
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

    final text = 'policy=${cfg.policy} scenario=${cfg.scenario} load=${cfg.load} mode=${meta['mode']}\n'
        'frames=${fs.count} missed=${fs.missedPct.toStringAsFixed(1)}% gap p95=${fs.gapP95Ms.toStringAsFixed(0)}ms p99=${fs.gapP99Ms.toStringAsFixed(0)}ms\n'
        'jank=${fs.dropPct.toStringAsFixed(1)}% (total>budget=${fs.dropTotalPct.toStringAsFixed(1)}%)\n'
        'p95 total=${fs.p95Ms.toStringAsFixed(1)} build=${fs.buildP95Ms.toStringAsFixed(1)} raster=${fs.rasterP95Ms.toStringAsFixed(1)}ms '
        'p99=${fs.p99Ms.toStringAsFixed(1)}ms >700ms=${fs.extreme}\n'
        'tasks done=${ts['done']}/${ts['total']} makespan=${ts['makespanMs']}ms '
        'critP95=${ts['criticalLatencyP95Ms']}ms bgMaxWait=${ts['bgMaxWaitMs']}ms';
    result.value = text;
    status.value = 'DONE';
    debugPrint('RESULT\n$text');
    debugPrint('FILES ${paths.join(' ')}');
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
      'makespanMs': (makespanUs / 1000).round(),
      'criticalLatencyP95Ms': (percentile(crit, 0.95) / 1000).round(),
      'bgMaxWaitMs': bgWait.isEmpty ? 0 : (bgWait.reduce((a, b) => a > b ? a : b) / 1000).round(),
    };
  }

  void _startScroll() {
    if (!scroll.hasClients) return;
    final max = scroll.position.maxScrollExtent;
    final ms = (max / scrollPxPerSec * 1000).round();
    scroll.animateTo(max, duration: Duration(milliseconds: ms), curve: Curves.linear);
  }
}
