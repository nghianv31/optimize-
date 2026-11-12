import 'package:flutter/material.dart';

/// Lưới "ảnh" giả lập (gradient + bóng đổ) để có tải raster tương tự lưới ảnh.
/// Sẽ thay bằng ảnh thật ở bước A8.
class PhotoGrid extends StatelessWidget {
  const PhotoGrid({super.key, required this.controller, this.count = 2000});
  final ScrollController controller;
  final int count;

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      controller: controller,
      physics: const NeverScrollableScrollPhysics(), // chỉ cuộn theo kịch bản
      padding: const EdgeInsets.all(4),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 4,
        crossAxisSpacing: 4,
      ),
      itemCount: count,
      itemBuilder: (_, i) => _Tile(i),
    );
  }
}

class _Tile extends StatelessWidget {
  const _Tile(this.i);
  final int i;

  @override
  Widget build(BuildContext context) {
    final h = (i * 37) % 360.0;
    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        // Nhẹ cho GPU: màu đặc, không gradient/shadow (máy yếu bị nghẽn raster)
        color: HSVColor.fromAHSV(1, h, .5, .85).toColor(),
      ),
      child: Center(child: Text('#$i', style: const TextStyle(color: Colors.white, fontSize: 18))),
    );
  }
}
