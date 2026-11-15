import 'dart:math';

/// Bộ điều khiển AIMD (Additive Increase, Multiplicative Decrease)
/// tự động co giãn số lượng worker theo phản hồi thời gian thực của frame UI.
class AimdController {
  AimdController({
    required this.minWorkers,
    required this.maxWorkers,
    required this.targetGapMs,
    this.pacingMs = 500, // Đánh giá mỗi epoch 500ms để tránh co giảm quá dồn dập
    double initialWorkers = 2.0,
  })  : _workers = initialWorkers.clamp(minWorkers.toDouble(), maxWorkers.toDouble());

  final int minWorkers;
  final int maxWorkers;
  final double targetGapMs;
  final int pacingMs;

  double _workers;
  int _lastUpdateUs = 0;

  /// Số worker nguyên hiện hành được phép cấp phát tác vụ thông thường.
  int get workerCount => _workers.round().clamp(minWorkers, maxWorkers);

  /// Lịch sử số worker qua các chu kỳ (để thống kê / vẽ biểu đồ).
  final List<int> history = [];

  /// Cập nhật số worker dựa trên p95 khoảng cách frame gần nhất:
  /// - Nếu chưa hết chu kỳ epoch [pacingMs]: giữ nguyên.
  /// - Nếu gap > targetGapMs: Multiplicative Decrease (* 0.5)
  /// - Nếu gap <= targetGapMs * 0.8: Additive Increase (+ 1.0)
  int update(double gapP95Ms, [int? nowUs]) {
    final now = nowUs ?? DateTime.now().microsecondsSinceEpoch;
    if (_lastUpdateUs != 0 && (now - _lastUpdateUs) < pacingMs * 1000) {
      return workerCount;
    }
    _lastUpdateUs = now;

    if (gapP95Ms > targetGapMs) {
      // Giảm nhân để nhanh chóng hạ tải CPU, cứu UI
      _workers = max(minWorkers.toDouble(), _workers * 0.5);
    } else if (gapP95Ms <= targetGapMs * 0.8) {
      // Tăng cộng đều đặn từng worker khi UI mượt
      _workers = min(maxWorkers.toDouble(), _workers + 1.0);
    }
    final c = workerCount;
    history.add(c);
    return c;
  }
}
