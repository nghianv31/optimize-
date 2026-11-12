import 'package:flutter/material.dart';

import 'config/run_config.dart';
import 'run_controller.dart';
import 'ui/photo_grid.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cfg = await RunConfig.loadConfig();
  runApp(MaterialApp(
    debugShowCheckedModeBanner: false,
    theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.indigo),
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
    if (widget.cfg.autorun) {
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
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        toolbarHeight: 48,
        title: ValueListenableBuilder<String>(
          valueListenable: ctl.status,
          builder: (_, s, __) => Text('${widget.cfg.policy}/${widget.cfg.scenario}  $s',
              style: const TextStyle(fontSize: 13)),
        ),
        actions: const [
          // Animation vòng xoay liên tục = "máy dò jank"
          Padding(
            padding: EdgeInsets.only(right: 16),
            child: SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 3)),
          ),
        ],
      ),
      body: Stack(
        children: [
          PhotoGrid(controller: ctl.scroll),
          Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: ValueListenableBuilder<String?>(
              valueListenable: ctl.result,
              builder: (_, r, __) => r == null
                  ? const SizedBox.shrink()
                  : Container(
                      color: Colors.black87,
                      padding: const EdgeInsets.all(8),
                      child: Text(r, style: const TextStyle(color: Colors.white, fontSize: 11)),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}
