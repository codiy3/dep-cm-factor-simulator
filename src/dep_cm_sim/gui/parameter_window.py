from __future__ import annotations

import sys
from dataclasses import dataclass

import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dep_cm_sim.equations import calculate_cm_factor_real
from dep_cm_sim.gui.graph_window import GraphWindow
from dep_cm_sim.paper_conditions import PAPER_FIGURE_SIGMA_S_CONDITIONS
from dep_cm_sim.parameter_io import load_parameters_from_csv, save_parameters_to_csv


@dataclass(frozen=True)
class ParameterDefinition:
    key: str
    name: str
    symbol: str
    unit: str
    default_value: str
    relation: str
    value_type: str = "float"


PARAMETER_DEFINITIONS: list[ParameterDefinition] = [
    ParameterDefinition(
        key="graph_label",
        name="グラフラベル",
        symbol="label",
        unit="-",
        default_value="",
        relation="空欄の場合は sigma_s から自動生成",
        value_type="str",
    ),
    ParameterDefinition(
        key="membrane_capacitance",
        name="細胞膜容量",
        symbol="C_m",
        unit="F/m^2",
        default_value="0.015",
        relation="tau_ms = C_m r / sigma_s, tau_mc = C_m r / sigma_c",
    ),
    ParameterDefinition(
        key="radius_m",
        name="細胞半径",
        symbol="r",
        unit="m",
        default_value="6.7e-6",
        relation="HL60 cell radius",
    ),
    ParameterDefinition(
        key="eps_c_relative",
        name="細胞質の比誘電率",
        symbol="epsilon_c / epsilon_0",
        unit="-",
        default_value="60",
        relation="epsilon_c = epsilon_c_relative * epsilon_0",
    ),
    ParameterDefinition(
        key="eps_s_relative",
        name="溶液の比誘電率",
        symbol="epsilon_s / epsilon_0",
        unit="-",
        default_value="80",
        relation="epsilon_s = epsilon_s_relative * epsilon_0",
    ),
    ParameterDefinition(
        key="sigma_c",
        name="細胞質導電率",
        symbol="sigma_c",
        unit="S/m",
        default_value="0.5",
        relation="tau_c = epsilon_c / sigma_c",
    ),
    ParameterDefinition(
        key="sigma_s",
        name="溶液導電率",
        symbol="sigma_s",
        unit="S/m",
        default_value="2.0e-4",
        relation="tau_s = epsilon_s / sigma_s",
    ),
    ParameterDefinition(
        key="f_min",
        name="最小周波数",
        symbol="f_min",
        unit="Hz",
        default_value="1",
        relation="frequency lower bound",
    ),
    ParameterDefinition(
        key="f_max",
        name="最大周波数",
        symbol="f_max",
        unit="Hz",
        default_value="1.0e10",
        relation="frequency upper bound",
    ),
    ParameterDefinition(
        key="num_points",
        name="計算点数",
        symbol="N",
        unit="points",
        default_value="1000",
        relation="number of log-spaced frequency points",
        value_type="int",
    ),
]


class ParameterWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DEP CM Factor Simulator - Parameter Window")
        self.resize(1200, 650)

        self.input_widgets: dict[str, QLineEdit] = {}
        self.graph_window: GraphWindow | None = None
        self.extra_graph_windows: list[GraphWindow] = []

        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        title = QLabel("CM因子シミュレーション用パラメータ")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["パラメータ名", "記号", "単位", "値", "関係式・説明"])
        self.table.setRowCount(len(PARAMETER_DEFINITIONS))

        for row, parameter in enumerate(PARAMETER_DEFINITIONS):
            self.table.setItem(row, 0, QTableWidgetItem(parameter.name))
            self.table.setItem(row, 1, QTableWidgetItem(parameter.symbol))
            self.table.setItem(row, 2, QTableWidgetItem(parameter.unit))

            line_edit = QLineEdit(parameter.default_value)
            self.table.setCellWidget(row, 3, line_edit)
            self.input_widgets[parameter.key] = line_edit

            self.table.setItem(row, 4, QTableWidgetItem(parameter.relation))

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        button_layout = QGridLayout()

        read_button = QPushButton("入力値を読み取る")
        read_button.clicked.connect(self.print_parameters)
        button_layout.addWidget(read_button, 0, 0)

        overlay_button = QPushButton("現在のグラフに重ねる")
        overlay_button.clicked.connect(self.plot_on_current_graph)
        button_layout.addWidget(overlay_button, 0, 1)

        new_window_button = QPushButton("新しいWindowで表示")
        new_window_button.clicked.connect(self.plot_on_new_graph_window)
        button_layout.addWidget(new_window_button, 0, 2)

        save_csv_button = QPushButton("CSV保存")
        save_csv_button.clicked.connect(self.save_parameters_csv)
        button_layout.addWidget(save_csv_button, 1, 0)

        load_csv_button = QPushButton("CSV読み込み")
        load_csv_button.clicked.connect(self.load_parameters_csv)
        button_layout.addWidget(load_csv_button, 1, 1)

        reset_button = QPushButton("既定値に戻す")
        reset_button.clicked.connect(self.reset_parameters)
        button_layout.addWidget(reset_button, 1, 2)

        paper_figure_button = QPushButton("論文図(a)〜(h)を再現")
        paper_figure_button.clicked.connect(self.plot_paper_figure_reproduction)
        button_layout.addWidget(paper_figure_button, 2, 0, 1, 3)

        layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

    def read_parameters(self) -> dict[str, float | int | str]:
        parameters: dict[str, float | int | str] = {}

        for parameter in PARAMETER_DEFINITIONS:
            raw_value = self.input_widgets[parameter.key].text()

            if parameter.value_type == "str":
                parameters[parameter.key] = raw_value.strip()
            elif parameter.value_type == "int":
                parameters[parameter.key] = int(raw_value)
            else:
                parameters[parameter.key] = float(raw_value)

        return parameters

    def apply_parameters(self, parameters: dict[str, float | int | str]) -> None:
        for parameter in PARAMETER_DEFINITIONS:
            if parameter.key not in parameters:
                if parameter.key == "graph_label":
                    self.input_widgets[parameter.key].setText("")
                    continue
                raise ValueError(f"CSVに必要なパラメータがありません: {parameter.key}")

            self.input_widgets[parameter.key].setText(str(parameters[parameter.key]))

    def validate_parameters(self, parameters: dict[str, float | int | str]) -> None:
        f_min = float(parameters["f_min"])
        f_max = float(parameters["f_max"])
        num_points = int(parameters["num_points"])

        if f_min <= 0:
            raise ValueError("最小周波数 f_min は0より大きい値にしてください。")
        if f_max <= 0:
            raise ValueError("最大周波数 f_max は0より大きい値にしてください。")
        if f_min >= f_max:
            raise ValueError("最大周波数 f_max は最小周波数 f_min より大きい値にしてください。")
        if num_points < 2:
            raise ValueError("計算点数 N は2以上にしてください。")

    def calculate_curve(self) -> tuple[np.ndarray, np.ndarray, str]:
        parameters = self.read_parameters()
        self.validate_parameters(parameters)

        frequency_hz = np.logspace(
            np.log10(float(parameters["f_min"])),
            np.log10(float(parameters["f_max"])),
            int(parameters["num_points"]),
        )

        cm_factor_real = calculate_cm_factor_real(
            frequency_hz=frequency_hz,
            membrane_capacitance=float(parameters["membrane_capacitance"]),
            radius_m=float(parameters["radius_m"]),
            eps_c_relative=float(parameters["eps_c_relative"]),
            eps_s_relative=float(parameters["eps_s_relative"]),
            sigma_c=float(parameters["sigma_c"]),
            sigma_s=float(parameters["sigma_s"]),
        )

        graph_label = str(parameters["graph_label"]).strip()

        if graph_label:
            label = graph_label
        else:
            label = f"sigma_s={float(parameters['sigma_s']):.2e} S/m"

        return frequency_hz, cm_factor_real, label

    def plot_on_current_graph(self) -> None:
        try:
            frequency_hz, cm_factor_real, label = self.calculate_curve()

            if self.graph_window is None:
                self.graph_window = GraphWindow()

            self.graph_window.add_curve(frequency_hz, cm_factor_real, label)
            self.graph_window.show()

        except Exception as error:
            self.show_generation_error(error)

    def plot_on_new_graph_window(self) -> None:
        try:
            frequency_hz, cm_factor_real, label = self.calculate_curve()

            graph_window = GraphWindow()
            graph_window.add_curve(frequency_hz, cm_factor_real, label)
            graph_window.show()

            self.extra_graph_windows.append(graph_window)

        except Exception as error:
            self.show_generation_error(error)

    def plot_paper_figure_reproduction(self) -> None:
        try:
            parameters = self.read_parameters()
            self.validate_parameters(parameters)

            frequency_hz = np.logspace(
                np.log10(float(parameters["f_min"])),
                np.log10(float(parameters["f_max"])),
                int(parameters["num_points"]),
            )

            graph_window = GraphWindow()

            for paper_label, sigma_s in PAPER_FIGURE_SIGMA_S_CONDITIONS:
                cm_factor_real = calculate_cm_factor_real(
                    frequency_hz=frequency_hz,
                    membrane_capacitance=float(parameters["membrane_capacitance"]),
                    radius_m=float(parameters["radius_m"]),
                    eps_c_relative=float(parameters["eps_c_relative"]),
                    eps_s_relative=float(parameters["eps_s_relative"]),
                    sigma_c=float(parameters["sigma_c"]),
                    sigma_s=sigma_s,
                )

                label = f"{paper_label} sigma_s={sigma_s:.1e} S/m"
                graph_window.add_curve(frequency_hz, cm_factor_real, label)

            graph_window.show()
            self.extra_graph_windows.append(graph_window)

        except Exception as error:
            self.show_generation_error(error)

    def save_parameters_csv(self) -> None:
        try:
            parameters = self.read_parameters()
        except Exception as error:
            QMessageBox.critical(
                self,
                "CSV保存エラー",
                f"入力値を読み取れないため、CSV保存できませんでした。\n\n原因:\n{error}",
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "パラメータ条件をCSV保存",
            "outputs/parameters.csv",
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        try:
            save_parameters_to_csv(parameters, file_path)
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
            f"パラメータ条件をCSV保存しました。\n\n保存先:\n{file_path}",
        )

    def load_parameters_csv(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "パラメータ条件CSVを読み込み",
            "outputs",
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        try:
            parameters = load_parameters_from_csv(file_path)
            self.apply_parameters(parameters)
        except Exception as error:
            QMessageBox.critical(
                self,
                "CSV読み込みエラー",
                f"CSVを読み込めませんでした。\n\n原因:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "CSV読み込み完了",
            f"パラメータ条件を読み込みました。\n\n読み込み元:\n{file_path}",
        )

    def show_generation_error(self, error: Exception) -> None:
        QMessageBox.critical(
            self,
            "グラフ生成エラー",
            f"グラフを生成できませんでした。\n\n入力値または計算条件を確認してください。\n\n原因:\n{error}",
        )

    def print_parameters(self) -> None:
        try:
            parameters = self.read_parameters()
        except ValueError as error:
            print(f"入力値を読み取れませんでした: {error}")
            return

        print("現在の入力値:")
        for key, value in parameters.items():
            print(f"{key}: {value}")

    def reset_parameters(self) -> None:
        for parameter in PARAMETER_DEFINITIONS:
            self.input_widgets[parameter.key].setText(parameter.default_value)


def main() -> None:
    app = QApplication(sys.argv)
    window = ParameterWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
