import 'package:flutter/material.dart';

import '../run_controller.dart';

class DemoControlDock extends StatelessWidget {
  const DemoControlDock({super.key, required this.controller});
  final RunController controller;

  Color _policyColor(String p) {
    switch (p.toLowerCase()) {
      case 'p0':
        return const Color(0xFFEF4444); // Đỏ
      case 'p1':
        return const Color(0xFF38BDF8); // Xanh dương
      case 'p2':
        return const Color(0xFFA855F7); // Tím
      case 'p3':
        return const Color(0xFF10B981); // Xanh lục
      case 'p4':
        return const Color(0xFFF59E0B); // Vàng cam
      default:
        return const Color(0xFF94A3B8);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      bottom: 8,
      left: 6,
      right: 6,
      child: Material(
        color: Colors.transparent,
        child: Container(
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color(0xF20F172A), Color(0xFA0B0F19)],
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF38BDF8).withValues(alpha: 0.5), width: 1.2),
            boxShadow: const [
              BoxShadow(color: Color(0xCC000000), blurRadius: 16, offset: Offset(0, 6)),
            ],
          ),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Hàng 1: Nút bấm chọn nhanh 5 Chính sách P0 -> P4
              ValueListenableBuilder<String>(
                valueListenable: controller.currentPolicy,
                builder: (_, currentPol, _) {
                  const policies = ['p0', 'p1', 'p2', 'p3', 'p4'];
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      for (final p in policies)
                        _buildPolicyButton(
                          p: p,
                          isSelected: currentPol.toLowerCase() == p,
                          color: _policyColor(p),
                          onTap: () => controller.switchPolicy(p),
                        ),
                    ],
                  );
                },
              ),

              const SizedBox(height: 7),

              // Hàng 2: Công tắc Tải nền, Ép giật UI và Bão nhiệt
              Row(
                children: [
                  Expanded(
                    child: ValueListenableBuilder<bool>(
                      valueListenable: controller.continuousLoad,
                      builder: (_, on, _) => ElevatedButton(
                        onPressed: controller.toggleContinuousLoad,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: on ? const Color(0xFF0284C7) : const Color(0xFF1E293B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 7, horizontal: 2),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: BorderSide(color: on ? Colors.cyanAccent : const Color(0xFF334155), width: on ? 1.4 : 1.0),
                          ),
                        ),
                        child: FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(on ? Icons.sync_rounded : Icons.bolt_rounded, size: 14, color: on ? Colors.white : Colors.amberAccent),
                              const SizedBox(width: 3),
                              Text(on ? 'Tải: BẬT' : '⚡ Tải nền', style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: ValueListenableBuilder<bool>(
                      valueListenable: controller.uiStress,
                      builder: (_, lag, _) => ElevatedButton(
                        onPressed: controller.toggleUiStress,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: lag ? const Color(0xFF9333EA) : const Color(0xFF1E293B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 7, horizontal: 2),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: BorderSide(color: lag ? Colors.purpleAccent : const Color(0xFF334155), width: lag ? 1.4 : 1.0),
                          ),
                        ),
                        child: FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.speed_rounded, size: 14, color: lag ? Colors.white : Colors.purpleAccent),
                              const SizedBox(width: 3),
                              Text(lag ? 'Giật: BẬT' : '💥 Ép giật', style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: ValueListenableBuilder<bool>(
                      valueListenable: controller.thermalOverload,
                      builder: (_, hot, _) => ElevatedButton(
                        onPressed: controller.toggleThermalOverload,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: hot ? const Color(0xFFDC2626) : const Color(0xFF1E293B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 7, horizontal: 2),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                            side: BorderSide(color: hot ? Colors.orangeAccent : const Color(0xFF475569), width: hot ? 1.4 : 1.0),
                          ),
                        ),
                        child: FittedBox(
                          fit: BoxFit.scaleDown,
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.local_fire_department_rounded, size: 14, color: hot ? Colors.white : Colors.deepOrangeAccent),
                              const SizedBox(width: 3),
                              Text(hot ? 'Nhiệt: BẬT' : '🔥 Bão nhiệt', style: const TextStyle(fontSize: 10.5, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  IconButton(
                    onPressed: () => controller.clearQueue(),
                    icon: const Icon(Icons.cleaning_services_rounded, size: 16, color: Colors.white70),
                    tooltip: 'Dừng tải & Xóa hàng đợi',
                    style: IconButton.styleFrom(
                      backgroundColor: const Color(0xFF1E293B),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      padding: const EdgeInsets.all(7),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 4),

              // Hàng 3: chạy kịch bản demo 60 s và bảng so sánh
              Row(
                children: [
                  Expanded(
                    flex: 5,
                    child: ValueListenableBuilder<bool>(
                      valueListenable: controller.demoRunning,
                      builder: (_, running, _) => FilledButton.icon(
                        onPressed: running ? controller.stopDemo : controller.runDemo,
                        icon: Icon(running ? Icons.stop_rounded : Icons.play_arrow_rounded, size: 18),
                        label: Text(running ? 'DỪNG DEMO' : 'CHẠY DEMO 60s',
                            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w900)),
                        style: FilledButton.styleFrom(
                          backgroundColor: running ? const Color(0xFFEF4444) : const Color(0xFF10B981),
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    flex: 3,
                    child: OutlinedButton.icon(
                      onPressed: () => controller.showScoreboard.value = true,
                      icon: const Icon(Icons.table_chart_rounded, size: 16),
                      label: const Text('So sánh', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.white,
                        side: const BorderSide(color: Color(0xFF38BDF8)),
                        padding: const EdgeInsets.symmetric(vertical: 8),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPolicyButton({
    required String p,
    required bool isSelected,
    required Color color,
    required VoidCallback onTap,
  }) {
    final label = p.toUpperCase();
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 2),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(vertical: 6),
            decoration: BoxDecoration(
              color: isSelected ? color : const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: isSelected ? Colors.white : const Color(0xFF334155),
                width: isSelected ? 1.5 : 0.8,
              ),
              boxShadow: isSelected
                  ? [
                      BoxShadow(
                        color: color.withValues(alpha: 0.5),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      )
                    ]
                  : null,
            ),
            child: Center(
              child: Text(
                label,
                style: TextStyle(
                  color: isSelected ? Colors.white : Colors.white70,
                  fontSize: 12,
                  fontWeight: isSelected ? FontWeight.w900 : FontWeight.bold,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
