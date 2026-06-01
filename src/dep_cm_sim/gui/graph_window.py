from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from numpy.typing import NDArray
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class GraphWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DEP CM Factor Simulator - Graph Window")
        self.resize(900, 700)

        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        central_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.canvas)

        button_layout = QHBoxLayout()

        save_button = QPushButton("PNG保存")
        save_button.clicked.connect(self.save_png)
        button_layout.addWidget(save_button)

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
        self._setup_axes()
        self.figure.tight_layout()
        self.canvas.draw()

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "グラフ生成エラー", message)
