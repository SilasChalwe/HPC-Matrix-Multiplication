from __future__ import annotations

import html
from pathlib import Path

from plotly.offline import get_plotlyjs

from charts_and_graphs.models import ChartDataFiles, ChartSections, ResultRow


class ReportBuilder:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_report(
        self,
        csv_path: Path,
        grouped_rows: dict[int, list[ResultRow]],
        chart_sections: dict[int, ChartSections],
        chart_data_files: ChartDataFiles,
    ) -> Path:
        report_path = self.output_dir / "performance_report.html"
        report_path.write_text(
            self._build_report(csv_path, grouped_rows, chart_sections, chart_data_files),
            encoding="utf-8",
        )
        return report_path

    def _build_report(
        self,
        csv_path: Path,
        grouped_rows: dict[int, list[ResultRow]],
        chart_sections: dict[int, ChartSections],
        chart_data_files: ChartDataFiles,
    ) -> str:
        sections = [
            self._build_section(matrix_size, rows, chart_sections[matrix_size])
            for matrix_size, rows in grouped_rows.items()
        ]

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Matrix Performance Report</title>
  <script>{get_plotlyjs()}</script>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 24px auto;
      max-width: 1180px;
      color: #0f172a;
      background: #f8fafc;
    }}
    h1, h2, h3 {{
      margin-bottom: 12px;
    }}
    .report-header {{
      margin-bottom: 20px;
    }}
    .report-subtitle {{
      margin-top: 0;
      color: #475569;
      max-width: 760px;
    }}
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 16px 0 0;
    }}
    .meta-pill {{
      background: #e0f2fe;
      border: 1px solid #bae6fd;
      color: #0f172a;
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 14px;
    }}
    section {{
      background: #ffffff;
      border: 1px solid #dbeafe;
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 20px;
    }}
    ul {{
      margin-top: 8px;
      margin-bottom: 16px;
      padding-left: 20px;
    }}
    th, td {{
      border: 1px solid #cbd5e1;
      padding: 10px 12px;
      text-align: left;
    }}
    th {{
      background: #e2e8f0;
    }}
    .chart-grid {{
      display: grid;
      gap: 20px;
    }}
    .chart-block {{
      background: #ffffff;
      border: 1px solid #dbeafe;
      border-radius: 14px;
      padding: 16px;
    }}
    .chart-title {{
      margin: 0 0 4px;
      font-size: 18px;
    }}
    .chart-aim {{
      margin: 0 0 14px;
      color: #475569;
      font-size: 14px;
    }}
    .chart-card {{
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 12px;
      background: #ffffff;
      overflow-x: auto;
    }}
    .info-card {{
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 24px;
    }}
    .formula {{
      font-family: "Courier New", monospace;
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 10px 12px;
      margin: 8px 0;
      display: inline-block;
    }}
    .section-note {{
      color: #475569;
      margin-top: 0;
      margin-bottom: 16px;
    }}
    .data-note {{
      margin-top: 20px;
      color: #64748b;
      font-size: 13px;
    }}
    .table-title {{
      margin-top: 0;
      color: #334155;
    }}
  </style>
</head>
<body>
  <div class="report-header">
    <h1>Matrix Performance Report</h1>
    <p class="report-subtitle">Serial and parallel matrix multiplication results, with sample spread, average time, and scaling shown for the latest comparable run set.</p>
    <div class="meta-row">
      <span class="meta-pill">Raw results: {html.escape(csv_path.name)}</span>
      <span class="meta-pill">Summary data: {html.escape(chart_data_files.summary_csv.name)}</span>
      <span class="meta-pill">Sample data: {html.escape(chart_data_files.sample_csv.name)}</span>
    </div>
  </div>
  <div class="info-card">
    <h2>How To Read This Report</h2>
    <ul>
      <li><strong>Serial</strong> means one-thread execution.</li>
      <li><strong>Parallel</strong> means OpenMP execution with the shown thread count.</li>
      <li><strong>Runs Averaged</strong> shows how many sample runs were used to get the average time.</li>
      <li><strong>Verified</strong> means the parallel result matched the serial result.</li>
    </ul>
    <p><strong>Formulas</strong></p>
    <div class="formula">average time = (sample1 + sample2 + ... + sampleN) / N</div><br>
    <div class="formula">speedup = serial average time / parallel average time</div><br>
    <div class="formula">efficiency = speedup / number of threads</div>
  </div>
  {"".join(sections)}
  <p class="data-note">The report uses the latest comparable rows for each matrix size, so serial and parallel values come from the same measured run set.</p>
</body>
</html>
"""

    def _build_section(self, matrix_size: int, rows: list[ResultRow], chart_sections: ChartSections) -> str:
        sample_counts = sorted({row.sample_count for row in rows if row.sample_count is not None})
        note = "Rows in this section use the same averaged run count."

        if len(sample_counts) == 1:
            note = f"Rows in this section are based on {sample_counts[0]} averaged runs."

        return f"""
<section>
  <h2>Matrix Size: {matrix_size} x {matrix_size}</h2>
  <p class="section-note">{html.escape(note)}</p>
  <h3 class="table-title">Measured Results</h3>
  {self._build_table(rows)}
  <div class="chart-grid">
    {self._build_chart_block("Sample Spread", "Aim: show every recorded sample for each run type, together with the average and the spread of the measured times.", chart_sections.sample_chart_html)}
    {self._build_chart_block("Average Time Comparison", "Aim: compare the average execution time of serial and parallel runs. Lower time is better.", chart_sections.time_chart_html)}
    {self._build_chart_block("Why Speedup Is Not Linear", "Aim: compare measured speedup with the ideal straight line. The gap comes from thread overhead, memory access cost, and coordination cost.", chart_sections.scaling_chart_html)}
  </div>
</section>
""".strip()

    @staticmethod
    def _build_chart_block(title: str, aim: str, chart_html: str) -> str:
        return f"""
<div class="chart-block">
  <h3 class="chart-title">{html.escape(title)}</h3>
  <p class="chart-aim">{html.escape(aim)}</p>
  <div class="chart-card">{chart_html}</div>
</div>
""".strip()

    @staticmethod
    def _build_table(rows: list[ResultRow]) -> str:
        lines = [
            "<table>",
            "<thead>",
            "<tr>",
            "<th>Mode</th>",
            "<th>Threads</th>",
            "<th>Runs Averaged</th>",
            "<th>Average Time (s)</th>",
            "<th>Speedup</th>",
            "<th>Efficiency</th>",
            "<th>Verified</th>",
            "</tr>",
            "</thead>",
            "<tbody>",
        ]

        for row in rows:
            lines.extend(
                [
                    "<tr>",
                    f"<td>{html.escape(row.mode)}</td>",
                    f"<td>{row.threads}</td>",
                    f"<td>{ReportBuilder._format_optional_int(row.sample_count)}</td>",
                    f"<td>{row.execution_seconds:.6f}</td>",
                    f"<td>{ReportBuilder._format_number(row.speedup)}</td>",
                    f"<td>{ReportBuilder._format_number(row.efficiency)}</td>",
                    f"<td>{html.escape(row.verified or 'N/A')}</td>",
                    "</tr>",
                ]
            )

        lines.extend(["</tbody>", "</table>"])
        return "\n".join(lines)

    @staticmethod
    def _format_number(value: float | None, decimals: int = 4) -> str:
        if value is None:
            return "N/A"
        return f"{value:.{decimals}f}"

    @staticmethod
    def _format_optional_int(value: int | None) -> str:
        if value is None:
            return "N/A"
        return str(value)
