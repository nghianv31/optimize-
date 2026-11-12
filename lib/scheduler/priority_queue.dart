import 'dart:collection';

import 'task.dart';

/// Chọn chỉ số tác vụ chạy tiếp theo trong hàng đợi [q].
/// - FIFO nếu !usePriority.
/// - Ngược lại: điểm = rank*agingMs - thời gian chờ(ms); nhỏ nhất thắng, hòa thì đến trước.
///   Aging: tác vụ ưu tiên thấp chờ đủ lâu sẽ vượt tác vụ ưu tiên cao mới đến.
int pickNext(List<Task> q, int nowUs, {required bool usePriority, required int agingMs}) {
  if (!usePriority || q.length == 1) return 0;
  int best = 0;
  double bestScore = double.infinity;
  for (int i = 0; i < q.length; i++) {
    final t = q[i];
    final waitMs = (nowUs - t.submitUs) / 1000.0;
    final score = t.priority.index * agingMs - waitMs;
    if (score < bestScore) {
      bestScore = score;
      best = i;
    }
  }
  return best;
}

/// Hàng đợi 3 mức (hoặc 1 mức FIFO khi !usePriority).
/// Trong mỗi mức, đầu hàng là tác vụ cũ nhất => chỉ cần so 3 đầu hàng (O(1)),
/// quan trọng khi hàng đợi dài hàng nghìn tác vụ lúc quá tải.
class TaskQueue {
  TaskQueue({required this.usePriority}) : _q = List.generate(3, (_) => Queue<Task>());
  final bool usePriority;
  final List<Queue<Task>> _q;

  Queue<Task> _bucket(Task t) => _q[usePriority ? t.priority.index : 0];

  void add(Task t) => _bucket(t).addLast(t);

  /// Tác vụ đang dở (đã chạy một chunk) quay lại đầu hàng của mức mình.
  void addFront(Task t) => _bucket(t).addFirst(t);

  int get length => _q.fold(0, (a, b) => a + b.length);
  bool get isEmpty => length == 0;

  /// Lấy tác vụ có điểm nhỏ nhất (rank*agingMs - chờ) trong các đầu hàng thỏa [eligible].
  Task? popNext(int nowUs, {required int agingMs, bool Function(Task)? eligible}) {
    Queue<Task>? best;
    double bestScore = double.infinity;
    for (final q in _q) {
      if (q.isEmpty) continue;
      final t = q.first;
      if (eligible != null && !eligible(t)) continue;
      final score = usePriority ? t.priority.index * agingMs - (nowUs - t.submitUs) / 1000.0 : 0.0;
      if (best == null || score < bestScore) {
        best = q;
        bestScore = score;
      }
    }
    return best?.removeFirst();
  }
}
