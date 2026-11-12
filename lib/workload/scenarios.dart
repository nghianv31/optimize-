import 'dart:math';

import '../config/run_config.dart';
import '../scheduler/task.dart';

class TaskSpec {
  final int atMs; // thời điểm đến dự kiến, tính từ đầu kịch bản
  final Priority priority;
  final int costMs;
  final bool chunkable;
  const TaskSpec(this.atMs, this.priority, this.costMs, this.chunkable);
}

/// Sinh danh sách tác vụ xác định theo seed. Cùng seed => cùng kịch bản.
List<TaskSpec> buildScenario(RunConfig c) {
  switch (c.scenario) {
    case 's1':
      return _s1(c);
    default:
      throw UnimplementedError('Scenario "${c.scenario}" chưa được cài');
  }
}

/// S1: cuộn kèm tải nền.
///  - visible:    thumbnail 25 ms, ~4/giây
///  - background: đồng bộ 300 ms, ~1/giây
///  - background: lập chỉ mục 1500 ms (chunkable), ~1 mỗi 5 giây
///  - critical:   mở ảnh lớn 80 ms, 5 lần ngẫu nhiên
/// `load` nhân tốc độ đến của 3 loại đầu (không đổi kích thước tác vụ).
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
