import 'package:flutter/material.dart';

import 'config/run_config.dart';
import 'run_controller.dart';
import 'ui/demo_dock.dart';
import 'ui/monitor_overlay.dart';
import 'ui/photo_grid.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cfg = await RunConfig.loadConfig();
  runApp(MaterialApp(
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      useMaterial3: true,
      colorSchemeSeed: Colors.indigo,
      scaffoldBackgroundColor: const Color(0xFF0F172A),
    ),
    home: RunPage(cfg: cfg),
  ));
}

class RunPage extends StatefulWidget {
  const RunPage({super.key, required this.cfg});
  final RunConfig cfg;

  @override
  State<RunPage> createState() => _RunPageState();
}

class _RunPageState extends State<RunPage> {
  late final RunController ctl = RunController(widget.cfg);

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      try {
        await ctl.start();
      } catch (e, st) {
        ctl.status.value = 'ERROR';
        ctl.result.value = '$e';
        debugPrint('ERROR $e\n$st');
      }
    });
  }

  @override
  void dispose() {
    ctl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 44,
        backgroundColor: const Color(0xFF0F172A),
        foregroundColor: Colors.white,
        elevation: 0,
        title: ValueListenableBuilder<String>(
          valueListenable: ctl.currentPolicy,
          builder: (_, pol, _) => ValueListenableBuilder<String>(
            valueListenable: ctl.status,
            builder: (_, s, _) => Text(
              '${pol.toUpperCase()} • $s',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ),
        actions: [
          // Nút bật/dừng tự động cuộn (Auto Scroll)
          ValueListenableBuilder<bool>(
            valueListenable: ctl.isAutoScrolling,
            builder: (_, isAuto, _) => IconButton(
              icon: Icon(
                isAuto ? Icons.pause_circle_filled_rounded : Icons.play_circle_fill_rounded,
                color: isAuto ? Colors.amberAccent : Colors.white70,
                size: 22,
              ),
              tooltip: isAuto ? 'Dừng tự cuộn' : 'Bật tự động cuộn',
              onPressed: ctl.toggleAutoScroll,
            ),
          ),
          // Animation vòng xoay liên tục = "Máy dò Jank trực quan"
          const Padding(
            padding: EdgeInsets.only(right: 14, left: 4),
            child: SizedBox(
              width: 18,
              height: 18,
              child: CircularProgressIndicator(
                strokeWidth: 2.2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.cyanAccent),
              ),
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Lưới ảnh cuộn mượt tương tác
          ValueListenableBuilder<List<String>>(
            valueListenable: ctl.imagePaths,
            builder: (_, paths, _) => ValueListenableBuilder<Map<int, TileStatus>>(
              valueListenable: ctl.tileStatuses,
              builder: (_, statuses, _) => PhotoGrid(
                controller: ctl.scroll,
                imagePaths: paths,
                tileStatuses: statuses,
                onTileTap: ctl.handleTileTap,
              ),
            ),
          ),

          // Lớp hiển thị lỗi (nếu có)
          Positioned(
            left: 0,
            right: 0,
            bottom: 110,
            child: ValueListenableBuilder<String?>(
              valueListenable: ctl.result,
              builder: (_, r, _) => (r == null || ctl.status.value != 'ERROR')
                  ? const SizedBox.shrink()
                  : Container(
                      color: Colors.red.shade900.withValues(alpha: 0.9),
                      padding: const EdgeInsets.all(8),
                      child: Text(r, style: const TextStyle(color: Colors.white, fontSize: 11)),
                    ),
            ),
          ),

          // Màn hình HUD đo lường ở góc trên
          MonitorOverlay(snapshotNotifier: ctl.monitor),

          // Thanh điều khiển Live Demo nhanh ở góc dưới
          DemoControlDock(controller: ctl),
        ],
      ),
    );
  }
}
