/// Các mức suy giảm (Degradation Modes) của hệ thống.
enum DegradeMode {
  /// Bình thường: hệ thống xử lý đầy đủ mọi tác vụ.
  normal,

  /// Tiết kiệm / Suy giảm nhẹ:
  /// Tạm hoãn hoặc chỉ chạy các tác vụ critical và visible,
  /// giảm trần worker để kiểm soát nhiệt và pin.
  conserve,

  /// Nguy cấp / Suy giảm nặng:
  /// Thiết bị quá nóng hoặc pin cực yếu; drop tác vụ nền (load shedding),
  /// chỉ phục vụ tác vụ critical và UI.
  critical,
}

/// Máy trạng thái quản lý việc chuyển đổi chế độ suy giảm,
/// có cơ chế trễ (hysteresis) từ 5-10 giây để chống hiện tượng
/// chập chờn / rung giật (flapping) khi tín hiệu dao động quanh ngưỡng.
class ModeMachine {
  ModeMachine({
    this.hysteresisMs = 5000,
    DegradeMode initialMode = DegradeMode.normal,
  })  : currentMode = initialMode,
        _candidateMode = initialMode;

  final int hysteresisMs;

  DegradeMode currentMode;
  DegradeMode _candidateMode;
  int _candidateStartUs = 0;

  /// Đếm số lần chuyển đổi chế độ thành công (để kiểm tra độ ổn định).
  int transitions = 0;

  /// Lịch sử chuyển đổi (timestampUs, mode).
  final List<Map<String, dynamic>> history = [];

  /// Cập nhật tín hiệu mục tiêu tại thời điểm [nowUs].
  /// Chỉ chính thức chuyển sang [targetMode] nếu tín hiệu này
  /// được duy trì liên tục trong suốt khoảng thời gian [hysteresisMs].
  DegradeMode update(DegradeMode targetMode, int nowUs) {
    if (targetMode == currentMode) {
      // Tín hiệu khớp trạng thái hiện tại, reset candidate
      _candidateMode = targetMode;
      _candidateStartUs = 0;
      return currentMode;
    }

    if (targetMode != _candidateMode) {
      // Xuất hiện mục tiêu chuyển đổi mới, bắt đầu tính giờ trễ
      _candidateMode = targetMode;
      _candidateStartUs = nowUs;
    } else {
      // Mục tiêu duy trì ổn định, kiểm tra đã đủ thời gian trễ chưa
      if (nowUs - _candidateStartUs >= hysteresisMs * 1000) {
        currentMode = _candidateMode;
        transitions++;
        history.add({
          'timeUs': nowUs,
          'mode': currentMode.name,
        });
      }
    }
    return currentMode;
  }
}
