import 'dart:math';

import '../scheduler/task.dart';
import 'scenarios.dart';

/// Một pha của kịch bản demo trình diễn (60 s) cho giáo viên.
class DemoPhase {
  final String title;
  final String hint; // điều cần quan sát
  final int startS;
  final int endS;
  final double load; // hệ số tốc độ đến (như LOAD của S1)
  final bool thermal; // bật mô hình nhiệt mô phỏng
  final int burst; // số tác vụ nền ập đến ngay đầu pha
  const DemoPhase(this.title, this.hint, this.startS, this.endS, this.load, {this.thermal = false, this.burst = 0});
}

/// Giá trị khởi điểm, cần hiệu chỉnh trên máy thật (A04e, 8 worker).
const demoPhases = <DemoPhase>[
  DemoPhase('1 · TẢI NHẸ', 'Cả 5 chính sách đều mượt: đây là mốc so sánh.', 0, 10, 4),
  DemoPhase('2 · TẢI VỪA', 'Hàng đợi bắt đầu hình thành. Xem ô "BẤM ẢNH": P1 chờ lâu, P2/P3/P4 chen lên đầu.', 10, 22, 48),
  DemoPhase('3 · TẢI NẶNG', 'Tranh CPU với UI. Xem quả bóng: P0 đứng hình, P1/P2 giật, P3/P4 vẫn mượt.', 22, 35, 96),
  DemoPhase('4 · BÃO TẢI', '800 tác vụ ập đến. Xem Queue/Drop: P3 để phình to, P4 chặn ở ngưỡng.', 35, 45, 96, burst: 800),
  DemoPhase('5 · MÁY NÓNG (mô phỏng)', 'Nhiệt tăng theo số worker bận. Vượt 42°C: máy hạ xung, UI chậm. P4 đọc nhiệt độ nên giảm tải sớm.', 45, 60, 96, thermal: true),
];

const demoDurationS = 60;

DemoPhase demoPhaseAt(double sec) {
  for (final p in demoPhases) {
    if (sec < p.endS) return p;
  }
  return demoPhases.last;
}

/// Kịch bản xác định theo seed: tác vụ nền theo từng pha + 12 lần "bấm ảnh" (critical).
List<TaskSpec> buildDemoScenario(int seed) {
  final rnd = Random(seed);
  final out = <TaskSpec>[];

  for (final ph in demoPhases) {
    void periodic(int baseMs, Priority p, int cost) {
      final interval = max(10, (baseMs / ph.load).round());
      final jitter = max(1, interval ~/ 4);
      for (int t = ph.startS * 1000; t < ph.endS * 1000; t += interval) {
        final at = t + rnd.nextInt(jitter);
        if (at < ph.endS * 1000) out.add(TaskSpec(at, p, cost, true));
      }
    }

    periodic(250, Priority.visible, 25);
    periodic(1000, Priority.background, 300);
    periodic(5000, Priority.background, 1500);

    for (int i = 0; i < ph.burst; i++) {
      out.add(TaskSpec(ph.startS * 1000 + (i * 500) ~/ ph.burst, Priority.background, 300, true));
    }
  }

  // 12 lần người dùng bấm ảnh, cách nhau 5 s
  for (int s = 4; s < demoDurationS; s += 5) {
    out.add(TaskSpec(s * 1000 + rnd.nextInt(500), Priority.critical, 80, false));
  }

  out.sort((a, b) => a.atMs.compareTo(b.atMs));
  return out;
}

/// Kết quả một lần demo của một chính sách, để dựng bảng so sánh.
class DemoResult {
  final String policy;
  final double missedPct; // % frame bị bỏ so với kỳ vọng
  final double critP95Ms;
  final double donePct;
  final int dropped;
  final double peakTempC;
  final double throttledS;
  final double peakRamMb;
  const DemoResult({
    required this.policy,
    required this.missedPct,
    required this.critP95Ms,
    required this.donePct,
    required this.dropped,
    required this.peakTempC,
    required this.throttledS,
    this.peakRamMb = 0.0,
  });

  Map<String, Object?> toJson() => {
        'policy': policy,
        'missedPct': double.parse(missedPct.toStringAsFixed(2)),
        'critP95Ms': critP95Ms.round(),
        'donePct': double.parse(donePct.toStringAsFixed(1)),
        'dropped': dropped,
        'peakTempC': double.parse(peakTempC.toStringAsFixed(1)),
        'throttledS': double.parse(throttledS.toStringAsFixed(1)),
        'peakRamMb': double.parse(peakRamMb.toStringAsFixed(1)),
      };
}
