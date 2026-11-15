import '../workload/synthetic.dart';

enum Priority { critical, visible, background }

class Task {
  final int id;
  final Priority priority;
  final int costMs;
  final bool chunkable;
  final String? imagePath;
  void Function()? onComplete;

  /// Các mốc thời gian (µs, tuyệt đối theo Timeline.now). 0 = chưa xảy ra.
  int submitUs = 0;
  int startUs = 0;
  int _endUs = 0;

  int get endUs => _endUs;
  set endUs(int val) {
    _endUs = val;
    if (val != 0) {
      onComplete?.call();
    }
  }

  Task({
    required this.id,
    required this.priority,
    required this.costMs,
    this.chunkable = false,
    this.imagePath,
    this.onComplete,
  });

  /// Tiến độ theo vòng lặp (dùng cho chunking).
  int doneIters = 0;
  int inFlight = 0; // số vòng lặp của chunk đang chạy
  bool dropped = false; // Bị backpressure / load shedding loại bỏ

  int get iters => costMs * Burner.effectiveItersPerMs;
  int get remainingIters => iters - doneIters;
  bool get done => _endUs != 0 && !dropped;
}
