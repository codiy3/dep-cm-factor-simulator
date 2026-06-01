from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy.typing import NDArray
from PySide6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget


class GraphWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DEP CM Factor Simulator - Graph Window")
        self.resize(900, 650)

        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
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
        self.ax.legend()
        self.figure.tight_layout()
        self.canvas.draw()

    def clear_graph(self) -> None:
        self.ax.clear()
        self._setup_axes()
        self.canvas.draw()

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "グラフ生成エラー", message)
