import 'dart:math';

import 'mode_machine.dart';

/// Mô hình nhiệt MÔ PHỎNG, chỉ dùng cho demo trình diễn (KHÔNG phải số đo thật).
///
/// Nhiệt tăng theo số worker đang chạy, tỏa dần về nhiệt độ môi trường.
/// Quá [throttleAt] thì "máy hạ xung": mỗi frame UI bị phạt thêm vài chục ms
/// (mô phỏng CPU chậm đi). Cùng một mô hình áp cho mọi chính sách; chỉ P4 đọc
/// được nhiệt độ này để tự giảm tải.
class ThermalSim {
  static const ambient = 30.0;
  static const conserveAt = 40.0;
  static const throttleAt = 42.0;
  static const criticalAt = 43.5;
  static const heatPerWorkerPerS = 0.10; // °C/s cho mỗi worker bận
  static const coolPerDegPerS = 0.02; // tỏa nhiệt tỉ lệ với (T - môi trường)

  static bool active = false;
  static double tempC = ambient;
  static double peakC = ambient;
  static double throttledS = 0;

  static void start({double startC = 39.0}) {
    active = true;
    tempC = startC;
    peakC = startC;
    throttledS = 0;
  }

  static void stop() {
    active = false;
    tempC = ambient;
  }

  static void step(double dtS, double busyWorkers) {
    if (!active) return;
    tempC += (heatPerWorkerPerS * busyWorkers - coolPerDegPerS * (tempC - ambient)) * dtS;
    tempC = max(ambient, tempC);
    peakC = max(peakC, tempC);
    if (throttling) throttledS += dtS;
  }

  static bool get throttling => active && tempC >= throttleAt;

  /// Thời gian phạt thêm cho mỗi frame UI khi đang hạ xung (ms).
  static double get penaltyMs => throttling ? 10 + 15 * ((tempC - throttleAt) / 2).clamp(0.0, 1.0) : 0;

  static DegradeMode get mode => tempC >= criticalAt
      ? DegradeMode.critical
      : (tempC >= conserveAt ? DegradeMode.conserve : DegradeMode.normal);
}
