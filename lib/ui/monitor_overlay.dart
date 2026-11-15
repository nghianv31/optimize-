import 'dart:math';
import 'package:flutter/material.dart';

class MonitorSnapshot {
  final String policy;
  final String scenario;
  final int elapsedS;
  final int totalS;
  final double currentFps;
  final double currentFrameMs;
  final double p95Ms;
  final double buildP95Ms;
  final double rasterP95Ms;
  final int totalFrames;
  final double missedPct;
  final List<double> recentFrameDurations; // last 40 frames in ms
  final int activeWorkers;
  final int maxWorkers;
  final int configuredWorkers;
  final String modeName;
  final int pendingTasks;
  final int doneTasks;
  final int droppedTasks;
  final double critLatencyMs;

  const MonitorSnapshot({
    required this.policy,
    required this.scenario,
    required this.elapsedS,
    required this.totalS,
    required this.currentFps,
    required this.currentFrameMs,
    required this.p95Ms,
    required this.buildP95Ms,
    required this.rasterP95Ms,
    required this.totalFrames,
    required this.missedPct,
    required this.recentFrameDurations,
    required this.activeWorkers,
    required this.maxWorkers,
    required this.configuredWorkers,
    required this.modeName,
    required this.pendingTasks,
    required this.doneTasks,
    required this.droppedTasks,
    required this.critLatencyMs,
  });
}

class MonitorOverlay extends StatefulWidget {
  const MonitorOverlay({super.key, required this.snapshotNotifier});
  final ValueNotifier<MonitorSnapshot?> snapshotNotifier;

  @override
  State<MonitorOverlay> createState() => _MonitorOverlayState();
}

class _MonitorOverlayState extends State<MonitorOverlay> {
  bool _expanded = true;

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<MonitorSnapshot?>(
      valueListenable: widget.snapshotNotifier,
      builder: (_, snap, _) {
        if (snap == null) return const SizedBox.shrink();

        final policyColor = _policyColor(snap.policy);
        final modeColor = _modeColor(snap.modeName);
        final progress = snap.totalS > 0 ? (snap.elapsedS / snap.totalS).clamp(0.0, 1.0) : 0.0;

        return Positioned(
          top: 6,
          left: 8,
          right: 8,
          child: Material(
            color: Colors.transparent,
            child: Container(
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xF20B1120), Color(0xEC111827)],
                ),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.75), width: 1.2),
                boxShadow: const [
                  BoxShadow(color: Color(0x99000000), blurRadius: 14, offset: Offset(0, 6)),
                ],
              ),
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 8),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // --- Header Trực Quan ---
                  Row(
                    children: [
                      Flexible(
                        child: _policyBadge(_policyLabel(snap.policy), policyColor),
                      ),
                      const SizedBox(width: 6),
                      _modeBadge(snap.modeName, modeColor),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          '${snap.elapsedS}/${snap.totalS}s',
                          style: const TextStyle(
                            color: Colors.white70,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                      const SizedBox(width: 4),
                      InkWell(
                        onTap: () => setState(() => _expanded = !_expanded),
                        borderRadius: BorderRadius.circular(12),
                        child: Padding(
                          padding: const EdgeInsets.all(2),
                          child: Icon(
                            _expanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                            color: Colors.white70,
                            size: 18,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 5),

                  // Thanh tiến trình mỏng
                  ClipRRect(
                    borderRadius: BorderRadius.circular(2),
                    child: LinearProgressIndicator(
                      value: progress,
                      minHeight: 2.5,
                      backgroundColor: const Color(0xFF1E293B),
                      valueColor: AlwaysStoppedAnimation<Color>(policyColor),
                    ),
                  ),

                  if (_expanded) ...[
                    const SizedBox(height: 7),

                    // --- Thanh Trực Quan Hóa Worker Pool (CPU Worker Slots) ---
                    _buildWorkerSlotsBar(snap),

                    const SizedBox(height: 7),

                    // --- 4 Thẻ Chỉ Số Lớn (KPI Cards) ---
                    Row(
                      children: [
                        Expanded(
                          child: _kpiCard(
                            label: 'FPS',
                            value: snap.currentFps.toStringAsFixed(0),
                            subtitle: 'Miss: ${snap.missedPct.toStringAsFixed(1)}%',
                            valueColor: snap.currentFps >= 45
                                ? const Color(0xFF10B981)
                                : (snap.currentFps >= 25 ? const Color(0xFFFBBF24) : const Color(0xFFEF4444)),
                          ),
                        ),
                        const SizedBox(width: 5),
                        Expanded(
                          child: _kpiCard(
                            label: 'FRAME TIME',
                            value: snap.currentFrameMs >= 100
                                ? '${snap.currentFrameMs.toStringAsFixed(0)}ms'
                                : '${snap.currentFrameMs.toStringAsFixed(1)}ms',
                            subtitle: 'p95: ${snap.p95Ms.toStringAsFixed(1)}ms',
                            valueColor: snap.currentFrameMs <= 16.7
                                ? const Color(0xFF10B981)
                                : (snap.currentFrameMs <= 33.3 ? const Color(0xFFFBBF24) : const Color(0xFFEF4444)),
                          ),
                        ),
                        const SizedBox(width: 5),
                        Expanded(
                          child: _kpiCard(
                            label: 'CRIT P95',
                            value: snap.critLatencyMs >= 1000
                                ? '${(snap.critLatencyMs / 1000).toStringAsFixed(1)}s'
                                : '${snap.critLatencyMs.toStringAsFixed(0)}ms',
                            subtitle: 'Mục tiêu <100ms',
                            valueColor: snap.critLatencyMs <= 100
                                ? const Color(0xFF10B981)
                                : (snap.critLatencyMs <= 500 ? const Color(0xFFFBBF24) : const Color(0xFFEF4444)),
                          ),
                        ),
                        const SizedBox(width: 5),
                        Expanded(
                          child: _kpiCard(
                            label: 'UI BUILD P95',
                            value: snap.buildP95Ms >= 100
                                ? '${snap.buildP95Ms.toStringAsFixed(0)}ms'
                                : '${snap.buildP95Ms.toStringAsFixed(1)}ms',
                            subtitle: 'Raster: ${snap.rasterP95Ms.toStringAsFixed(0)}ms',
                            valueColor: snap.buildP95Ms <= 16.7
                                ? const Color(0xFF38BDF8)
                                : (snap.buildP95Ms <= 33.3 ? const Color(0xFFFBBF24) : const Color(0xFFEF4444)),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 7),

                    // --- Chú thích Sparkline ---
                    Row(
                      children: [
                        Text(
                          '40 frame gần nhất (${snap.totalFrames}f)',
                          style: const TextStyle(color: Colors.white54, fontSize: 8.5, fontWeight: FontWeight.w500),
                        ),
                        const Spacer(),
                        _legendDot(const Color(0xFF10B981), '≤16.7ms Mượt'),
                        const SizedBox(width: 6),
                        _legendDot(const Color(0xFFFBBF24), '≤33ms Trễ'),
                        const SizedBox(width: 6),
                        _legendDot(const Color(0xFFEF4444), '>33ms Giật/Đơ'),
                      ],
                    ),

                    const SizedBox(height: 4),

                    // --- Biểu Đồ Sparkline Nâng Cấp ---
                    SizedBox(
                      height: 64,
                      child: CustomPaint(
                        painter: FrameChartPainter(snap.recentFrameDurations),
                        child: const SizedBox.expand(),
                      ),
                    ),

                    const SizedBox(height: 7),

                    // --- Thanh Hàng Đợi 3 Pill ở Đáy ---
                    Row(
                      children: [
                        Expanded(
                          child: _queuePill(
                            '⏳ Queue: ${snap.pendingTasks}',
                            color: snap.pendingTasks > 200 ? const Color(0xFFFBBF24) : Colors.white70,
                            borderColor: snap.pendingTasks > 200
                                ? const Color(0xFFFBBF24).withValues(alpha: 0.5)
                                : Colors.white12,
                          ),
                        ),
                        const SizedBox(width: 5),
                        Expanded(
                          child: _queuePill(
                            '✅ Done: ${snap.doneTasks}',
                            color: const Color(0xFF34D399),
                            borderColor: const Color(0xFF10B981).withValues(alpha: 0.35),
                          ),
                        ),
                        const SizedBox(width: 5),
                        Expanded(
                          child: _queuePill(
                            '🛡️ Drop: ${snap.droppedTasks}',
                            color: snap.droppedTasks > 0 ? const Color(0xFFFBBF24) : Colors.white54,
                            borderColor: snap.droppedTasks > 0
                                ? const Color(0xFFEF4444).withValues(alpha: 0.7)
                                : Colors.white12,
                            fillColor: snap.droppedTasks > 0 ? const Color(0x33EF4444) : const Color(0xFF1E293B),
                            bold: snap.droppedTasks > 0,
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildWorkerSlotsBar(MonitorSnapshot snap) {
    final totalSlots = max(1, snap.configuredWorkers);
    final isMainOnly = snap.policy.toLowerCase() == 'p0';
    final isBaseline = snap.policy.toLowerCase() == 'none';
    final displaySlots = isBaseline ? 0 : (isMainOnly ? 1 : min(totalSlots, 8));
    final throttledCount = max(0, totalSlots - snap.maxWorkers);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0x991E293B),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white12),
      ),
      child: Row(
        children: [
          Text(
            isMainOnly ? 'MAIN THREAD' : 'WORKER POOL',
            style: const TextStyle(
              color: Colors.white60,
              fontSize: 9,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.4,
            ),
          ),
          const SizedBox(width: 8),
          if (displaySlots == 0)
            const Text('No background workers', style: TextStyle(color: Colors.white38, fontSize: 9))
          else
            Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(displaySlots, (i) {
                final bool isLocked = !isMainOnly && i >= snap.maxWorkers;
                final bool isActive = !isLocked && i < snap.activeWorkers;

                Color fill;
                Color border;
                Widget? inner;
                if (isLocked) {
                  fill = const Color(0x33EF4444);
                  border = const Color(0xFFF59E0B);
                  inner = const Icon(Icons.lock_rounded, size: 9, color: Color(0xFFFBBF24));
                } else if (isActive) {
                  fill = isMainOnly ? const Color(0xFFEF4444) : const Color(0xFF06B6D4);
                  border = isMainOnly ? const Color(0xFFFCA5A5) : const Color(0xFF67E8F9);
                  inner = const Icon(Icons.bolt_rounded, size: 10, color: Colors.white);
                } else {
                  fill = const Color(0xFF0F172A);
                  border = const Color(0xFF475569);
                  inner = null;
                }

                return Container(
                  width: 17,
                  height: 15,
                  margin: const EdgeInsets.only(right: 4),
                  decoration: BoxDecoration(
                    color: fill,
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: border, width: 1.1),
                    boxShadow: isActive
                        ? [BoxShadow(color: border.withValues(alpha: 0.45), blurRadius: 4)]
                        : null,
                  ),
                  child: inner != null ? Center(child: inner) : null,
                );
              }),
            ),
          const Spacer(),
          Flexible(
            child: FittedBox(
              fit: BoxFit.scaleDown,
              alignment: Alignment.centerRight,
              child: Text(
                isBaseline
                    ? 'UI Only'
                    : isMainOnly
                        ? '1/1 (Chặn Main)'
                        : throttledCount > 0
                            ? '${snap.activeWorkers}/${snap.maxWorkers} (AIMD khóa $throttledCount)'
                            : '${snap.activeWorkers}/${snap.maxWorkers} sẵn sàng',
                style: TextStyle(
                  color: throttledCount > 0 && !isMainOnly
                      ? const Color(0xFFFBBF24)
                      : (isMainOnly ? const Color(0xFFF87171) : const Color(0xFF38BDF8)),
                  fontSize: 9.5,
                  fontWeight: FontWeight.bold,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _policyBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color, width: 1.1),
      ),
      child: FittedBox(
        fit: BoxFit.scaleDown,
        child: Text(
          text,
          style: TextStyle(
            color: color,
            fontSize: 9.5,
            fontWeight: FontWeight.w800,
            letterSpacing: 0.3,
          ),
        ),
      ),
    );
  }

  Widget _modeBadge(String mode, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withValues(alpha: 0.8), width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 4),
          Text(
            mode,
            style: TextStyle(
              color: color,
              fontSize: 9,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _kpiCard({
    required String label,
    required String value,
    required String subtitle,
    required Color valueColor,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 5),
      decoration: BoxDecoration(
        color: const Color(0x881E293B),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.white54,
                fontSize: 7.5,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.3,
              ),
            ),
          ),
          const SizedBox(height: 1),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              value,
              style: TextStyle(
                color: valueColor,
                fontSize: 13.5,
                fontWeight: FontWeight.w800,
                fontFamily: 'monospace',
              ),
            ),
          ),
          const SizedBox(height: 1),
          FittedBox(
            fit: BoxFit.scaleDown,
            alignment: Alignment.centerLeft,
            child: Text(
              subtitle,
              style: const TextStyle(color: Colors.white60, fontSize: 8),
            ),
          ),
        ],
      ),
    );
  }

  Widget _legendDot(Color color, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 6,
          height: 6,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 3),
        Text(
          label,
          style: const TextStyle(color: Colors.white60, fontSize: 8),
        ),
      ],
    );
  }

  Widget _queuePill(
    String text, {
    required Color color,
    required Color borderColor,
    Color fillColor = const Color(0x991E293B),
    bool bold = false,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
      decoration: BoxDecoration(
        color: fillColor,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: borderColor),
      ),
      child: FittedBox(
        fit: BoxFit.scaleDown,
        child: Text(
          text,
          style: TextStyle(
            color: color,
            fontSize: 9.5,
            fontWeight: bold ? FontWeight.w800 : FontWeight.w600,
            fontFamily: 'monospace',
          ),
        ),
      ),
    );
  }

  String _policyLabel(String p) {
    switch (p.toLowerCase()) {
      case 'none':
        return 'NONE · UI BASELINE';
      case 'p0':
        return 'P0 · MAIN ISOLATE';
      case 'naive':
        return 'NAIVE · UNBOUNDED';
      case 'p1':
        return 'P1 · FIXED POOL';
      case 'p2':
        return 'P2 · PRIORITY+AGING';
      case 'p3c':
        return 'P3c · CHUNKING';
      case 'p3r':
        return 'P3r · CHUNK+RESERVE';
      case 'p3':
        return 'P3 · CHUNK+YIELD';
      case 'p4':
        return 'P4 · ADAPTIVE AIMD';
      case 'p4_aimd':
        return 'P4 · AIMD ONLY';
      default:
        return p.toUpperCase();
    }
  }

  Color _policyColor(String p) {
    switch (p.toLowerCase()) {
      case 'none':
        return Colors.blueGrey.shade300;
      case 'p0':
      case 'naive':
        return const Color(0xFFEF4444);
      case 'p1':
        return const Color(0xFFF97316);
      case 'p2':
        return const Color(0xFFEAB308);
      case 'p3':
      case 'p3c':
      case 'p3r':
        return const Color(0xFF38BDF8);
      case 'p4':
      case 'p4_aimd':
        return const Color(0xFF10B981);
      default:
        return Colors.cyan;
    }
  }

  Color _modeColor(String m) {
    switch (m.toUpperCase()) {
      case 'CRITICAL':
      case 'MAIN_ISOLATE':
      case 'NAIVE':
        return const Color(0xFFEF4444);
      case 'CONSERVE':
      case 'YIELDING':
        return const Color(0xFFFBBF24);
      default:
        return const Color(0xFF10B981);
    }
  }
}

class FrameChartPainter extends CustomPainter {
  final List<double> frameDurationsMs;

  FrameChartPainter(this.frameDurationsMs);

  /// Thang đo phi tuyến hai đoạn:
  /// - [0, 33.33ms] chiếm 70% chiều cao dưới (nên vạch 16.67ms nằm đúng 35% chiều cao).
  /// - (33.33ms, 300ms] nén trong 30% chiều cao trên để phân biệt được spike 80ms vs 250ms.
  double _mapHeight(double durMs, double h) {
    if (durMs <= 0) return 2.0;
    if (durMs <= 33.33) {
      return (durMs / 33.33 * 0.70 * h).clamp(2.0, h);
    }
    final upper = ((durMs - 33.33) / (300.0 - 33.33)).clamp(0.0, 1.0);
    return (0.70 * h + upper * 0.30 * h).clamp(2.0, h);
  }

  @override
  void paint(Canvas canvas, Size size) {
    // Nền biểu đồ
    final bgPaint = Paint()..color = const Color(0x660F172A);
    final bgRect = RRect.fromRectAndRadius(Offset.zero & size, const Radius.circular(8));
    canvas.drawRRect(bgRect, bgPaint);

    final borderPaint = Paint()
      ..color = Colors.white12
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;
    canvas.drawRRect(bgRect, borderPaint);

    // Lưới ngang mờ tại 33.3ms (70%) và 150ms (~83%)
    final gridPaint = Paint()
      ..color = Colors.white10
      ..strokeWidth = 0.8;
    for (final ms in [33.33, 150.0]) {
      final y = size.height - _mapHeight(ms, size.height);
      canvas.drawLine(Offset(2, y), Offset(size.width - 2, y), gridPaint);
    }

    // Vẽ các cột dữ liệu frame
    if (frameDurationsMs.isNotEmpty) {
      const slotCount = 40;
      const gap = 1.8;
      final usableW = size.width - 6;
      final barWidth = max(2.0, (usableW - (slotCount - 1) * gap) / slotCount);
      final startOffset = (slotCount - frameDurationsMs.length).clamp(0, slotCount);

      for (int i = 0; i < frameDurationsMs.length; i++) {
        final dur = frameDurationsMs[i];
        final barHeight = _mapHeight(dur, size.height - 4);
        final x = 3.0 + (startOffset + i) * (barWidth + gap);
        final y = size.height - 2 - barHeight;

        final Color color;
        if (dur <= 16.7) {
          color = const Color(0xFF10B981); // Xanh ngọc lục bảo: Mượt
        } else if (dur <= 33.3) {
          color = const Color(0xFFFBBF24); // Vàng: Trễ 1 nhịp
        } else {
          color = const Color(0xFFEF4444); // Đỏ: Giật/Đơ
        }

        final barPaint = Paint()..color = color;
        canvas.drawRRect(
          RRect.fromRectAndRadius(Rect.fromLTWH(x, y, barWidth, barHeight), const Radius.circular(2)),
          barPaint,
        );
      }
    }

    // Vẽ đường đứt nét Ngân sách 16.7ms (60FPS) ĐÈ LÊN TRÊN các cột
    final budgetY = size.height - 2 - _mapHeight(16.67, size.height - 4);
    final dashPaint = Paint()
      ..color = const Color(0xFFFB7185)
      ..strokeWidth = 1.4;
    const dashW = 5.0;
    const dashSpace = 3.5;
    double cx = 2.0;
    while (cx < size.width - 2) {
      final endX = min(cx + dashW, size.width - 2);
      canvas.drawLine(Offset(cx, budgetY), Offset(endX, budgetY), dashPaint);
      cx += dashW + dashSpace;
    }

    // Nhãn "16.7ms (60FPS)" bên phải vạch ngân sách
    final tp = TextPainter(
      text: const TextSpan(
        text: '16.7ms (60FPS)',
        style: TextStyle(
          color: Color(0xFFFFE4E6),
          fontSize: 7.5,
          fontWeight: FontWeight.w800,
          fontFamily: 'monospace',
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();

    final tagW = tp.width + 6;
    final tagH = tp.height + 2;
    final tagRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(size.width - tagW - 4, (budgetY - tagH - 1).clamp(2.0, size.height - tagH - 2), tagW, tagH),
      const Radius.circular(4),
    );
    canvas.drawRRect(tagRect, Paint()..color = const Color(0xCC9F1239));
    tp.paint(canvas, Offset(tagRect.left + 3, tagRect.top + 1));
  }

  @override
  bool shouldRepaint(covariant FrameChartPainter oldDelegate) => true;
}
