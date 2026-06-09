from __future__ import annotations

from dataclasses import dataclass

from datetime import datetime
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from dep_cm_sim.condition_optimizer import find_optimal_opposite_sign_frequency
from dep_cm_sim.optimization import find_optimal_frequency
from matplotlib.figure import Figure
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


@dataclass
class CurveData:
    label: str
    frequencies: object
    values: object


class GraphWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DEP CM Factor Simulator - Graph Window")
        self.resize(900, 700)

        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.curve_data_list: list[CurveData] = []
        self.optimal_marker_handles: list[object] = []

        central_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.canvas)

        button_layout = QHBoxLayout()

        save_button = QPushButton("PNG保存")
        save_button.clicked.connect(self.save_png)
        button_layout.addWidget(save_button)

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
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_ylabel("Re[K]")
        self.ax.set_title("Real part of Clausius-Mossotti factor")
        self.ax.grid(True, which="both")
        self.ax.axhline(0.0, linewidth=1.0)

    def add_curve(
        self,
        frequency_hz: NDArray[np.float64],
        cm_factor_real: NDArray[np.float64],
        label: str,
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

        self.ax.plot(frequency_hz, cm_factor_real, label=label)
        self.curve_data_list.append(
            CurveData(
                label=label,
                frequencies=frequency_hz,
                values=cm_factor_real,
            )
        )
        self.ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def add_experimental_data(
        self,
        frequency_hz: NDArray[np.float64],
        values: NDArray[np.float64],
        label: str,
        plot_style: str = "scatter",
    ) -> None:
        if frequency_hz.size == 0:
            raise ValueError("frequency_hz must not be empty.")
        if values.size == 0:
            raise ValueError("values must not be empty.")
        if frequency_hz.shape != values.shape:
            raise ValueError("frequency_hz and values must have the same shape.")
        if np.isnan(frequency_hz).any():
            raise ValueError("frequency_hz must not contain NaN.")
        if np.any(frequency_hz <= 0):
            raise ValueError("frequency_hz must be positive.")
        if np.isnan(values).any():
            raise ValueError("values must not contain NaN.")
        if not label.strip():
            raise ValueError("label must not be empty.")
        if plot_style not in {"scatter", "line", "scatter_line"}:
            raise ValueError("plot_style must be scatter, line, or scatter_line.")

        legend_label = f"experimental: {label}"

        if plot_style == "scatter":
            self.ax.scatter(frequency_hz, values, label=legend_label)
        elif plot_style == "line":
            self.ax.plot(frequency_hz, values, label=legend_label)
        else:
            self.ax.plot(frequency_hz, values, marker="o", label=legend_label)
        self.ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

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
        for handle in self.optimal_marker_handles:
            try:
                handle.remove()
            except ValueError:
                pass
        self.optimal_marker_handles.clear()

        vertical_line = self.ax.axvline(
            frequency_hz,
            linestyle="--",
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

        optimization_mode = self.optimal_frequency_mode_combo.currentData()

        if optimization_mode == "opposite_sign":
            result = find_optimal_opposite_sign_frequency(
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
        else:
            result = find_optimal_frequency(
                curve_1.frequencies,
                curve_1.values,
                curve_2.values,
            )

        for handle in self.optimal_marker_handles:
            try:
                handle.remove()
            except ValueError:
                pass
        self.optimal_marker_handles.clear()

        vertical_line = self.ax.axvline(
            result.frequency_hz,
            linestyle="--",
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
        self.ax.legend()
        self.canvas.draw()

