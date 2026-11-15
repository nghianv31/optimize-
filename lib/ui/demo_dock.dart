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

              // Hàng 2: Các nút hành động kích hoạt tải
              Row(
                children: [
                  Expanded(
                    flex: 4,
                    child: ElevatedButton.icon(
                      onPressed: () => controller.injectBackgroundTasks(count: 30, costMs: 300),
                      icon: const Icon(Icons.bolt_rounded, size: 15, color: Colors.amberAccent),
                      label: const Text('Nạp 30 ảnh', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1E293B),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 7),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                          side: const BorderSide(color: Color(0xFF334155)),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 5),
                  Expanded(
                    flex: 4,
                    child: ElevatedButton.icon(
                      onPressed: () => controller.injectBurstTasks(count: 60, costMs: 400),
                      icon: const Icon(Icons.local_fire_department_rounded, size: 15, color: Colors.deepOrangeAccent),
                      label: const Text('Bão tải 60', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1E293B),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 7),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                          side: const BorderSide(color: Color(0xFF475569)),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 5),
                  IconButton(
                    onPressed: () => controller.clearQueue(),
                    icon: const Icon(Icons.cleaning_services_rounded, size: 16, color: Colors.white70),
                    tooltip: 'Xóa hàng đợi',
                    style: IconButton.styleFrom(
                      backgroundColor: const Color(0xFF1E293B),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      padding: const EdgeInsets.all(7),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 4),

              // Hàng 3: Lời gợi ý chỉ dẫn
              const Text(
                '👆 Chạm vào bất kỳ ô ảnh nào bên trên để thử thách độ trễ mở ảnh (VIP)',
                style: TextStyle(color: Colors.white54, fontSize: 9.5, fontStyle: FontStyle.italic),
                textAlign: TextAlign.center,
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
