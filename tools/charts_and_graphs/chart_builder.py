from __future__ import annotations

from plotly import graph_objects as go

from charts_and_graphs.models import BuiltCharts, ChartFigures, ChartSections, ResultRow


class ChartBuilder:
    def create_charts(self, matrix_size: int, rows: list[ResultRow]) -> BuiltCharts:
        figures = self.create_figures(matrix_size, rows)
        return BuiltCharts(
            sections=ChartSections(
                sample_chart_html=figures.sample_figure.to_html(
                    full_html=False, include_plotlyjs=False, config=self._config()
                ),
                time_chart_html=figures.time_figure.to_html(
                    full_html=False, include_plotlyjs=False, config=self._config()
                ),
                scaling_chart_html=figures.scaling_figure.to_html(
                    full_html=False, include_plotlyjs=False, config=self._config()
                ),
            ),
            figures=figures,
        )

    def create_figures(self, matrix_size: int, rows: list[ResultRow]) -> ChartFigures:
        return ChartFigures(
            sample_figure=self._build_sample_figure(matrix_size, rows),
            time_figure=self._build_time_figure(matrix_size, rows),
            scaling_figure=self._build_scaling_figure(matrix_size, rows),
        )

    def _build_sample_figure(self, matrix_size: int, rows: list[ResultRow]) -> go.Figure:
        rows_with_samples = [row for row in rows if row.sample_times]

        if not rows_with_samples:
            figure = go.Figure()
            self._add_placeholder(
                figure,
                title=f"Sample Spread By Run Type ({matrix_size} x {matrix_size})",
                message="Run the program again to record per-sample times.",
                y_label="Run Type",
            )
            return figure

        figure = go.Figure()
        category_labels: list[str] = []

        for row in rows_with_samples:
            sample_numbers = list(range(1, len(row.sample_times) + 1))
            label = f"{row.mode} ({row.threads}T)"
            category_labels.append(label)
            color = self._trace_color(row)
            figure.add_trace(
                go.Box(
                    x=row.sample_times,
                    y=[label] * len(row.sample_times),
                    customdata=sample_numbers,
                    name=label,
                    orientation="h",
                    boxpoints="all",
                    jitter=0.34,
                    pointpos=0,
                    whiskerwidth=0.45,
                    marker=dict(size=11, color=color, line=dict(color="#0f172a", width=1)),
                    line=dict(color=color, width=2),
                    fillcolor=self._with_alpha(color, 0.14),
                    showlegend=False,
                    hovertemplate=(
                        "Run: "
                        + label
                        + "<br>Sample: S%{customdata}<br>Time: %{x:.6f} s<extra></extra>"
                    ),
                )
            )

            figure.add_trace(
                go.Scatter(
                    x=[row.execution_seconds],
                    y=[label],
                    mode="markers+text",
                    name=f"{label} average",
                    marker=dict(
                        symbol="diamond",
                        size=14,
                        color="#111827",
                        line=dict(color=color, width=2),
                    ),
                    text=[f"avg {row.execution_seconds:.4f}s"],
                    textposition="middle right",
                    showlegend=False,
                    hovertemplate=(
                        "Run: " + label + "<br>Average: %{x:.6f} s<extra></extra>"
                    ),
                )
            )

        figure.update_yaxes(
            title_text="Run Type",
            categoryorder="array",
            categoryarray=list(reversed(category_labels)),
            gridcolor="#e2e8f0",
            zerolinecolor="#cbd5e1",
        )
        figure.update_xaxes(
            title_text="Time (seconds)",
            gridcolor="#dbeafe",
            zerolinecolor="#cbd5e1",
        )
        figure.update_layout(
            title=f"Sample Spread By Run Type ({matrix_size} x {matrix_size})",
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(l=110, r=50, t=80, b=60),
            height=max(420, 90 * len(rows_with_samples)),
            boxmode="group",
            showlegend=False,
        )
        return figure

    def _build_time_figure(self, matrix_size: int, rows: list[ResultRow]) -> go.Figure:
        labels = [f"{row.mode} ({row.threads}T)" for row in rows]
        values = [row.execution_seconds for row in rows]
        colors = [self._trace_color(row) for row in rows]

        figure = go.Figure()
        figure.add_bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{value:.4f}" for value in values],
            textposition="outside",
            hovertemplate="Average time: %{x:.6f} s<br>Run: %{y}<extra></extra>",
        )
        self._apply_layout(
            figure,
            title=f"Average Execution Time ({matrix_size} x {matrix_size})",
            x_label="Seconds",
            y_label="Run Type",
            show_legend=False,
        )
        return figure

    def _build_scaling_figure(self, matrix_size: int, rows: list[ResultRow]) -> go.Figure:
        parallel_rows = sorted(
            [row for row in rows if row.mode == "Parallel" and row.speedup is not None],
            key=lambda row: row.threads,
        )

        if not parallel_rows:
            figure = go.Figure()
            self._add_placeholder(
                figure,
                title=f"Why Speedup Is Not Linear ({matrix_size} x {matrix_size})",
                message="Run compare mode first to record speedup values.",
                y_label="Speedup",
            )
            return figure

        threads = [1] + [row.threads for row in parallel_rows]
        actual_speedup = [1.0] + [row.speedup for row in parallel_rows if row.speedup is not None]
        ideal_speedup = [float(thread) for thread in threads]

        figure = go.Figure()
        figure.add_scatter(
            x=threads,
            y=ideal_speedup,
            mode="lines+markers",
            name="Ideal speedup",
            line=dict(color="#94a3b8", width=3, dash="dash"),
            marker=dict(size=9, color="#94a3b8"),
            hovertemplate="Threads: %{x}<br>Ideal speedup: %{y:.4f}<extra></extra>",
        )
        figure.add_scatter(
            x=threads,
            y=actual_speedup,
            mode="lines+markers",
            name="Measured speedup",
            line=dict(color="#dc2626", width=3),
            marker=dict(size=10, color="#dc2626", line=dict(color="#ffffff", width=1)),
            hovertemplate="Threads: %{x}<br>Measured speedup: %{y:.4f}<extra></extra>",
        )

        last_thread = threads[-1]
        last_speedup = actual_speedup[-1]
        figure.add_annotation(
            x=last_thread,
            y=last_speedup,
            text="Real result",
            showarrow=True,
            arrowhead=2,
            ax=-55,
            ay=-35,
            font=dict(size=11, color="#991b1b"),
            arrowcolor="#991b1b",
            bgcolor="#ffffff",
        )

        self._apply_layout(
            figure,
            title=f"Why Speedup Is Not Linear ({matrix_size} x {matrix_size})",
            x_label="Threads",
            y_label="Speedup",
            show_legend=True,
        )
        figure.update_xaxes(
            tickmode="array",
            tickvals=threads,
            gridcolor="#dbeafe",
            zerolinecolor="#cbd5e1",
        )
        figure.update_yaxes(
            rangemode="tozero",
            gridcolor="#dbeafe",
            zerolinecolor="#cbd5e1",
        )
        return figure

    @staticmethod
    def _trace_color(row: ResultRow) -> str:
        if row.mode == "Serial":
            return "#0f766e"

        colors = {
            2: "#2563eb",
            3: "#0f62fe",
            4: "#7c3aed",
            5: "#db2777",
            6: "#ea580c",
            7: "#65a30d",
            8: "#dc2626",
            10: "#0891b2",
            12: "#9333ea",
            16: "#b91c1c",
        }
        if row.threads in colors:
            return colors[row.threads]

        palette = [
            "#2563eb",
            "#7c3aed",
            "#db2777",
            "#ea580c",
            "#65a30d",
            "#0891b2",
            "#dc2626",
        ]
        return palette[row.threads % len(palette)]

    @staticmethod
    def _with_alpha(hex_color: str, alpha: float) -> str:
        red = int(hex_color[1:3], 16)
        green = int(hex_color[3:5], 16)
        blue = int(hex_color[5:7], 16)
        return f"rgba({red}, {green}, {blue}, {alpha})"

    @staticmethod
    def _apply_layout(
        figure: go.Figure,
        title: str,
        x_label: str,
        y_label: str,
        show_legend: bool,
    ) -> None:
        figure.update_layout(
            title=title,
            template="plotly_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            margin=dict(l=60, r=30, t=70, b=60),
            xaxis_title=x_label,
            yaxis_title=y_label,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            showlegend=show_legend,
        )
        figure.update_yaxes(gridcolor="#dbeafe", zerolinecolor="#cbd5e1")

    def _add_placeholder(self, figure: go.Figure, title: str, message: str, y_label: str) -> None:
        self._apply_layout(
            figure,
            title=title,
            x_label="Threads",
            y_label=y_label,
            show_legend=False,
        )
        figure.add_annotation(
            text=message,
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font=dict(size=16, color="#475569"),
        )
        figure.update_xaxes(visible=False)
        figure.update_yaxes(visible=False)

    @staticmethod
    def _config() -> dict[str, object]:
        return {
            "displaylogo": False,
            "responsive": True,
            "modeBarButtonsToRemove": [
                "select2d",
                "lasso2d",
                "zoomIn2d",
                "zoomOut2d",
                "autoScale2d",
                "hoverClosestCartesian",
                "hoverCompareCartesian",
                "toggleSpikelines",
            ],
        }
