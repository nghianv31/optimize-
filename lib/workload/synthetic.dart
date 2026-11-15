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
  /// Quy ước chuẩn: 1 "ms" công việc = 100k vòng lặp (≈ 1 ms trên main isolate của A04e).
  static const int itersPerMs = 100000;

  /// Tốc độ đo được lúc khởi động trên main isolate (chỉ để ghi vào meta).
  static int measuredItersPerMs = 0;

  /// Số vòng lặp thực tế tương ứng với 1ms trên thiết bị hiện hành.
  /// Nếu máy mạnh hơn A04e (vd PC emulator, chip cao cấp), tự nâng số vòng lặp
  /// để tải 300ms thực sự đốt CPU đủ 300ms, giúp P0 khựng rõ ràng.
  static int get effectiveItersPerMs =>
      measuredItersPerMs > 0 ? measuredItersPerMs : itersPerMs;

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
