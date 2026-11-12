import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

import '../scheduler/task.dart';

/// Thư mục xuất: /sdcard/Android/data/<pkg>/files (kéo về bằng adb pull).
Future<Directory> outDir() async {
  final d = await getExternalStorageDirectory() ?? await getApplicationDocumentsDirectory();
  await d.create(recursive: true);
  return d;
}

Future<List<String>> writeRun({
  required String name,
  required int runStartUs,
  required List<List<int>> frames,
  required List<Task> tasks,
  required Map<String, Object?> meta,
}) async {
  final dir = await outDir();

  final f = StringBuffer('vsync_us,build_us,raster_us,total_us\n');
  for (final r in frames) {
    f.writeln('${r[0] - runStartUs},${r[1]},${r[2]},${r[3]}');
  }

  final t = StringBuffer('id,priority,cost_ms,submit_us,start_us,end_us\n');
  for (final k in tasks) {
    int rel(int v) => v == 0 ? -1 : v - runStartUs; // -1 = chưa xảy ra
    t.writeln('${k.id},${k.priority.name},${k.costMs},${rel(k.submitUs)},${rel(k.startUs)},${rel(k.endUs)}');
  }

  final paths = ['${dir.path}/frames_$name.csv', '${dir.path}/tasks_$name.csv', '${dir.path}/meta_$name.json'];
  await File(paths[0]).writeAsString(f.toString());
  await File(paths[1]).writeAsString(t.toString());
  await File(paths[2]).writeAsString(const JsonEncoder.withIndent('  ').convert(meta));
  return paths;
}
