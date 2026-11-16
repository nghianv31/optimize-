import 'package:flutter/material.dart';

import '../run_controller.dart';
import '../scheduler/thermal_sim.dart';
import '../workload/demo_scenario.dart';

const _policyOrder = ['p0', 'p1', 'p2', 'p3', 'p4'];

String policyShort(String p) {
  switch (p.toLowerCase()) {
    case 'p0':
      return 'P0 · Main isolate';
    case 'p1':
      return 'P1 · Pool cố định';
    case 'p2':
      return 'P2 · Ưu tiên + aging';
    case 'p3':
      return 'P3 · Chunk + nhường frame';
    case 'p4':
      return 'P4 · Thích ứng (AIMD)';
    default:
      return p.toUpperCase();
  }
}

Color _good(bool ok, bool warn) => ok ? const Color(0xFF10B981) : (warn ? const Color(0xFFFBBF24) : const Color(0xFFEF4444));

/// Dải thông tin trên cùng cho demo: pha hiện tại + điều cần xem, quả bóng dò giật,
/// các chỉ số "dấu hiệu" của từng chính sách.
class DemoBanner extends StatelessWidget {
  const DemoBanner({super.key, required this.controller});
  final RunController controller;

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: Material(
        color: const Color(0xF2080C16),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(10, 6, 10, 6),
          child: AnimatedBuilder(
            animation: Listenable.merge([
              controller.demoCaption,
              controller.demoRemainS,
              controller.monitor,
              controller.lastCritMs,
              controller.thermalView,
              controller.currentPolicy,
            ]),
            builder: (_, _) {
              final ph = controller.demoCaption.value;
              final snap = controller.monitor.value;
              final crit = controller.lastCritMs.value;
              final temp = controller.thermalView.value;
              final pol = controller.currentPolicy.value;
              return Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          ph == null ? 'Chọn chính sách rồi bấm ▶ CHẠY DEMO' : ph.title,
                          style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w900),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (ph != null)
                        Text('còn ${controller.demoRemainS.value}s',
                            style: const TextStyle(color: Colors.white54, fontSize: 11, fontFamily: 'monospace')),
                      const SizedBox(width: 8),
                      Text(policyShort(pol),
                          style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 11, fontWeight: FontWeight.w800)),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    ph?.hint ?? 'Cùng một kịch bản 60 s, đổi chính sách và so sánh các chỉ số bên dưới.',
                    style: const TextStyle(color: Colors.white70, fontSize: 10.5),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  JankTrack(),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      _chip('FPS', snap == null ? '--' : snap.currentFps.toStringAsFixed(0),
                          snap == null ? Colors.white54 : _good(snap.currentFps >= 50, snap.currentFps >= 30)),
                      _chip('BẤM ẢNH', crit == null ? '--' : _ms(crit),
                          crit == null ? Colors.white54 : _good(crit <= 100, crit <= 1000)),
                      _chip('HÀNG ĐỢI', snap == null ? '--' : '${snap.pendingTasks}',
                          snap == null ? Colors.white54 : _good(snap.pendingTasks < 100, snap.pendingTasks < 400)),
                      _chip('BỎ', snap == null ? '--' : '${snap.droppedTasks}',
                          (snap?.droppedTasks ?? 0) > 0 ? const Color(0xFFFBBF24) : Colors.white54),
                      _chip('WORKER', snap == null ? '--' : '${snap.activeWorkers}/${snap.maxWorkers}', const Color(0xFF38BDF8)),
                      if (temp != null)
                        _chip('NHIỆT (SIM)', '${temp.toStringAsFixed(1)}°',
                            _good(temp < ThermalSim.conserveAt, temp < ThermalSim.throttleAt)),
                    ],
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  static String _ms(double v) => v >= 1000 ? '${(v / 1000).toStringAsFixed(1)}s' : '${v.toStringAsFixed(0)}ms';

  Widget _chip(String label, String value, Color color) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.only(right: 4),
        padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 3),
        decoration: BoxDecoration(
          color: const Color(0x881E293B),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: color.withValues(alpha: 0.6)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(label, style: const TextStyle(color: Colors.white54, fontSize: 7.5, fontWeight: FontWeight.w700)),
            ),
            FittedBox(
              fit: BoxFit.scaleDown,
              child: Text(value,
                  style: TextStyle(color: color, fontSize: 13, fontWeight: FontWeight.w900, fontFamily: 'monospace')),
            ),
          ],
        ),
      ),
    );
  }
}

/// Quả bóng chạy đều trên một đường ray, có vệt mờ phía sau.
/// Frame bị bỏ => các chấm của vệt cách xa nhau / bóng nhảy cóc: giật nhìn thấy ngay.
/// Khi mô hình nhiệt đang "hạ xung", build() bị phạt thêm vài ms (mô phỏng CPU chậm).
class JankTrack extends StatefulWidget {
  const JankTrack({super.key});

  @override
  State<JankTrack> createState() => _JankTrackState();
}

class _JankTrackState extends State<JankTrack> with SingleTickerProviderStateMixin {
  late final AnimationController _c = AnimationController(vsync: this, duration: const Duration(milliseconds: 1600))..repeat();
  final _trail = <double>[];

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  void _penalty() {
    final p = ThermalSim.penaltyMs;
    if (p <= 0) return;
    final sw = Stopwatch()..start();
    while (sw.elapsedMicroseconds < p * 1000) {}
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _c,
      builder: (_, _) {
        _penalty();
        _trail.add(_c.value);
        if (_trail.length > 9) _trail.removeAt(0);
        return SizedBox(
          height: 24,
          child: CustomPaint(painter: _TrailPainter(List.of(_trail)), size: Size.infinite),
        );
      },
    );
  }
}

class _TrailPainter extends CustomPainter {
  _TrailPainter(this.trail);
  final List<double> trail;

  @override
  void paint(Canvas canvas, Size size) {
    final y = size.height / 2;
    canvas.drawLine(
        Offset(4, y), Offset(size.width - 4, y), Paint()..color = Colors.white12..strokeWidth = 2);
    for (int i = 0; i < trail.length; i++) {
      final isLast = i == trail.length - 1;
      final x = 8 + trail[i] * (size.width - 16);
      final a = (i + 1) / trail.length;
      canvas.drawCircle(
        Offset(x, y),
        isLast ? 7 : 3.5 + 2 * a,
        Paint()..color = (isLast ? const Color(0xFF22D3EE) : const Color(0xFF38BDF8)).withValues(alpha: isLast ? 1 : a * 0.55),
      );
    }
  }

  @override
  bool shouldRepaint(covariant _TrailPainter old) => true;
}

/// Bảng so sánh cộng dồn: mỗi lần chạy demo xong, thêm một hàng.
class DemoScoreboard extends StatelessWidget {
  const DemoScoreboard({super.key, required this.controller});
  final RunController controller;

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: controller.showScoreboard,
      builder: (_, show, _) {
        if (!show) return const SizedBox.shrink();
        return Positioned.fill(
          child: Container(
            color: const Color(0xE6050810),
            padding: const EdgeInsets.fromLTRB(10, 150, 10, 150),
            child: ValueListenableBuilder<Map<String, DemoResult>>(
              valueListenable: controller.demoResults,
              builder: (_, res, _) {
                final rows = [for (final p in _policyOrder) if (res.containsKey(p)) res[p]!];
                return Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F172A),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFF38BDF8)),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Text('SO SÁNH CÁC CHÍNH SÁCH (cùng kịch bản 60 s)',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 13)),
                      const SizedBox(height: 6),
                      _row(['Chính sách', 'Rớt\nframe', 'Bấm ảnh\np95', 'Xong', 'Bỏ', 'Nhiệt\nmax', 'Hạ xung'], header: true),
                      if (rows.isEmpty)
                        const Padding(
                          padding: EdgeInsets.all(12),
                          child: Text('Chưa có kết quả. Chạy demo cho từng chính sách.',
                              style: TextStyle(color: Colors.white54, fontSize: 11)),
                        ),
                      for (final r in rows)
                        _row([
                          policyShort(r.policy).split(' · ').first,
                          '${r.missedPct.toStringAsFixed(0)}%',
                          r.critP95Ms >= 1000 ? '${(r.critP95Ms / 1000).toStringAsFixed(1)}s' : '${r.critP95Ms.toStringAsFixed(0)}ms',
                          '${r.donePct.toStringAsFixed(0)}%',
                          '${r.dropped}',
                          r.peakTempC > 0 ? '${r.peakTempC.toStringAsFixed(1)}°' : '-',
                          '${r.throttledS.toStringAsFixed(0)}s',
                        ], colors: [
                          Colors.white,
                          _good(r.missedPct <= 5, r.missedPct <= 25),
                          _good(r.critP95Ms <= 100, r.critP95Ms <= 1000),
                          Colors.white,
                          r.dropped > 0 ? const Color(0xFFFBBF24) : Colors.white70,
                          _good(r.peakTempC < ThermalSim.throttleAt, false),
                          _good(r.throttledS == 0, r.throttledS < 4),
                        ]),
                      const SizedBox(height: 6),
                      const Text('Nhiệt độ là mô hình mô phỏng, không phải số đo thật.',
                          style: TextStyle(color: Colors.white38, fontSize: 9, fontStyle: FontStyle.italic)),
                      const SizedBox(height: 6),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton(
                              onPressed: () => controller.demoResults.value = {},
                              child: const Text('Xóa kết quả', style: TextStyle(fontSize: 11))),
                          FilledButton(
                              onPressed: () => controller.showScoreboard.value = false,
                              child: const Text('Đóng', style: TextStyle(fontSize: 11))),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        );
      },
    );
  }

  Widget _row(List<String> cells, {bool header = false, List<Color>? colors}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          for (int i = 0; i < cells.length; i++)
            Expanded(
              flex: i == 0 ? 2 : 3,
              child: Text(
                cells[i],
                textAlign: i == 0 ? TextAlign.left : TextAlign.center,
                style: TextStyle(
                  color: header ? Colors.white54 : (colors?[i] ?? Colors.white),
                  fontSize: header ? 9 : 12.5,
                  fontWeight: header ? FontWeight.w700 : FontWeight.w900,
                  fontFamily: header ? null : 'monospace',
                ),
              ),
            ),
        ],
      ),
    );
  }
}
