import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:optimize/config/run_config.dart';
import 'package:optimize/scheduler/scheduler.dart';
import 'package:optimize/scheduler/task.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('Benchmark Scheduler Overhead', () async {
    final cfg = RunConfig(
      policy: 'p3',
      scenario: 's1',
      device: 'bench',
      run: 1,
      seed: 42,
      workers: 4,
      chunkMs: 80,
      agingMs: 3000,
      load: 1.0,
      settleS: 0,
      warmupS: 0,
      durationS: 60,
      graceS: 1,
      autorun: false,
    );

    final scheduler = createScheduler(cfg);
    await scheduler.init();

    // Warm up
    for (int i = 0; i < 20; i++) {
      final t = Task(id: i, priority: Priority.critical, costMs: 1);
      scheduler.submit(t);
      while (t.endUs == 0) {
        await Future<void>.delayed(const Duration(milliseconds: 1));
      }
    }

    // Benchmark dispatch & roundtrip latency for 200 tasks
    final latenciesUs = <int>[];
    final sw = Stopwatch();

    for (int i = 0; i < 200; i++) {
      final t = Task(id: 1000 + i, priority: Priority.critical, costMs: 1);
      sw.reset();
      sw.start();
      scheduler.submit(t);
      while (t.endUs == 0) {
        await Future<void>.delayed(const Duration(microseconds: 100));
      }
      sw.stop();
      latenciesUs.add(sw.elapsedMicroseconds);
    }

    latenciesUs.sort();
    final p50Us = latenciesUs[(latenciesUs.length * 0.50).toInt()];
    final p95Us = latenciesUs[(latenciesUs.length * 0.95).toInt()];
    final p99Us = latenciesUs[(latenciesUs.length * 0.99).toInt()];

    print('=== SCHEDULER OVERHEAD BENCHMARK ===');
    print('Policy: P3 (4 workers, PriorityQueue, Chunking, Yielding)');
    print('Samples: ${latenciesUs.length}');
    print('Round-trip Dispatch Latency p50: ${(p50Us / 1000).toStringAsFixed(2)} ms ($p50Us us)');
    print('Round-trip Dispatch Latency p95: ${(p95Us / 1000).toStringAsFixed(2)} ms ($p95Us us)');
    print('Round-trip Dispatch Latency p99: ${(p99Us / 1000).toStringAsFixed(2)} ms ($p99Us us)');

    await scheduler.dispose();
  });
}
