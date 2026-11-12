import 'package:flutter/scheduler.dart';

import '../metrics/stats.dart';

/// Tín hiệu "UI đang bận" lấy tức thời từ khoảng cách giữa các frame
/// (persistent frame callback), không phải chờ FrameTiming được gom lô.
class FrameSignal {
  FrameSignal({this.window = 30});
  final int window;
  final _sw = Stopwatch()..start();
  final _gaps = <int>[]; // µs
  int _last = 0;

  void attach() => SchedulerBinding.instance.addPersistentFrameCallback((_) {
        final now = _sw.elapsedMicroseconds;
        if (_last != 0) {
          _gaps.add(now - _last);
          if (_gaps.length > window) _gaps.removeAt(0);
        }
        _last = now;
      });

  /// p95 khoảng cách giữa 2 frame gần nhất (ms), tính cả frame đang bị treo.
  double gapP95Ms() {
    if (_gaps.isEmpty) return 0;
    final s = [..._gaps]..sort();
    final p95 = percentile(s, 0.95) / 1000;
    final stall = (_sw.elapsedMicroseconds - _last) / 1000;
    return p95 > stall ? p95 : stall;
  }
}
