double percentile(List<num> sortedAsc, double p) {
  if (sortedAsc.isEmpty) return 0;
  final n = sortedAsc.length;
  final idx = ((p * n).ceil() - 1).clamp(0, n - 1).toInt();
  return sortedAsc[idx].toDouble();
}

class FrameSummary {
  final int count;
  final double dropPct; // jank kiểu DevTools: max(build, raster) > ngân sách
  final double dropTotalPct; // tổng thời gian vsync→raster xong > ngân sách (khắt khe hơn)
  final double p95Ms; // p95 của totalSpan
  final double p99Ms;
  final double buildP95Ms;
  final double rasterP95Ms;
  final int extreme; // frame > 700 ms
  final double missedPct; // % frame KHÔNG được dựng so với kỳ vọng (duration*Hz)
  final double gapP95Ms; // p95 khoảng cách giữa 2 frame liên tiếp
  final double gapP99Ms;
  const FrameSummary(this.count, this.dropPct, this.dropTotalPct, this.p95Ms, this.p99Ms,
      this.buildP95Ms, this.rasterP95Ms, this.extreme,
      [this.missedPct = 0, this.gapP95Ms = 0, this.gapP99Ms = 0]);

  /// [rows]: mỗi dòng [vsync, build, raster, total] (µs).
  factory FrameSummary.from(List<List<int>> rows, double budgetUs, {int expectedFrames = 0}) {
    if (rows.isEmpty) return const FrameSummary(0, 0, 0, 0, 0, 0, 0, 0);
    final n = rows.length;
    final total = [for (final r in rows) r[3]]..sort();
    final build = [for (final r in rows) r[1]]..sort();
    final raster = [for (final r in rows) r[2]]..sort();
    final vs = [for (final r in rows) r[0]]..sort();
    final gaps = [for (int i = 1; i < vs.length; i++) vs[i] - vs[i - 1]]..sort();
    final missed = expectedFrames > 0 ? (100.0 * (expectedFrames - n) / expectedFrames).clamp(0.0, 100.0) : 0.0;
    final jank = rows.where((r) => (r[1] > r[2] ? r[1] : r[2]) > budgetUs).length;
    final jankTotal = rows.where((r) => r[3] > budgetUs).length;
    return FrameSummary(
      n,
      100.0 * jank / n,
      100.0 * jankTotal / n,
      percentile(total, 0.95) / 1000,
      percentile(total, 0.99) / 1000,
      percentile(build, 0.95) / 1000,
      percentile(raster, 0.95) / 1000,
      rows.where((r) => r[3] > 700000).length,
      missed.toDouble(),
      percentile(gaps, 0.95) / 1000,
      percentile(gaps, 0.99) / 1000,
    );
  }

  Map<String, Object?> toJson() => {
        'frames': count,
        'dropPct': double.parse(dropPct.toStringAsFixed(2)),
        'dropTotalPct': double.parse(dropTotalPct.toStringAsFixed(2)),
        'p95Ms': double.parse(p95Ms.toStringAsFixed(2)),
        'p99Ms': double.parse(p99Ms.toStringAsFixed(2)),
        'buildP95Ms': double.parse(buildP95Ms.toStringAsFixed(2)),
        'rasterP95Ms': double.parse(rasterP95Ms.toStringAsFixed(2)),
        'extremeFrames': extreme,
        'missedPct': double.parse(missedPct.toStringAsFixed(2)),
        'gapP95Ms': double.parse(gapP95Ms.toStringAsFixed(2)),
        'gapP99Ms': double.parse(gapP99Ms.toStringAsFixed(2)),
      };
}
