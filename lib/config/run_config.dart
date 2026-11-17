import 'dart:convert';
import 'dart:io';

import 'package:path_provider/path_provider.dart';

/// Cấu hình một lần đo, truyền qua --dart-define.
class RunConfig {
  final String policy; // p0 | naive | (p1..p4 ở các giai đoạn sau)
  final String scenario; // s1 | (s2..s4 sau)
  final String device; // nhãn thiết bị, vd a04e
  final int run; // số thứ tự lần chạy
  final int seed;
  final int workers; // N (dùng từ P1)
  final int chunkMs; // dùng từ P3
  final int agingMs; // P2+: 1 mức ưu tiên tụt = agingMs chờ
  final double load; // hệ số tốc độ đến của tác vụ (1.0 = chuẩn)
  final int settleS; // chờ ổn định
  final int warmupS; // warm-up, không tính
  final int durationS; // thời lượng kịch bản được ghi
  final int graceS; // chờ tác vụ còn tồn sau khi hết kịch bản
  final bool autorun;
  final int yieldMs; // P3: gap p95 giữa frame vượt ngưỡng này => UI bận
  final int deferCapMs; // P3: background chờ quá lâu thì không bị hoãn nữa
  final String tag; // nhãn thêm vào tên file (vd L8W4) để các cấu hình không ghi đè nhau

  const RunConfig({
    required this.policy,
    required this.scenario,
    required this.device,
    required this.run,
    required this.seed,
    required this.workers,
    required this.chunkMs,
    required this.load,
    required this.agingMs,
    required this.settleS,
    required this.warmupS,
    required this.durationS,
    required this.graceS,
    required this.autorun,
    this.yieldMs = 20,
    this.deferCapMs = 8000,
    this.tag = '',
  });

  factory RunConfig.fromEnv() => RunConfig(
        policy: const String.fromEnvironment('POLICY', defaultValue: 'p0'),
        scenario: const String.fromEnvironment('SCENARIO', defaultValue: 's1'),
        device: const String.fromEnvironment('DEVICE', defaultValue: 'dev'),
        run: const int.fromEnvironment('RUN', defaultValue: 1),
        seed: const int.fromEnvironment('SEED', defaultValue: 42),
        workers: const int.fromEnvironment('WORKERS', defaultValue: 8),
        chunkMs: const int.fromEnvironment('CHUNK_MS', defaultValue: 80),
        agingMs: const int.fromEnvironment('AGING_MS', defaultValue: 3000),
        load: double.parse(const String.fromEnvironment('LOAD', defaultValue: '1.0')),
        settleS: const int.fromEnvironment('SETTLE_S', defaultValue: 10),
        warmupS: const int.fromEnvironment('WARMUP_S', defaultValue: 10),
        durationS: const int.fromEnvironment('DURATION_S', defaultValue: 60),
        graceS: const int.fromEnvironment('GRACE_S', defaultValue: 30),
        autorun: const bool.fromEnvironment('AUTORUN', defaultValue: false),
        yieldMs: const int.fromEnvironment('YIELD_MS', defaultValue: 20),
        deferCapMs: const int.fromEnvironment('DEFER_CAP_MS', defaultValue: 8000),
        tag: const String.fromEnvironment('TAG', defaultValue: ''),
      );

  /// Ưu tiên config.json trong thư mục ngoài của app (do tools/run_matrix.py đẩy
  /// bằng adb) rồi mới tới --dart-define. Nhờ vậy không cần build lại giữa các lần đo.
  static Future<RunConfig> loadConfig() async {
    final env = RunConfig.fromEnv();
    try {
      final d = await getExternalStorageDirectory();
      final f = File('${d!.path}/config.json');
      if (await f.exists()) {
        return env._merge(jsonDecode(await f.readAsString()) as Map<String, dynamic>);
      }
    } catch (_) {}
    return env;
  }

  RunConfig copyWith({
    String? policy,
    String? scenario,
    String? device,
    int? run,
    int? seed,
    int? workers,
    int? chunkMs,
    int? agingMs,
    double? load,
    int? settleS,
    int? warmupS,
    int? durationS,
    int? graceS,
    bool? autorun,
    int? yieldMs,
    int? deferCapMs,
    String? tag,
  }) =>
      RunConfig(
        policy: policy ?? this.policy,
        scenario: scenario ?? this.scenario,
        device: device ?? this.device,
        run: run ?? this.run,
        seed: seed ?? this.seed,
        workers: workers ?? this.workers,
        chunkMs: chunkMs ?? this.chunkMs,
        agingMs: agingMs ?? this.agingMs,
        load: load ?? this.load,
        settleS: settleS ?? this.settleS,
        warmupS: warmupS ?? this.warmupS,
        durationS: durationS ?? this.durationS,
        graceS: graceS ?? this.graceS,
        autorun: autorun ?? this.autorun,
        yieldMs: yieldMs ?? this.yieldMs,
        deferCapMs: deferCapMs ?? this.deferCapMs,
        tag: tag ?? this.tag,
      );

  RunConfig _merge(Map<String, dynamic> m) => RunConfig(
        policy: (m['policy'] ?? policy) as String,
        scenario: (m['scenario'] ?? scenario) as String,
        device: (m['device'] ?? device) as String,
        run: (m['run'] ?? run) as int,
        seed: (m['seed'] ?? seed) as int,
        workers: (m['workers'] ?? workers) as int,
        chunkMs: (m['chunkMs'] ?? chunkMs) as int,
        agingMs: (m['agingMs'] ?? agingMs) as int,
        load: ((m['load'] ?? load) as num).toDouble(),
        settleS: (m['settleS'] ?? settleS) as int,
        warmupS: (m['warmupS'] ?? warmupS) as int,
        durationS: (m['durationS'] ?? durationS) as int,
        graceS: (m['graceS'] ?? graceS) as int,
        autorun: (m['autorun'] ?? autorun) as bool,
        yieldMs: (m['yieldMs'] ?? yieldMs) as int,
        deferCapMs: (m['deferCapMs'] ?? deferCapMs) as int,
        tag: (m['tag'] ?? tag) as String,
      );

  String get name => '${policy}_${scenario}_${device}_${tag.isEmpty ? '' : '${tag}_'}$run';

  Map<String, Object?> toJson() => {
        'policy': policy,
        'scenario': scenario,
        'device': device,
        'run': run,
        'seed': seed,
        'workers': workers,
        'chunkMs': chunkMs,
        'load': load,
        'agingMs': agingMs,
        'settleS': settleS,
        'warmupS': warmupS,
        'durationS': durationS,
        'graceS': graceS,
        'yieldMs': yieldMs,
        'deferCapMs': deferCapMs,
        'tag': tag,
      };
}
