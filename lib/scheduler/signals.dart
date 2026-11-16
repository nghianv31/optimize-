import 'package:flutter/scheduler.dart';
import 'package:flutter/services.dart';

import '../metrics/stats.dart';
import 'thermal_sim.dart';
import 'mode_machine.dart';

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

/// Giao diện nguồn tín hiệu môi trường (nhiệt độ, mức pin).
abstract class SignalSource {
  Future<void> init() async {}
  DegradeMode sample(int elapsedMs);
  Future<void> dispose() async {}
}

/// Nguồn tín hiệu theo kịch bản có sẵn (dùng cho kịch bản mô phỏng S4).
/// Mặc định: 0–20s: Normal -> 20–40s: Conserve -> 40–60s: Critical.
class ScriptedSignalSource extends SignalSource {
  ScriptedSignalSource({
    this.conserveAtMs = 20000,
    this.criticalAtMs = 40000,
  });

  final int conserveAtMs;
  final int criticalAtMs;

  @override
  DegradeMode sample(int elapsedMs) {
    if (elapsedMs >= criticalAtMs) return DegradeMode.critical;
    if (elapsedMs >= conserveAtMs) return DegradeMode.conserve;
    return DegradeMode.normal;
  }
}

/// Nguồn tín hiệu đọc từ thiết bị Android thật qua MethodChannel.
/// Fallback an toàn về Normal nếu không có MethodChannel hoặc trên nền tảng khác.
class DeviceSignalSource extends SignalSource {
  static const _channel = MethodChannel('com.example.optimize/device_signals');
  double _lastTempC = 30.0;
  int _batteryLevel = 100;

  @override
  Future<void> init() async {
    await refresh();
  }

  Future<void> refresh() async {
    try {
      final res = await _channel.invokeMethod<Map>('getSignals');
      if (res != null) {
        _lastTempC = (res['tempC'] as num?)?.toDouble() ?? _lastTempC;
        _batteryLevel = (res['batteryLevel'] as num?)?.toInt() ?? _batteryLevel;
      }
    } catch (_) {
      // Bỏ qua nếu chạy trên máy ảo hoặc môi trường test
    }
  }

  @override
  DegradeMode sample(int elapsedMs) {
    // Ngưỡng nhiệt / pin tham khảo cho thiết bị di động:
    // Temp > 42°C hoặc Pin < 10% => Critical
    // Temp > 38°C hoặc Pin < 20% => Conserve
    if (_lastTempC >= 42.0 || (_batteryLevel > 0 && _batteryLevel <= 10)) {
      return DegradeMode.critical;
    }
    if (_lastTempC >= 38.0 || (_batteryLevel > 0 && _batteryLevel <= 20)) {
      return DegradeMode.conserve;
    }
    return DegradeMode.normal;
  }
}

/// Dùng nhiệt độ mô phỏng khi demo đang bật mô hình nhiệt, ngược lại dùng nguồn thật.
class SimAwareSignalSource extends SignalSource {
  SimAwareSignalSource(this.inner);
  final SignalSource inner;

  @override
  Future<void> init() => inner.init();

  @override
  DegradeMode sample(int elapsedMs) => ThermalSim.active ? ThermalSim.mode : inner.sample(elapsedMs);

  @override
  Future<void> dispose() => inner.dispose();
}
