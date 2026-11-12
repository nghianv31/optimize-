import 'dart:async';
import 'dart:isolate';

import '../workload/synthetic.dart';
import 'task.dart';

void _workerMain(SendPort toMain) {
  final rx = ReceivePort();
  toMain.send(rx.sendPort);
  rx.listen((m) {
    final msg = m as List<int>; // [taskId, iters]
    burn(msg[1]);
    toMain.send(msg[0]);
  });
}

/// Một isolate sống lâu. Mỗi lần chỉ chạy một tác vụ.
class PoolWorker {
  PoolWorker._(this._isolate, this._rx);
  final Isolate _isolate;
  final ReceivePort _rx;
  late SendPort _tx;
  bool busy = false;
  void Function(int taskId)? onDone;

  static Future<PoolWorker> spawn() async {
    final rx = ReceivePort();
    final ready = Completer<SendPort>();
    final iso = await Isolate.spawn(_workerMain, rx.sendPort);
    final w = PoolWorker._(iso, rx);
    rx.listen((m) {
      if (m is SendPort) {
        ready.complete(m);
      } else {
        w.busy = false;
        w.onDone?.call(m as int);
      }
    });
    w._tx = await ready.future;
    return w;
  }

  void run(Task t, int iters) {
    busy = true;
    _tx.send([t.id, iters]);
  }

  void kill() {
    _isolate.kill(priority: Isolate.immediate);
    _rx.close();
  }
}

class WorkerPool {
  WorkerPool(this.size);
  final int size;
  final workers = <PoolWorker>[];

  Future<void> start() async {
    for (int i = 0; i < size; i++) {
      workers.add(await PoolWorker.spawn());
    }
  }

  PoolWorker? acquire() {
    for (final w in workers) {
      if (!w.busy) return w;
    }
    return null;
  }

  void dispose() {
    for (final w in workers) {
      w.kill();
    }
    workers.clear();
  }
}
