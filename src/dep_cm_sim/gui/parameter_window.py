from __future__ import annotations

import sys
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class ParameterDefinition:
    key: str
    name: str
    symbol: str
    unit: str
    default_value: str
    relation: str


PARAMETER_DEFINITIONS: list[ParameterDefinition] = [
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
    ),
]


class ParameterWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("DEP CM Factor Simulator - Parameter Window")
        self.resize(1100, 500)

        self.input_widgets: dict[str, QLineEdit] = {}

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

        reset_button = QPushButton("既定値に戻す")
        reset_button.clicked.connect(self.reset_parameters)
        button_layout.addWidget(reset_button, 0, 1)

        layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

    def read_parameters(self) -> dict[str, float | int]:
        parameters: dict[str, float | int] = {}

        for parameter in PARAMETER_DEFINITIONS:
            raw_value = self.input_widgets[parameter.key].text()

            if parameter.key == "num_points":
                parameters[parameter.key] = int(raw_value)
            else:
                parameters[parameter.key] = float(raw_value)

        return parameters

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
