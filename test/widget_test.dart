import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:optimize/config/run_config.dart';
import 'package:optimize/metrics/stats.dart';
import 'package:optimize/scheduler/aimd.dart';
import 'package:optimize/scheduler/mode_machine.dart';
import 'package:optimize/scheduler/priority_queue.dart';
import 'package:optimize/scheduler/scheduler.dart';
import 'package:optimize/scheduler/task.dart';
import 'package:optimize/workload/image_workload.dart';
import 'package:optimize/workload/scenarios.dart';

RunConfig cfg({int seed = 42, String scenario = 's1', String policy = 'p0'}) => RunConfig(
      policy: policy, scenario: scenario, device: 't', run: 1, seed: seed, workers: 8,
      chunkMs: 80, agingMs: 3000, load: 1.0, settleS: 0, warmupS: 0, durationS: 60, graceS: 1, autorun: false,
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

  test('scenario S2: tải tăng dần theo bậc thang và có 8 critical tasks', () {
    final s2 = buildScenario(cfg(scenario: 's2'));
    expect(s2.isNotEmpty, isTrue);
    expect(s2.where((s) => s.priority == Priority.critical).length, 8);
    // Kiểm tra số tác vụ ở nửa sau (30-60s) nhiều hơn nửa đầu (0-30s)
    final firstHalf = s2.where((s) => s.atMs < 30000).length;
    final secondHalf = s2.where((s) => s.atMs >= 30000).length;
    expect(secondHalf, greaterThan(firstHalf));
  });

  test('FrameSummary', () {
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

  group('AimdController', () {
    test('Tăng cộng khi frame mượt và giảm nhân khi frame chậm', () {
      final aimd = AimdController(
        minWorkers: 1,
        maxWorkers: 8,
        targetGapMs: 20.0,
        initialWorkers: 4.0,
        pacingMs: 0,
      );

      expect(aimd.workerCount, 4);

      // Frame mượt (gap = 15ms <= 20 * 0.8 = 16ms): Tăng cộng (+1)
      aimd.update(15.0);
      expect(aimd.workerCount, 5);

      aimd.update(15.0);
      expect(aimd.workerCount, 6);

      // Frame xấu (gap = 25ms > 20ms): Giảm nhân (* 0.5)
      aimd.update(25.0);
      expect(aimd.workerCount, 3);

      // Giảm tiếp
      aimd.update(30.0);
      expect(aimd.workerCount, 2);

      // Không giảm dưới minWorkers (1)
      aimd.update(30.0);
      aimd.update(30.0);
      expect(aimd.workerCount, 1);
    });
  });

  group('ModeMachine', () {
    test('Chuyển trạng thái kèm trễ hysteresis chống chập chờn', () {
      final mm = ModeMachine(hysteresisMs: 5000); // 5 giây
      expect(mm.currentMode, DegradeMode.normal);

      // Nhận tín hiệu Conserve tại t = 1s
      mm.update(DegradeMode.conserve, 1000 * 1000);
      expect(mm.currentMode, DegradeMode.normal); // Chưa đổi vì chưa đủ 5s

      // Tại t = 4s (3s trôi qua)
      mm.update(DegradeMode.conserve, 4000 * 1000);
      expect(mm.currentMode, DegradeMode.normal);

      // Tại t = 6.1s (> 5s trôi qua liên tục)
      mm.update(DegradeMode.conserve, 6100 * 1000);
      expect(mm.currentMode, DegradeMode.conserve); // Đã chuyển thành công!
      expect(mm.transitions, 1);

      // Tín hiệu dao động chập chờn ngắn không làm chuyển mode ngay
      mm.update(DegradeMode.critical, 6500 * 1000);
      mm.update(DegradeMode.conserve, 7000 * 1000); // quay lại conserve
      expect(mm.currentMode, DegradeMode.conserve);
    });
  });

  group('P4Scheduler Policy', () {
    test('createScheduler trả về P4Scheduler cho policy p4 và p4_aimd', () {
      final sP4 = createScheduler(cfg(policy: 'p4'));
      expect(sP4, isA<P4Scheduler>());

      final sP4Aimd = createScheduler(cfg(policy: 'p4_aimd'));
      expect(sP4Aimd, isA<P4Scheduler>());
      expect((sP4Aimd as P4Scheduler).useModes, isFalse);
    });
  });

  group('Real Image Workload (s_image)', () {
    test('scenario s_image gắn 80 ảnh img_00..img_79 và tải tăng dần', () {
      final a = buildScenario(cfg(scenario: 's_image'));
      final b = buildScenario(cfg(scenario: 's_image'));
      expect(a.isNotEmpty, isTrue);
      expect([for (final s in a) s.atMs], [for (final s in b) s.atMs]);
      expect(a.where((s) => s.priority == Priority.critical).length, 8);
      expect(a.every((s) => s.imageName != null && s.imageName!.startsWith('img_')), isTrue);
      final uniqueImgs = a.map((s) => s.imageName).toSet();
      expect(uniqueImgs.length, 80);
    });

    test('processImageChunk đọc ảnh JPEG thật từ assets và hỗ trợ fallback', () {
      // Fallback khi null hoặc không tồn tại
      final fb = processImageChunk(null, 5000, 0, 5000);
      expect(fb.isFinite, isTrue);

      final assetsDir = Directory('assets');
      String? realImg;
      if (assetsDir.existsSync()) {
        for (final ent in assetsDir.listSync(recursive: true)) {
          if (ent is File && ent.path.toLowerCase().endsWith('.jpg')) {
            realImg = ent.path;
            break;
          }
        }
      }
      expect(realImg, isNotNull);
      final res1 = processImageChunk(realImg, 10000, 0, 20000);
      final res2 = processImageChunk(realImg, 10000, 10000, 20000);
      expect(res1.isFinite, isTrue);
      expect(res2.isFinite, isTrue);
    });
  });
}
