import 'dart:isolate';

/// Tác vụ synthetic dựa trên khối lượng công việc cố định (số vòng lặp),
/// nên khi tranh chấp CPU thì thời gian thực tế dài ra (đúng hiện tượng cần đo).
double burn(int iters) {
  double x = 1.0;
  for (int i = 0; i < iters; i++) {
    x = x * 1.0000001 + (i & 7) * 1e-9;
  }
  return x;
}

/// Hàm top-level để closure của Isolate.run không bắt nhầm `this`.
Future<double> burnInIsolate(int iters) => Isolate.run(() => burn(iters));

class Burner {
  /// Quy ước CỐ ĐỊNH: 1 "ms" công việc = 100k vòng lặp (≈ 1 ms trên main isolate của A04e).
  /// Không hiệu chuẩn lại mỗi lần chạy vì tốc độ phụ thuộc nhiệt/xung nhịp -> làm tải không lặp lại được.
  static const int itersPerMs = 100000;

  /// Tốc độ đo được lúc khởi động trên main isolate (chỉ để ghi vào meta).
  static int measuredItersPerMs = 0;

  static void calibrate() {
    const n = 3000000;
    int best = 1 << 62;
    double sink = 0;
    for (int k = 0; k < 3; k++) {
      final sw = Stopwatch()..start();
      sink += burn(n);
      final us = sw.elapsedMicroseconds;
      if (us < best) best = us;
    }
    if (sink.isNaN) throw StateError('unreachable');
    measuredItersPerMs = (n * 1000 / best).round();
  }
}
