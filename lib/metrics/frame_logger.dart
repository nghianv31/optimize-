import 'dart:ui';

import 'package:flutter/scheduler.dart';

/// Ghi FrameTiming vào RAM. Chỉ nhận frame có vsyncStart trong [startUs, endUs].
/// (Callback của engine được gom lô nên có thể đến muộn; lọc theo timestamp.)
class FrameLogger {
  int startUs = 0;
  int endUs = 1 << 62;
  final List<List<int>> rows = []; // vsync, build, raster, total (µs, tuyệt đối)

  void attach() => SchedulerBinding.instance.addTimingsCallback(_onTimings);

  void _onTimings(List<FrameTiming> ts) {
    if (startUs == 0) return;
    for (final t in ts) {
      final v = t.timestampInMicroseconds(FramePhase.vsyncStart);
      if (v < startUs || v > endUs) continue;
      rows.add([
        v,
        t.buildDuration.inMicroseconds,
        t.rasterDuration.inMicroseconds,
        t.totalSpan.inMicroseconds,
      ]);
    }
  }

  List<int> get totals => [for (final r in rows) r[3]];
}
