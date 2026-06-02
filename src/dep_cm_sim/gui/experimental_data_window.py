from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dep_cm_sim.experimental_data import (
    ExperimentalData,
    load_experimental_data_from_csv,
    save_experimental_data_to_csv,
)


class ExperimentalDataWindow(QWidget):
    def __init__(
        self,
        overlay_callback: Callable[[ExperimentalData], None],
    ) -> None:
        super().__init__()

        self.overlay_callback = overlay_callback

        self.setWindowTitle("DEP CM Factor Simulator - Experimental Data")
        self.resize(800, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("実験データ入力")
        layout.addWidget(title)

        metadata_layout = QGridLayout()

        metadata_layout.addWidget(QLabel("ラベル"), 0, 0)
        self.label_input = QLineEdit("experiment")
        metadata_layout.addWidget(self.label_input, 0, 1)

        metadata_layout.addWidget(QLabel("表示形式"), 0, 2)
        self.plot_style_combo = QComboBox()
        self.plot_style_combo.addItem("点のみ", "scatter")
        self.plot_style_combo.addItem("線のみ", "line")
        self.plot_style_combo.addItem("点＋線", "scatter_line")
        metadata_layout.addWidget(self.plot_style_combo, 0, 3)

        layout.addLayout(metadata_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["frequency_hz", "value"])
        self.table.setRowCount(5)
        layout.addWidget(self.table)

        table_button_layout = QHBoxLayout()

        add_row_button = QPushButton("行を追加")
        add_row_button.clicked.connect(self.add_row)
        table_button_layout.addWidget(add_row_button)

        remove_row_button = QPushButton("選択行を削除")
        remove_row_button.clicked.connect(self.remove_selected_rows)
        table_button_layout.addWidget(remove_row_button)

        layout.addLayout(table_button_layout)

        action_button_layout = QGridLayout()

        save_button = QPushButton("実験データCSV保存")
        save_button.clicked.connect(self.save_csv)
        action_button_layout.addWidget(save_button, 0, 0)

        load_button = QPushButton("実験データCSV読み込み")
        load_button.clicked.connect(self.load_csv)
        action_button_layout.addWidget(load_button, 0, 1)

        overlay_button = QPushButton("グラフに重ね描き")
        overlay_button.clicked.connect(self.overlay_to_graph)
        action_button_layout.addWidget(overlay_button, 0, 2)

        layout.addLayout(action_button_layout)

    def add_row(self) -> None:
        self.table.insertRow(self.table.rowCount())

    def remove_selected_rows(self) -> None:
        selected_rows = sorted(
            {index.row() for index in self.table.selectedIndexes()},
            reverse=True,
        )

        for row in selected_rows:
            self.table.removeRow(row)

    def read_experimental_data(self) -> ExperimentalData:
        frequencies: list[float] = []
        values: list[float] = []

        for row in range(self.table.rowCount()):
            frequency_item = self.table.item(row, 0)
            value_item = self.table.item(row, 1)

            frequency_text = frequency_item.text().strip() if frequency_item else ""
            value_text = value_item.text().strip() if value_item else ""

            if not frequency_text and not value_text:
                continue

            if not frequency_text or not value_text:
                raise ValueError(
                    f"Row {row + 1}: frequency_hz and value must both be filled."
                )

            try:
                frequency = float(frequency_text)
                value = float(value_text)
            except ValueError as error:
                raise ValueError(f"Row {row + 1}: values must be numeric.") from error

            frequencies.append(frequency)
            values.append(value)

        return ExperimentalData(
            frequency_hz=np.array(frequencies, dtype=np.float64),
            values=np.array(values, dtype=np.float64),
            label=self.label_input.text().strip(),
            plot_style=str(self.plot_style_combo.currentData()),
        )

    def set_experimental_data(self, data: ExperimentalData) -> None:
        self.label_input.setText(data.label)

        index = self.plot_style_combo.findData(data.plot_style)
        if index >= 0:
            self.plot_style_combo.setCurrentIndex(index)

        self.table.setRowCount(len(data.frequency_hz))

        for row, (frequency, value) in enumerate(
            zip(data.frequency_hz, data.values, strict=True)
        ):
            self.table.setItem(row, 0, QTableWidgetItem(str(frequency)))
            self.table.setItem(row, 1, QTableWidgetItem(str(value)))

    def save_csv(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "実験データCSVを保存",
            str(Path("outputs") / "experimental_data.csv"),
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        save_path = Path(file_path)
        if save_path.suffix.lower() != ".csv":
            save_path = save_path.with_suffix(".csv")

        try:
            data = self.read_experimental_data()
            save_experimental_data_to_csv(data, save_path)
        except Exception as error:
            QMessageBox.critical(
                self,
                "実験データCSV保存エラー",
                f"実験データCSVを保存できませんでした。\n\n原因:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "実験データCSV保存完了",
            f"実験データCSVを保存しました。\n\n保存先:\n{save_path}",
        )

    def load_csv(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "実験データCSVを読み込み",
            "",
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        try:
            data = load_experimental_data_from_csv(file_path)
            self.set_experimental_data(data)
        except Exception as error:
            QMessageBox.critical(
                self,
                "実験データCSV読み込みエラー",
                f"実験データCSVを読み込めませんでした。\n\n原因:\n{error}",
            )

    def overlay_to_graph(self) -> None:
        try:
            data = self.read_experimental_data()
            self.overlay_callback(data)
        except Exception as error:
            QMessageBox.critical(
                self,
                "実験データ重ね描きエラー",
                f"実験データをグラフに重ね描きできませんでした。\n\n原因:\n{error}",
            )
