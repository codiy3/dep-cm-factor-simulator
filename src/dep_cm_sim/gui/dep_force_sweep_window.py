from __future__ import annotations

from matplotlib.artist import Artist
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.ticker import NullLocator
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dep_cm_sim.crossover_display import (
    build_dep_force_metric_summary,
)
from dep_cm_sim.dep_force_sweep import DepForceSweepResult
from dep_cm_sim.gui.graph_window import (
    FREQUENCY_MAJOR_TICK_LABELS,
    FREQUENCY_MAJOR_TICKS,
    FREQUENCY_X_MAX_HZ,
    FREQUENCY_X_MIN_HZ,
    find_japanese_font_properties,
)


class DepForceSweepWindow(QMainWindow):
    """DEP力の周波数依存性を表示する専用グラフウィンドウ。"""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(
            "DEP CM Factor Simulator - DEP Force Frequency Sweep"
        )
        self.resize(900, 700)

        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)  # type: ignore[no-untyped-call]
        self.ax = self.figure.add_subplot(111)

        self.force_curve_handle: Artist | None = None
        self.crossover_marker_handles: list[Artist] = []
        self.crossover_info_handle: Text | None = None
        self.current_result: DepForceSweepResult | None = None
        self.japanese_font_properties = find_japanese_font_properties()

        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout.addWidget(self.canvas)

        self.clear_button = QPushButton("グラフをクリア")
        self.clear_button.clicked.connect(self.clear_graph)
        layout.addWidget(self.clear_button)

        self.setCentralWidget(central_widget)
        self._setup_axes()

    def _setup_axes(self) -> None:
        self.ax.set_xscale("log")
        self.ax.set_xticks(
            FREQUENCY_MAJOR_TICKS,
            labels=FREQUENCY_MAJOR_TICK_LABELS,
        )
        self.ax.xaxis.set_minor_locator(NullLocator())
        self.ax.set_xlim(FREQUENCY_X_MIN_HZ, FREQUENCY_X_MAX_HZ)
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("F_DEP [pN]")
        self.ax.set_title("DEP force frequency sweep")
        self.ax.set_axisbelow(True)
        self.ax.grid(
            True,
            which="major",
            axis="both",
            linestyle="--",
            linewidth=0.8,
            alpha=0.5,
        )
        self.ax.axhline(
            0.0,
            color="0.35",
            linestyle="-",
            linewidth=1.2,
            alpha=0.9,
            zorder=1.5,
            label="_nolegend_",
        )

    def _clear_dynamic_artists(self) -> None:
        if self.force_curve_handle is not None:
            try:
                self.force_curve_handle.remove()
            except ValueError:
                pass

            self.force_curve_handle = None

        for handle in self.crossover_marker_handles:
            try:
                handle.remove()
            except ValueError:
                pass

        self.crossover_marker_handles.clear()

        if self.crossover_info_handle is not None:
            try:
                self.crossover_info_handle.remove()
            except ValueError:
                pass

            self.crossover_info_handle = None

    def _add_crossover_markers(
        self,
        result: DepForceSweepResult,
    ) -> None:
        for crossover in result.crossover_results:
            marker = self.ax.axvline(
                crossover.frequency_hz,
                linestyle=":",
                linewidth=1.2,
                alpha=0.8,
                zorder=2.5,
                label="_nolegend_",
            )
            self.crossover_marker_handles.append(marker)

        self.crossover_info_handle = self.ax.text(
            0.98,
            0.98,
            build_dep_force_metric_summary(
                solution_conductivity_s_m=(
                    result.solution_conductivity_s_m
                ),
                crossover_results=result.crossover_results,
                force_pn_values=result.force_pn_values,
            ),
            transform=self.ax.transAxes,
            horizontalalignment="right",
            verticalalignment="top",
            fontsize=8,
            fontproperties=self.japanese_font_properties,
            bbox={
                "boxstyle": "round",
                "facecolor": "white",
                "alpha": 0.8,
            },
        )

    def update_result(
        self,
        result: DepForceSweepResult,
        *,
        label: str,
    ) -> None:
        """既存表示を置き換えて、新しい周波数掃引結果を表示する。"""

        if not label.strip():
            raise ValueError("グラフラベルを空にできません。")

        self._clear_dynamic_artists()

        (curve_line,) = self.ax.plot(
            result.frequency_hz,
            result.force_pn_values,
            label=label,
        )
        self.force_curve_handle = curve_line
        self.current_result = result

        self._add_crossover_markers(result)

        self.ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()  # type: ignore[no-untyped-call]

    def clear_graph(self) -> None:
        """DEP力曲線、crossover表示、保持中の計算結果を削除する。"""

        self.ax.clear()
        self.force_curve_handle = None
        self.crossover_marker_handles.clear()
        self.crossover_info_handle = None
        self.current_result = None

        self._setup_axes()
        self.figure.tight_layout()
        self.canvas.draw()  # type: ignore[no-untyped-call]
