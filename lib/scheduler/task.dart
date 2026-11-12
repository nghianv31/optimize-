import '../workload/synthetic.dart';

enum Priority { critical, visible, background }

class Task {
  final int id;
  final Priority priority;
  final int costMs;
  final bool chunkable;

  /// Các mốc thời gian (µs, tuyệt đối theo Timeline.now). 0 = chưa xảy ra.
  int submitUs = 0;
  int startUs = 0;
  int endUs = 0;

  Task({
    required this.id,
    required this.priority,
    required this.costMs,
    this.chunkable = false,
  });

  /// Tiến độ theo vòng lặp (dùng cho chunking).
  int doneIters = 0;
  int inFlight = 0; // số vòng lặp của chunk đang chạy

  int get iters => costMs * Burner.itersPerMs;
  int get remainingIters => iters - doneIters;
  bool get done => endUs != 0;
}
