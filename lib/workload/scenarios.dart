import 'dart:math';

import '../config/run_config.dart';
import '../scheduler/task.dart';

class TaskSpec {
  final int atMs; // thời điểm đến dự kiến, tính từ đầu kịch bản
  final Priority priority;
  final int costMs;
  final bool chunkable;
  final String? imageName;
  const TaskSpec(this.atMs, this.priority, this.costMs, this.chunkable, [this.imageName]);
}

/// Sinh danh sách tác vụ xác định theo seed. Cùng seed => cùng kịch bản.
List<TaskSpec> buildScenario(RunConfig c) {
  switch (c.scenario) {
    case 's1':
      return _s1(c);
    case 's2':
      return _s2(c);
    case 's4':
      return _s1(c); // S4 dùng cùng mẫu tác vụ S1 nhưng kết hợp ScriptedSignalSource
    case 's_image':
      return _sImage(c);
    default:
      throw UnimplementedError('Scenario "${c.scenario}" chưa được cài');
  }
}

/// S1: cuộn kèm tải nền cố định.
///  - visible:    thumbnail 25 ms, ~4/giây
///  - background: đồng bộ 300 ms, ~1/giây
///  - background: lập chỉ mục 1500 ms (chunkable), ~1 mỗi 5 giây
///  - critical:   mở ảnh lớn 80 ms, 5 lần ngẫu nhiên
List<TaskSpec> _s1(RunConfig c) {
  final rnd = Random(c.seed);
  final durMs = c.durationS * 1000;
  final out = <TaskSpec>[];

  void periodic(int baseIntervalMs, Priority p, int cost, bool chunkable) {
    final interval = max(10, (baseIntervalMs / c.load).round());
    final jitter = max(1, interval ~/ 4);
    for (int t = 0; t < durMs; t += interval) {
      final at = t + rnd.nextInt(jitter);
      if (at < durMs) out.add(TaskSpec(at, p, cost, chunkable));
    }
  }

  periodic(250, Priority.visible, 25, true);
  periodic(1000, Priority.background, 300, true);
  periodic(5000, Priority.background, 1500, true);

  final lo = 5000, hi = max(lo + 1, durMs - 5000);
  for (int i = 0; i < 5; i++) {
    out.add(TaskSpec(lo + rnd.nextInt(hi - lo), Priority.critical, 80, false));
  }

  out.sort((a, b) => a.atMs.compareTo(b.atMs));
  return out;
}

/// S2: Kịch bản tải tăng dần theo 4 bậc thang (ramp-up load mỗi 15 giây).
/// Dùng để kiểm chứng thuật toán thích ứng AIMD (H4):
///  - Pha 1 (0–15s):  Tải nhẹ  (0.25x load)
///  - Pha 2 (15–30s): Tải vừa  (0.5x load)
///  - Pha 3 (30–45s): Tải chuẩn (1.0x load)
///  - Pha 4 (45–60s): Tải nặng (2.0x load, đẩy hệ thống vào bão hòa)
List<TaskSpec> _s2(RunConfig c) {
  final rnd = Random(c.seed);
  final durMs = c.durationS * 1000;
  final phaseDurationMs = max(1000, durMs ~/ 4);
  final out = <TaskSpec>[];

  final phaseMultipliers = [0.25, 0.5, 1.0, 2.0];

  for (int phase = 0; phase < 4; phase++) {
    final phaseStart = phase * phaseDurationMs;
    final phaseEnd = min(durMs, (phase + 1) * phaseDurationMs);
    final currentLoad = c.load * phaseMultipliers[phase];

    void periodicInPhase(int baseIntervalMs, Priority p, int cost, bool chunkable) {
      final interval = max(10, (baseIntervalMs / currentLoad).round());
      final jitter = max(1, interval ~/ 4);
      for (int t = phaseStart; t < phaseEnd; t += interval) {
        final at = t + rnd.nextInt(jitter);
        if (at < phaseEnd) out.add(TaskSpec(at, p, cost, chunkable));
      }
    }

    periodicInPhase(250, Priority.visible, 25, true);
    periodicInPhase(1000, Priority.background, 300, true);
    periodicInPhase(5000, Priority.background, 1500, true);
  }

  // Rải 8 tác vụ critical đều qua 4 pha
  for (int i = 0; i < 8; i++) {
    final segStart = (i * durMs) ~/ 8;
    final segEnd = ((i + 1) * durMs) ~/ 8;
    final at = segStart + rnd.nextInt(max(1, segEnd - segStart));
    if (at < durMs) {
      out.add(TaskSpec(at, Priority.critical, 80, false));
    }
  }

  out.sort((a, b) => a.atMs.compareTo(b.atMs));
  return out;
}

/// S_image: Kịch bản xử lý tập 80 ảnh DSLR thực tế (6016x4016, 6–12 MB/ảnh)
/// mô phỏng ứng dụng thư viện ảnh với 4 bậc thang tải [0.25x, 0.5x, 1.0x, 2.0x]:
///  - visible:    giải mã & tạo thumbnail lưới ảnh (30 ms, chunkable)
///  - background: nén & tính Perceptual Hash đồng bộ (300 ms, chunkable)
///  - background: phân tích histogram & lập chỉ mục 24MP (1500 ms, chunkable)
///  - critical:   8 lần người dùng chạm mở xem ảnh gốc (80 ms, không chunk)
List<TaskSpec> _sImage(RunConfig c) {
  const totalImages = 80;
  final rnd = Random(c.seed);
  final durMs = c.durationS * 1000;
  final phaseDurationMs = max(1000, durMs ~/ 4);
  final out = <TaskSpec>[];
  int imgIdx = 0;

  String nextImageName() {
    final name = 'img_${(imgIdx % totalImages).toString().padLeft(2, '0')}.jpg';
    imgIdx++;
    return name;
  }

  const phaseMultipliers = [0.25, 0.5, 1.0, 2.0];
  for (int phase = 0; phase < 4; phase++) {
    final phaseStart = phase * phaseDurationMs;
    final phaseEnd = min(durMs, (phase + 1) * phaseDurationMs);
    final currentLoad = c.load * phaseMultipliers[phase];

    void periodicInPhase(int baseIntervalMs, Priority p, int cost) {
      final interval = max(10, (baseIntervalMs / currentLoad).round());
      final jitter = max(1, interval ~/ 4);
      for (int t = phaseStart; t < phaseEnd; t += interval) {
        final at = t + rnd.nextInt(jitter);
        if (at < phaseEnd) {
          out.add(TaskSpec(at, p, cost, true, nextImageName()));
        }
      }
    }

    periodicInPhase(250, Priority.visible, 30);
    periodicInPhase(1000, Priority.background, 300);
    periodicInPhase(5000, Priority.background, 1500);
  }

  for (int i = 0; i < 8; i++) {
    final segStart = (i * durMs) ~/ 8;
    final segEnd = ((i + 1) * durMs) ~/ 8;
    final at = segStart + rnd.nextInt(max(1, segEnd - segStart));
    if (at < durMs) {
      final name = 'img_${(i % totalImages).toString().padLeft(2, '0')}.jpg';
      out.add(TaskSpec(at, Priority.critical, 80, false, name));
    }
  }

  out.sort((a, b) => a.atMs.compareTo(b.atMs));
  return out;
}
