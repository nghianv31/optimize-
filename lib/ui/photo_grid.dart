import 'dart:io';

import 'package:flutter/material.dart';

class TileStatus {
  final bool isLoading;
  final double? latencyMs;
  final int timestamp;
  const TileStatus({required this.isLoading, this.latencyMs, required this.timestamp});
}

/// Lưới ảnh hiển thị ảnh JPEG thật (hoặc ô màu dự phòng nếu chưa nạp ảnh).
/// Hỗ trợ vuốt lướt bằng tay và chạm mở chi tiết ảnh (tác vụ Critical).
class PhotoGrid extends StatelessWidget {
  const PhotoGrid({
    super.key,
    required this.controller,
    this.count = 2000,
    this.imagePaths = const [],
    this.onTileTap,
    this.tileStatuses = const {},
  });

  final ScrollController controller;
  final int count;
  final List<String> imagePaths;
  final void Function(int index, String? path)? onTileTap;
  final Map<int, TileStatus> tileStatuses;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      controller: controller,
      physics: const BouncingScrollPhysics(), // Mở khóa cho ngón tay vuốt lướt tự do
      padding: const EdgeInsets.fromLTRB(4, 180, 4, 120), // Chừa khoảng trống cho HUD ở trên và Dock ở dưới
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 5,
        crossAxisSpacing: 5,
      ),
      itemCount: count,
      itemBuilder: (_, i) {
        final imgPath = imagePaths.isEmpty ? null : imagePaths[i % imagePaths.length];
        return _Tile(
          i,
          imagePath: imgPath,
          status: tileStatuses[i],
          onTap: () => onTileTap?.call(i, imgPath),
        );
      },
    );
  }
}

class _Tile extends StatelessWidget {
  const _Tile(
    this.i, {
    this.imagePath,
    this.status,
    this.onTap,
  });

  final int i;
  final String? imagePath;
  final TileStatus? status;
  final VoidCallback? onTap;

  Widget _colorBox(double h) => DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(10),
          color: HSVColor.fromAHSV(1, h, .5, .85).toColor(),
        ),
        child: Center(
          child: Text(
            '#$i',
            style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
          ),
        ),
      );

  @override
  Widget build(BuildContext context) {
    final h = (i * 37) % 360.0;
    final isLoading = status?.isLoading ?? false;
    final latency = status?.latencyMs;

    Widget imageContent;
    if (imagePath == null) {
      imageContent = _colorBox(h);
    } else {
      imageContent = ClipRRect(
        borderRadius: BorderRadius.circular(10),
        child: Image.file(
          File(imagePath!),
          cacheWidth: 240,
          fit: BoxFit.cover,
          filterQuality: FilterQuality.low,
          gaplessPlayback: true,
          errorBuilder: (_, _, _) => _colorBox(h),
        ),
      );
    }

    return GestureDetector(
      onTap: onTap,
      child: RepaintBoundary(
        child: Stack(
          fit: StackFit.expand,
          children: [
            DecoratedBox(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: isLoading
                      ? Colors.amberAccent
                      : (latency != null
                          ? (latency <= 100
                              ? const Color(0xFF10B981)
                              : (latency <= 500 ? const Color(0xFFFBBF24) : const Color(0xFFEF4444)))
                          : Colors.white12),
                  width: isLoading || latency != null ? 2.5 : 0.8,
                ),
              ),
              child: imageContent,
            ),

            // Hiệu ứng đang tải (Loading Spinner)
            if (isLoading)
              Container(
                decoration: BoxDecoration(
                  color: Colors.black.withValues(alpha: 0.65),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.amberAccent),
                      ),
                    ),
                    SizedBox(height: 4),
                    Text(
                      'Đang mở...',
                      style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),

            // Nhãn hiển thị độ trễ phản hồi (VIP Latency Badge)
            if (latency != null && !isLoading)
              Positioned(
                bottom: 4,
                right: 4,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                  decoration: BoxDecoration(
                    color: latency <= 100
                        ? const Color(0xE6059669) // Xanh lá: Tức thì <100ms
                        : (latency <= 500
                            ? const Color(0xE6D97706) // Vàng: 100-500ms
                            : const Color(0xE6DC2626)), // Đỏ: >500ms (kẹt FIFO)
                    borderRadius: BorderRadius.circular(6),
                    boxShadow: const [
                      BoxShadow(color: Colors.black45, blurRadius: 4, offset: Offset(0, 1)),
                    ],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        latency <= 100 ? Icons.bolt_rounded : Icons.timer_outlined,
                        color: Colors.white,
                        size: 11,
                      ),
                      const SizedBox(width: 2),
                      Text(
                        latency >= 1000
                            ? '${(latency / 1000).toStringAsFixed(1)}s'
                            : '${latency.toStringAsFixed(0)}ms',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
