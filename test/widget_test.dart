import 'package:flutter_test/flutter_test.dart';
import 'package:optimize/config/run_config.dart';
import 'package:optimize/metrics/stats.dart';
import 'package:optimize/scheduler/priority_queue.dart';
import 'package:optimize/scheduler/task.dart';
import 'package:optimize/workload/scenarios.dart';

RunConfig cfg({int seed = 42}) => RunConfig(
      policy: 'p0', scenario: 's1', device: 't', run: 1, seed: seed, workers: 3,
      chunkMs: 10, agingMs: 3000, load: 1.0, settleS: 0, warmupS: 0, durationS: 60, graceS: 1, autorun: false,
    );

void main() {
  test('scenario S1 xác định theo seed', () {
    final a = buildScenario(cfg());
    final b = buildScenario(cfg());
    final c = buildScenario(cfg(seed: 7));
    expect([for (final s in a) s.atMs], [for (final s in b) s.atMs]);
    expect([for (final s in a) s.atMs], isNot([for (final s in c) s.atMs]));
    expect(a.where((s) => s.priority.name == 'critical').length, 5);
  });

  test('FrameSummary', () {
    // 90 frame tốt (build/raster 5ms), 10 frame raster 30ms
    final rows = List<List<int>>.generate(
        100, (i) => i < 90 ? [i, 5000, 5000, 10000] : [i, 5000, 30000, 35000]);
    final s = FrameSummary.from(rows, 16666);
    expect(s.dropPct, closeTo(10, 1e-9));
    expect(s.dropTotalPct, closeTo(10, 1e-9));
    expect(s.rasterP95Ms, 30);
  });

  group('pickNext', () {
    Task mk(int id, Priority p, int submitMs) =>
        Task(id: id, priority: p, costMs: 10)..submitUs = submitMs * 1000;

    test('FIFO khi không ưu tiên', () {
      final q = [mk(1, Priority.background, 0), mk(2, Priority.critical, 1)];
      expect(pickNext(q, 10000, usePriority: false, agingMs: 3000), 0);
    });
    test('critical thắng background', () {
      final q = [mk(1, Priority.background, 0), mk(2, Priority.critical, 1)];
      expect(pickNext(q, 10000, usePriority: true, agingMs: 3000), 1);
    });
    test('aging: background chờ rất lâu vượt critical mới', () {
      // background chờ 10s (score 6000-10000<0), critical vừa đến (score ~0)
      final q = [mk(1, Priority.background, 0), mk(2, Priority.critical, 10000)];
      expect(pickNext(q, 10000 * 1000, usePriority: true, agingMs: 3000), 0);
    });
  });

  group('TaskQueue', () {
    Task mk(int id, Priority p, int submitMs) =>
        Task(id: id, priority: p, costMs: 10)..submitUs = submitMs * 1000;

    test('FIFO một mức khi !usePriority', () {
      final q = TaskQueue(usePriority: false)
        ..add(mk(1, Priority.background, 0))
        ..add(mk(2, Priority.critical, 1));
      expect(q.popNext(5000, agingMs: 3000)!.id, 1);
    });
    test('critical trước background; eligible lọc đầu hàng', () {
      final q = TaskQueue(usePriority: true)
        ..add(mk(1, Priority.background, 0))
        ..add(mk(2, Priority.critical, 1));
      expect(q.popNext(5000, agingMs: 3000)!.id, 2);
      q.add(mk(3, Priority.critical, 2));
      expect(q.popNext(5000, agingMs: 3000, eligible: (t) => t.priority != Priority.critical)!.id, 1);
    });
    test('addFront đặt chunk dở lên đầu mức của nó', () {
      final q = TaskQueue(usePriority: true)
        ..add(mk(1, Priority.visible, 0))
        ..addFront(mk(2, Priority.visible, 5));
      expect(q.popNext(5000, agingMs: 3000)!.id, 2);
    });
  });
}
