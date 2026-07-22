from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
from matplotlib.artist import Artist
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties, fontManager
from matplotlib.text import Text
from matplotlib.ticker import NullLocator
from matplotlib.typing import ColorType
from numpy.typing import NDArray
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dep_cm_sim.condition_optimizer import (
    FrequencyOptimizationResult,
    find_optimal_opposite_sign_frequency,
)
from dep_cm_sim.crossover_display import build_crossover_summary
from dep_cm_sim.csv_export import (
    CsvExportError,
    CurveExportData,
    OptimizationSnapshot,
    ParameterSnapshot,
    derive_csv_paths,
    save_simulation_csv_files,
)
from dep_cm_sim.equations import (
    CrossoverFrequencyResult,
    find_crossover_frequencies,
)
from dep_cm_sim.optimization import (
    OptimalFrequencyResult,
    find_optimal_frequency,
)


FREQUENCY_X_MIN_HZ = 1.0
FREQUENCY_X_MAX_HZ = 1.0e10

FREQUENCY_MAJOR_TICKS: tuple[float, ...] = (
    1.0,
    1.0e1,
    1.0e2,
    1.0e3,
    1.0e4,
    1.0e5,
    1.0e6,
    1.0e7,
    1.0e8,
    1.0e9,
    1.0e10,
)

FREQUENCY_MAJOR_TICK_LABELS: tuple[str, ...] = (
    "1",
    "10",
    r"$10^{2}$",
    r"$10^{3}$",
    r"$10^{4}$",
    r"$10^{5}$",
    r"$10^{6}$",
    r"$10^{7}$",
    r"$10^{8}$",
    r"$10^{9}$",
    r"$10^{10}$",
)


@dataclass
class CurveData:
    label: str
    frequencies: NDArray[np.float64]
    values: NDArray[np.float64]
    parameters: tuple[ParameterSnapshot, ...] = ()
    crossover_frequencies_hz: tuple[float, ...] = ()


def find_japanese_font_properties() -> FontProperties | None:
    """利用可能な日本語フォントを優先順位順に取得する。"""

    candidates = (
        "Hiragino Sans",
        "BIZ UDGothic",
        "YuGothic",
        "Yu Gothic",
        "Noto Sans CJK JP",
        "Noto Sans JP",
        "IPAexGothic",
        "IPAGothic",
    )
    installed_fonts = {font.name for font in fontManager.ttflist}

    for candidate in candidates:
        if candidate in installed_fonts:
            return FontProperties(family=candidate)

    return None


class GraphWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DEP CM Factor Simulator - Graph Window")
        self.resize(900, 700)

        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.curve_data_list: list[CurveData] = []
        self.optimization_snapshot: OptimizationSnapshot | None = None
        self.optimal_marker_handles: list[Artist] = []
        self.crossover_marker_handles: list[Artist] = []
        self.crossover_summaries: list[str] = []
        self.crossover_info_handle: Text | None = None
        self.crossover_font_properties = find_japanese_font_properties()

        central_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.canvas)

        button_layout = QHBoxLayout()

        save_button = QPushButton("PNG保存")
        save_button.clicked.connect(self.save_png)
        button_layout.addWidget(save_button)

        csv_save_button = QPushButton("CSV保存")
        csv_save_button.clicked.connect(self.save_csv)
        button_layout.addWidget(csv_save_button)

        self.optimal_frequency_mode_combo = QComboBox()
        self.optimal_frequency_mode_combo.addItem("差分最大", "difference_only")
        self.optimal_frequency_mode_combo.addItem("符号分離", "opposite_sign")
        button_layout.addWidget(self.optimal_frequency_mode_combo)

        optimal_frequency_button = QPushButton("最適周波数を表示")
        optimal_frequency_button.clicked.connect(self.show_optimal_frequency)
        button_layout.addWidget(optimal_frequency_button)

        clear_button = QPushButton("グラフをクリア")
        clear_button.clicked.connect(self.clear_graph)
        button_layout.addWidget(clear_button)

        layout.addLayout(button_layout)

        central_widget.setLayout(layout)
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
        self.ax.set_ylabel("Re[K]")
        self.ax.set_title("Real part of Clausius-Mossotti factor")
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

    def _refresh_crossover_info(self) -> None:
        if self.crossover_info_handle is not None:
            try:
                self.crossover_info_handle.remove()
            except ValueError:
                pass

            self.crossover_info_handle = None

        if not self.crossover_summaries:
            return

        self.crossover_info_handle = self.ax.text(
            0.98,
            0.98,
            "\n\n".join(self.crossover_summaries),
            transform=self.ax.transAxes,
            horizontalalignment="right",
            verticalalignment="top",
            fontsize=8,
            fontproperties=self.crossover_font_properties,
            bbox={
                "boxstyle": "round",
                "facecolor": "white",
                "alpha": 0.8,
            },
        )

    def _add_crossover_markers(
        self,
        label: str,
        color: ColorType,
        results: Sequence[CrossoverFrequencyResult],
    ) -> None:
        for result in results:
            vertical_line = self.ax.axvline(
                result.frequency_hz,
                linestyle=":",
                linewidth=1.2,
                color=color,
                alpha=0.8,
                zorder=2.5,
                label="_nolegend_",
            )
            self.crossover_marker_handles.append(vertical_line)

        self.crossover_summaries.append(build_crossover_summary(label, results))
        self._refresh_crossover_info()

    def _clear_optimal_markers(self) -> None:
        for handle in self.optimal_marker_handles:
            try:
                handle.remove()
            except ValueError:
                pass

        self.optimal_marker_handles.clear()
        self.optimization_snapshot = None

    def add_curve(
        self,
        frequency_hz: NDArray[np.float64],
        cm_factor_real: NDArray[np.float64],
        label: str,
        parameters: Sequence[ParameterSnapshot] = (),
    ) -> None:
        if frequency_hz.size == 0:
            raise ValueError("frequency_hz must not be empty.")
        if cm_factor_real.size == 0:
            raise ValueError("cm_factor_real must not be empty.")
        if frequency_hz.shape != cm_factor_real.shape:
            raise ValueError("frequency_hz and cm_factor_real must have the same shape.")
        if np.any(frequency_hz <= 0):
            raise ValueError("frequency_hz must be positive.")
        if np.isnan(cm_factor_real).any():
            raise ValueError("cm_factor_real must not contain NaN.")
        if not label.strip():
            raise ValueError("label must not be empty.")

        frequency_snapshot = np.array(
            frequency_hz,
            dtype=np.float64,
            copy=True,
        )
        value_snapshot = np.array(
            cm_factor_real,
            dtype=np.float64,
            copy=True,
        )
        crossover_results = find_crossover_frequencies(
            frequency_hz=frequency_snapshot,
            re_k_values=value_snapshot,
        )

        # 曲線構成が変わった場合、以前の最適化結果は無効になる。
        self._clear_optimal_markers()

        (curve_line,) = self.ax.plot(
            frequency_snapshot,
            value_snapshot,
            label=label,
        )
        self.curve_data_list.append(
            CurveData(
                label=label,
                frequencies=frequency_snapshot,
                values=value_snapshot,
                parameters=tuple(parameters),
                crossover_frequencies_hz=tuple(
                    result.frequency_hz for result in crossover_results
                ),
            )
        )
        self._add_crossover_markers(
            label=label,
            color=curve_line.get_color(),
            results=crossover_results,
        )
        self.ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def save_csv(self) -> None:
        if not self.curve_data_list:
            QMessageBox.warning(
                self,
                "CSV保存エラー",
                "保存対象のシミュレーション曲線がありません。",
            )
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = Path("outputs") / f"cm_factor_{timestamp}.csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "シミュレーション結果をCSV保存",
            str(default_path),
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        base_path = Path(file_path)
        summary_path, curve_data_path = derive_csv_paths(base_path)

        existing_paths = [
            path
            for path in (summary_path, curve_data_path)
            if path.exists()
        ]

        if existing_paths:
            existing_text = "\n".join(str(path) for path in existing_paths)
            response = QMessageBox.question(
                self,
                "CSV上書き確認",
                (
                    "次のファイルは既に存在します。上書きしますか？"
                    f"\n\n{existing_text}"
                ),
                (
                    QMessageBox.StandardButton.Yes
                    | QMessageBox.StandardButton.No
                ),
                QMessageBox.StandardButton.No,
            )

            if response != QMessageBox.StandardButton.Yes:
                return

        export_curves = [
            CurveExportData(
                label=curve.label,
                frequencies=curve.frequencies,
                values=curve.values,
                parameters=curve.parameters,
                crossover_frequencies_hz=curve.crossover_frequencies_hz,
            )
            for curve in self.curve_data_list
        ]

        try:
            saved_summary_path, saved_curve_data_path = (
                save_simulation_csv_files(
                    base_path=base_path,
                    curves=export_curves,
                    optimization=self.optimization_snapshot,
                )
            )
        except CsvExportError as error:
            if error.saved_paths:
                saved_text = "\n".join(
                    str(path) for path in error.saved_paths
                )
            else:
                saved_text = "なし"

            QMessageBox.critical(
                self,
                "CSV保存エラー",
                (
                    "CSVを完全には保存できませんでした。"
                    f"\n\n原因:\n{error}"
                    f"\n\n保存済みファイル:\n{saved_text}"
                    f"\n\nsummary予定先:\n{error.summary_path}"
                    f"\n\ncurve data予定先:\n{error.curve_data_path}"
                ),
            )
            return
        except Exception as error:
            QMessageBox.critical(
                self,
                "CSV保存エラー",
                f"CSVを保存できませんでした。\n\n原因:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "CSV保存完了",
            (
                "シミュレーション結果を2ファイルへ保存しました。"
                f"\n\nサマリーCSV:\n{saved_summary_path}"
                f"\n\n曲線データCSV:\n{saved_curve_data_path}"
            ),
        )

    def save_png(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = Path("outputs") / f"cm_factor_{timestamp}.png"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "PNGとして保存",
            str(default_path),
            "PNG files (*.png)",
        )

        if not file_path:
            return

        save_path = Path(file_path)
        if save_path.suffix.lower() != ".png":
            save_path = save_path.with_suffix(".png")

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            self.figure.savefig(save_path, dpi=300)
        except Exception as error:
            QMessageBox.critical(
                self,
                "PNG保存エラー",
                f"PNGを保存できませんでした。\n\n原因:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "PNG保存完了",
            f"PNGを保存しました。\n\n保存先:\n{save_path}",
        )

    def clear_graph(self) -> None:
        self.ax.clear()
        self.curve_data_list.clear()
        self.optimal_marker_handles.clear()
        self.optimization_snapshot = None
        self.crossover_marker_handles.clear()
        self.crossover_summaries.clear()
        self.crossover_info_handle = None
        self._setup_axes()
        self.figure.tight_layout()
        self.canvas.draw()

    def show_optimization_result_marker(
        self,
        frequency_hz: float,
        value_1: float,
        value_2: float,
        difference: float,
        label: str = "optimal",
    ) -> None:
        self._clear_optimal_markers()

        vertical_line = self.ax.axvline(
            frequency_hz,
            linestyle="--",
            linewidth=1.6,
            alpha=0.9,
            zorder=3.0,
            label="_nolegend_",
        )

        annotation = self.ax.annotate(
            (
                f"f_opt = {frequency_hz:.2e} Hz\n"
                f"|ΔRe[K]| = {difference:.3f}\n"
                f"Re[K]1 = {value_1:.3f}\n"
                f"Re[K]2 = {value_2:.3f}\n"
                f"mode = {label}"
            ),
            xy=(frequency_hz, max(value_1, value_2)),
            xytext=(0.05, 0.05),
            textcoords="axes fraction",
            bbox={
                "boxstyle": "round",
                "facecolor": "white",
                "alpha": 0.8,
            },
        )

        self.optimal_marker_handles.extend([vertical_line, annotation])

        curve_1_label = (
            self.curve_data_list[0].label
            if len(self.curve_data_list) >= 1
            else ""
        )
        curve_2_label = (
            self.curve_data_list[1].label
            if len(self.curve_data_list) >= 2
            else ""
        )
        self.optimization_snapshot = OptimizationSnapshot(
            mode=label,
            frequency_hz=frequency_hz,
            value_1=value_1,
            value_2=value_2,
            difference=difference,
            curve_1_label=curve_1_label,
            curve_2_label=curve_2_label,
        )

        self.ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "グラフ生成エラー", message)

    def show_optimal_frequency(self) -> None:
        if len(self.curve_data_list) != 2:
            QMessageBox.warning(
                self,
                "最適周波数表示エラー",
                "最適周波数は、グラフ上の曲線が2本の場合のみ表示できます。",
            )
            return

        curve_1 = self.curve_data_list[0]
        curve_2 = self.curve_data_list[1]

        optimization_mode = str(
            self.optimal_frequency_mode_combo.currentData()
        )
        result: FrequencyOptimizationResult | OptimalFrequencyResult | None

        if optimization_mode == "opposite_sign":
            result = find_optimal_opposite_sign_frequency(
                curve_1.frequencies,
                curve_1.values,
                curve_2.values,
            )
        else:
            result = find_optimal_frequency(
                curve_1.frequencies,
                curve_1.values,
                curve_2.values,
            )

        if result is None:
            QMessageBox.warning(
                self,
                "最適周波数表示エラー",
                (
                    "符号分離条件を満たす周波数点が見つかりませんでした。\n\n"
                    "Re[K]1 と Re[K]2 が正負に分かれる周波数範囲が、"
                    "現在のグラフ内に存在しない可能性があります。"
                ),
            )
            return

        self._clear_optimal_markers()

        vertical_line = self.ax.axvline(
            result.frequency_hz,
            linestyle="--",
            linewidth=1.6,
            alpha=0.9,
            zorder=3.0,
            label="_nolegend_",
        )

        annotation = self.ax.annotate(
            (
                f"f_opt = {result.frequency_hz:.2e} Hz\n"
                f"|ΔRe[K]| = {result.difference:.3f}\n"
                f"Re[K]1 = {result.value_1:.3f}\n"
                f"Re[K]2 = {result.value_2:.3f}\n"
                f"mode = {optimization_mode}"
            ),
            xy=(result.frequency_hz, max(result.value_1, result.value_2)),
            xytext=(0.05, 0.05),
            textcoords="axes fraction",
            bbox={
                "boxstyle": "round",
                "facecolor": "white",
                "alpha": 0.8,
            },
        )

        self.optimal_marker_handles.extend([vertical_line, annotation])
        self.optimization_snapshot = OptimizationSnapshot(
            mode=optimization_mode,
            frequency_hz=result.frequency_hz,
            value_1=result.value_1,
            value_2=result.value_2,
            difference=result.difference,
            curve_1_label=curve_1.label,
            curve_2_label=curve_2.label,
        )
        self.ax.legend()
        self.canvas.draw()
