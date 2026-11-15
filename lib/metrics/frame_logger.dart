import 'dart:developer';
import 'dart:ui';

import 'package:flutter/scheduler.dart';

/// Ghi FrameTiming vào RAM thời gian thực.
class FrameLogger {
  int startUs = 0;
  int endUs = 1 << 62;
  final List<List<int>> rows = []; // vsync, build, raster, total (µs, tuyệt đối)

  void attach() {
    if (startUs == 0) {
      startUs = Timeline.now; // Bắt đầu nhận frame ngay từ lúc attach
    }
    SchedulerBinding.instance.addTimingsCallback(_onTimings);
  }

  void _onTimings(List<FrameTiming> ts) {
    for (final t in ts) {
      final v = t.timestampInMicroseconds(FramePhase.vsyncStart);
      if (startUs > 0 && v < startUs) continue;
      if (v > endUs) continue;
      rows.add([
        v,
        t.buildDuration.inMicroseconds,
        t.rasterDuration.inMicroseconds,
        t.totalSpan.inMicroseconds,
      ]);
      // Giữ tối đa 500 frame gần nhất trong RAM khi chạy tương tác
      if (rows.length > 500) {
        rows.removeRange(0, rows.length - 300);
      }
    }
  }

  List<int> get totals => [for (final r in rows) r[3]];
}
