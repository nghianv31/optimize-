import 'dart:io';
import 'dart:isolate';
import 'dart:math';
import 'dart:typed_data';

import 'synthetic.dart';

/// Kích thước vùng đệm tối đa đọc mỗi chunk (256 KB) để vừa tạo tải File I/O
/// thực tế vừa tránh tràn RAM (OOM) khi nhiều worker cùng giải mã song song.
const int _maxChunkBytes = 256 * 1024;

/// Trích xuất kích thước (width, height) từ JPEG SOF marker trong phần header.
(int, int) _parseJpegDimensions(Uint8List header) {
  if (header.length < 4 || header[0] != 0xFF || header[1] != 0xD8) {
    return (0, 0);
  }
  int pos = 2;
  while (pos + 8 < header.length) {
    if (header[pos] != 0xFF) {
      pos++;
      continue;
    }
    final marker = header[pos + 1];
    // Skip padding 0xFF
    if (marker == 0xFF) {
      pos++;
      continue;
    }
    // SOF0 (0xC0) hoặc SOF2 (0xC2 - progressive) chứa kích thước ảnh
    if (marker == 0xC0 || marker == 0xC2) {
      final h = (header[pos + 5] << 8) | header[pos + 6];
      final w = (header[pos + 7] << 8) | header[pos + 8];
      return (w, h);
    }
    // Marker không có độ dài (SOI/EOI/RST)
    if (marker == 0xD8 || marker == 0xD9 || (marker >= 0xD0 && marker <= 0xD7)) {
      pos += 2;
      continue;
    }
    if (pos + 3 >= header.length) break;
    final segLen = (header[pos + 2] << 8) | header[pos + 3];
    if (segLen < 2) break;
    pos += 2 + segLen;
  }
  return (0, 0);
}

/// Đọc lát cắt dữ liệu ảnh JPEG thực tế từ [imagePath] theo tiến độ
/// [chunkOffset]/[totalIters], phân tích header & tính toán histogram/hash
/// theo khối lượng [iters]. Nếu file không tồn tại, fallback về [burn].
double processImageChunk(
  String? imagePath,
  int iters,
  int chunkOffset,
  int totalIters,
) {
  if (imagePath == null) {
    return burn(iters);
  }
  final file = File(imagePath);
  if (!file.existsSync()) {
    return burn(iters);
  }

  RandomAccessFile? raf;
  try {
    raf = file.openSync(mode: FileMode.read);
    final fileLen = raf.lengthSync();
    if (fileLen <= 0) {
      return burn(iters);
    }

    int imgWidth = 0;
    int imgHeight = 0;

    // Khi bắt đầu tác vụ, đọc 4 KB đầu để parse JPEG SOI + SOF marker
    if (chunkOffset == 0) {
      raf.setPositionSync(0);
      final headerBytes = raf.readSync(min(4096, fileLen));
      final (w, h) = _parseJpegDimensions(headerBytes);
      imgWidth = w;
      imgHeight = h;
    }

    // Đọc lát cắt byte dữ liệu thực tế tương ứng vị trí chunkOffset
    final progress = totalIters > 0 ? (chunkOffset / totalIters).clamp(0.0, 0.99) : 0.0;
    final int startByte = (progress * fileLen).floor().clamp(0, max(0, fileLen - 1)).toInt();
    raf.setPositionSync(startByte);
    final int readLen = min(_maxChunkBytes, fileLen - startByte);
    final chunkBytes = raf.readSync(readLen);

    // Tính Histogram 256 bins & năng lượng khối điểm ảnh thực tế
    final hist = Int32List(256);
    double blockEnergy = (imgWidth + imgHeight).toDouble();
    final len = chunkBytes.length;
    if (len > 0) {
      final sampleStep = max(1, len ~/ 4096);
      for (int i = 0; i < len; i += sampleStep) {
        final v = chunkBytes[i];
        hist[v]++;
        blockEnergy = blockEnergy * 0.99999 + v * 1e-4;
      }
    }

    // Chuẩn hóa khối lượng tính toán tỷ lệ theo iters trên dữ liệu ảnh thực
    double acc = 1.0 + blockEnergy * 1e-6;
    final byteMask = len > 0 ? len - 1 : 0;
    for (int i = 0; i < iters; i++) {
      final sample = len > 0 ? chunkBytes[i % len] : (i & 0xFF);
      final hVal = hist[sample & 0xFF];
      acc = acc * 1.0000001 + ((sample ^ hVal) & 7) * 1e-9;
    }
    if (byteMask < 0) return 0.0;
    return acc;
  } finally {
    raf?.closeSync();
  }
}

/// Phiên bản Isolate.run cho chế độ NaiveIsolateScheduler trên ảnh thật.
Future<double> processImageInIsolate(String? imagePath, int iters) =>
    Isolate.run(() => processImageChunk(imagePath, iters, 0, iters));
