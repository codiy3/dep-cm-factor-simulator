from __future__ import annotations

import sys
from dataclasses import dataclass

import numpy as np
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QInputDialog,
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

from dep_cm_sim.cell_templates import (
    CellTemplate,
    delete_user_cell_template_by_name,
    find_cell_template_by_name,
    load_available_cell_templates,
    save_user_cell_template,
)
from dep_cm_sim.condition_optimizer import find_optimal_solution_conductivity
from dep_cm_sim.equations import calculate_cm_factor_real
from dep_cm_sim.error_evaluation import (
    evaluate_simulation_error,
    save_error_evaluation_result_to_csv,
)
from dep_cm_sim.experimental_data import load_experimental_data_from_csv
from dep_cm_sim.gui.experimental_data_window import ExperimentalDataWindow
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
        self.experimental_data_window: ExperimentalDataWindow | None = None
        self.cell_templates = load_available_cell_templates()

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

        template_layout = QGridLayout()

        template_label = QLabel("細胞テンプレート")
        template_layout.addWidget(template_label, 0, 0)

        self.cell_template_combo = QComboBox()
        self.refresh_cell_template_combo()
        template_layout.addWidget(self.cell_template_combo, 0, 1)

        apply_template_button = QPushButton("テンプレートを適用")
        apply_template_button.clicked.connect(self.apply_selected_cell_template)
        template_layout.addWidget(apply_template_button, 0, 2)

        save_template_button = QPushButton("現在の細胞パラメータをテンプレート保存")
        save_template_button.clicked.connect(self.save_current_cell_template)
        template_layout.addWidget(save_template_button, 1, 0, 1, 3)

        delete_template_button = QPushButton("選択中のユーザーテンプレートを削除")
        delete_template_button.clicked.connect(self.delete_selected_cell_template)
        template_layout.addWidget(delete_template_button, 2, 0, 1, 3)

        layout.addLayout(template_layout)

        optimizer_layout = QGridLayout()

        optimizer_title = QLabel("2細胞テンプレート間の最適溶液導電率探索")
        optimizer_layout.addWidget(optimizer_title, 0, 0, 1, 4)

        optimizer_layout.addWidget(QLabel("細胞テンプレート1"), 1, 0)
        self.optimizer_cell_1_combo = QComboBox()
        optimizer_layout.addWidget(self.optimizer_cell_1_combo, 1, 1)

        optimizer_layout.addWidget(QLabel("細胞テンプレート2"), 1, 2)
        self.optimizer_cell_2_combo = QComboBox()
        optimizer_layout.addWidget(self.optimizer_cell_2_combo, 1, 3)

        optimizer_layout.addWidget(QLabel("sigma_s 最小値 [S/m]"), 2, 0)
        self.optimizer_sigma_s_min_input = QLineEdit("1.0e-4")
        optimizer_layout.addWidget(self.optimizer_sigma_s_min_input, 2, 1)

        optimizer_layout.addWidget(QLabel("sigma_s 最大値 [S/m]"), 2, 2)
        self.optimizer_sigma_s_max_input = QLineEdit("1.0")
        optimizer_layout.addWidget(self.optimizer_sigma_s_max_input, 2, 3)

        optimizer_layout.addWidget(QLabel("sigma_s 探索点数"), 3, 0)
        self.optimizer_num_sigma_points_input = QLineEdit("20")
        optimizer_layout.addWidget(self.optimizer_num_sigma_points_input, 3, 1)

        optimizer_layout.addWidget(QLabel("最適化モード"), 3, 2)
        self.optimizer_mode_combo = QComboBox()
        self.optimizer_mode_combo.addItem("差分最大", "difference_only")
        self.optimizer_mode_combo.addItem("符号分離", "opposite_sign")
        optimizer_layout.addWidget(self.optimizer_mode_combo, 3, 3)

        optimize_button = QPushButton("最適な溶液導電率を探索")
        optimize_button.clicked.connect(self.optimize_solution_conductivity)
        optimizer_layout.addWidget(optimize_button, 4, 0, 1, 4)

        layout.addLayout(optimizer_layout)

        self.refresh_optimizer_template_combos()

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

        experimental_csv_button = QPushButton("実験データCSVを重ね描き")
        experimental_csv_button.clicked.connect(self.overlay_experimental_data_csv)
        button_layout.addWidget(experimental_csv_button, 3, 0, 1, 3)

        experimental_data_window_button = QPushButton("実験データ入力ウィンドウを開く")
        experimental_data_window_button.clicked.connect(self.open_experimental_data_window)
        button_layout.addWidget(experimental_data_window_button, 4, 0, 1, 3)

        error_evaluation_button = QPushButton("実験データCSVと現在のシミュレーションを誤差評価")
        error_evaluation_button.clicked.connect(self.evaluate_experimental_data_error)
        button_layout.addWidget(error_evaluation_button, 5, 0, 1, 3)

        layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

    def refresh_cell_template_combo(self) -> None:
        self.cell_template_combo.clear()

        for template in self.cell_templates:
            self.cell_template_combo.addItem(template.name)

        if hasattr(self, "optimizer_cell_1_combo") and hasattr(
            self,
            "optimizer_cell_2_combo",
        ):
            self.refresh_optimizer_template_combos()

    def refresh_optimizer_template_combos(self) -> None:
        self.optimizer_cell_1_combo.clear()
        self.optimizer_cell_2_combo.clear()

        for template in self.cell_templates:
            self.optimizer_cell_1_combo.addItem(template.name)
            self.optimizer_cell_2_combo.addItem(template.name)

        if self.optimizer_cell_2_combo.count() >= 2:
            self.optimizer_cell_2_combo.setCurrentIndex(1)

    def apply_selected_cell_template(self) -> None:
        template_name = self.cell_template_combo.currentText()
        template = find_cell_template_by_name(self.cell_templates, template_name)

        if template is None:
            QMessageBox.warning(
                self,
                "テンプレート適用エラー",
                f"選択されたテンプレートが見つかりません: {template_name}",
            )
            return

        self.input_widgets["membrane_capacitance"].setText(
            str(template.membrane_capacitance)
        )
        self.input_widgets["radius_m"].setText(str(template.radius_m))
        self.input_widgets["eps_c_relative"].setText(str(template.eps_c_relative))
        self.input_widgets["sigma_c"].setText(str(template.sigma_c))

        QMessageBox.information(
            self,
            "テンプレート適用完了",
            f"細胞テンプレートを適用しました。\\n\\nテンプレート名:\\n{template.name}",
        )

    def delete_selected_cell_template(self) -> None:
        template_name = self.cell_template_combo.currentText().strip()

        if not template_name:
            QMessageBox.warning(
                self,
                "テンプレート削除エラー",
                "削除するテンプレートが選択されていません。",
            )
            return

        if template_name == "reference_cell":
            QMessageBox.warning(
                self,
                "テンプレート削除エラー",
                "デフォルトテンプレート reference_cell は削除できません。",
            )
            return

        reply = QMessageBox.question(
            self,
            "テンプレート削除確認",
            f"ユーザー定義テンプレートを削除しますか？\n\nテンプレート名:\n{template_name}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_user_cell_template_by_name(template_name)
            self.cell_templates = load_available_cell_templates()
            self.refresh_cell_template_combo()

        except Exception as error:
            QMessageBox.critical(
                self,
                "テンプレート削除エラー",
                f"テンプレートを削除できませんでした。\n\n原因:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "テンプレート削除完了",
            f"ユーザー定義テンプレートを削除しました。\n\nテンプレート名:\n{template_name}",
        )

    def save_current_cell_template(self) -> None:
        template_name, ok = QInputDialog.getText(
            self,
            "細胞テンプレート保存",
            "テンプレート名を入力してください:",
        )

        if not ok:
            return

        template_name = template_name.strip()

        if not template_name:
            QMessageBox.warning(
                self,
                "テンプレート保存エラー",
                "テンプレート名を入力してください。",
            )
            return

        try:
            parameters = self.read_parameters()

            template = CellTemplate(
                name=template_name,
                membrane_capacitance=float(parameters["membrane_capacitance"]),
                radius_m=float(parameters["radius_m"]),
                eps_c_relative=float(parameters["eps_c_relative"]),
                sigma_c=float(parameters["sigma_c"]),
                description="User-defined cell parameter template",
            )

            save_user_cell_template(template)
            self.cell_templates = load_available_cell_templates()
            self.refresh_cell_template_combo()

            index = self.cell_template_combo.findText(template.name)
            if index >= 0:
                self.cell_template_combo.setCurrentIndex(index)

        except Exception as error:
            QMessageBox.critical(
                self,
                "テンプレート保存エラー",
                f"テンプレートを保存できませんでした。\n\n原因:\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "テンプレート保存完了",
            f"細胞テンプレートを保存しました。\n\nテンプレート名:\n{template_name}",
        )

    def optimize_solution_conductivity(self) -> None:
        cell_1_name = self.optimizer_cell_1_combo.currentText().strip()
        cell_2_name = self.optimizer_cell_2_combo.currentText().strip()

        cell_1 = find_cell_template_by_name(self.cell_templates, cell_1_name)
        cell_2 = find_cell_template_by_name(self.cell_templates, cell_2_name)

        if cell_1 is None or cell_2 is None:
            QMessageBox.warning(
                self,
                "最適化エラー",
                "選択された細胞テンプレートが見つかりません。",
            )
            return

        try:
            parameters = self.read_parameters()

            eps_s_relative = float(parameters["eps_s_relative"])
            f_min = float(parameters["f_min"])
            f_max = float(parameters["f_max"])
            num_frequency_points = int(parameters["num_points"])

            sigma_s_min = float(self.optimizer_sigma_s_min_input.text())
            sigma_s_max = float(self.optimizer_sigma_s_max_input.text())
            num_sigma_points = int(float(self.optimizer_num_sigma_points_input.text()))
            optimization_mode = self.optimizer_mode_combo.currentData()

            result = find_optimal_solution_conductivity(
                cell_1=cell_1,
                cell_2=cell_2,
                eps_s_relative=eps_s_relative,
                sigma_s_min=sigma_s_min,
                sigma_s_max=sigma_s_max,
                num_sigma_points=num_sigma_points,
                f_min=f_min,
                f_max=f_max,
                num_frequency_points=num_frequency_points,
                optimization_mode=optimization_mode,
            )

            frequency_hz = np.logspace(
                np.log10(f_min),
                np.log10(f_max),
                num_frequency_points,
            )

            values_1 = calculate_cm_factor_real(
                frequency_hz=frequency_hz,
                membrane_capacitance=cell_1.membrane_capacitance,
                radius_m=cell_1.radius_m,
                eps_c_relative=cell_1.eps_c_relative,
                eps_s_relative=eps_s_relative,
                sigma_c=cell_1.sigma_c,
                sigma_s=result.optimal_sigma_s,
            )
            values_2 = calculate_cm_factor_real(
                frequency_hz=frequency_hz,
                membrane_capacitance=cell_2.membrane_capacitance,
                radius_m=cell_2.radius_m,
                eps_c_relative=cell_2.eps_c_relative,
                eps_s_relative=eps_s_relative,
                sigma_c=cell_2.sigma_c,
                sigma_s=result.optimal_sigma_s,
            )

            graph_window = GraphWindow()
            graph_window.add_curve(
                frequency_hz,
                values_1,
                f"{cell_1.name} at sigma_s={result.optimal_sigma_s:.2e} S/m",
            )
            graph_window.add_curve(
                frequency_hz,
                values_2,
                f"{cell_2.name} at sigma_s={result.optimal_sigma_s:.2e} S/m",
            )
            graph_window.show_optimization_result_marker(
                frequency_hz=result.optimal_frequency_hz,
                value_1=result.value_1_at_optimum,
                value_2=result.value_2_at_optimum,
                difference=result.max_difference,
                label=result.optimization_mode,
            )
            graph_window.show()
            self.extra_graph_windows.append(graph_window)

        except Exception as error:
            QMessageBox.critical(
                self,
                "最適化エラー",
                f"最適な溶液導電率を探索できませんでした。\n\n原因:\n{error}",
            )
            return

        boundary_warning = ""
        if result.is_boundary_optimum:
            boundary_label = "下限" if result.boundary_side == "lower" else "上限"
            boundary_warning = (
                "\n\n注意: 最適 sigma_s が探索範囲の"
                f"{boundary_label}にあります。"
                "\n探索範囲を広げると、より良い条件が見つかる可能性があります。"
            )

        mode_label = (
            "符号分離"
            if result.optimization_mode == "opposite_sign"
            else "差分最大"
        )

        QMessageBox.information(
            self,
            "最適化完了",
            (
                "最適な溶液導電率を探索しました。\n\n"
                f"最適化モード: {mode_label}\n"
                f"細胞テンプレート1: {cell_1.name}\n"
                f"細胞テンプレート2: {cell_2.name}\n"
                f"最適 sigma_s: {result.optimal_sigma_s:.4e} S/m\n"
                f"最適周波数 f_opt: {result.optimal_frequency_hz:.4e} Hz\n"
                f"最大 |ΔRe[K]|: {result.max_difference:.4f}\n"
                f"{cell_1.name} Re[K]: {result.value_1_at_optimum:.4f}\n"
                f"{cell_2.name} Re[K]: {result.value_2_at_optimum:.4f}"
                f"{boundary_warning}"
            ),
        )

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

    def evaluate_experimental_data_error(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "誤差評価に使用する実験データCSVを読み込み",
            "",
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        try:
            parameters = self.read_parameters()
            experimental_data = load_experimental_data_from_csv(file_path)

            frequency_hz = np.logspace(
                np.log10(float(parameters["f_min"])),
                np.log10(float(parameters["f_max"])),
                int(parameters["num_points"]),
            )

            simulation_values = calculate_cm_factor_real(
                frequency_hz=frequency_hz,
                membrane_capacitance=float(parameters["membrane_capacitance"]),
                radius_m=float(parameters["radius_m"]),
                eps_c_relative=float(parameters["eps_c_relative"]),
                eps_s_relative=float(parameters["eps_s_relative"]),
                sigma_c=float(parameters["sigma_c"]),
                sigma_s=float(parameters["sigma_s"]),
            )

            result = evaluate_simulation_error(
                simulation_frequency_hz=frequency_hz,
                simulation_values=simulation_values,
                experimental_frequency_hz=experimental_data.frequency_hz,
                experimental_values=experimental_data.values,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "誤差評価エラー",
                f"誤差評価を実行できませんでした。\n\n原因:\n{error}",
            )
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "誤差評価結果CSVを保存",
            "outputs/error_evaluation_result.csv",
            "CSV files (*.csv)",
        )

        if save_path:
            try:
                save_error_evaluation_result_to_csv(result, save_path)
            except Exception as error:
                QMessageBox.critical(
                    self,
                    "誤差評価結果CSV保存エラー",
                    f"誤差評価結果CSVを保存できませんでした。\n\n原因:\n{error}",
                )
                return

        QMessageBox.information(
            self,
            "誤差評価完了",
            (
                "実験データと現在のシミュレーションを比較しました。\n\n"
                f"実験データ: {experimental_data.label}\n"
                f"評価点数: {result.num_points}\n"
                f"MAE: {result.mae:.6g}\n"
                f"RMSE: {result.rmse:.6g}\n"
                f"最大絶対誤差: {result.max_absolute_error:.6g}"
            ),
        )

    def open_experimental_data_window(self) -> None:
        if self.experimental_data_window is None:
            self.experimental_data_window = ExperimentalDataWindow(
                overlay_callback=self.overlay_experimental_data,
            )

        self.experimental_data_window.show()

    def overlay_experimental_data(self, experimental_data) -> None:  # noqa: ANN001
        if self.graph_window is None:
            self.graph_window = GraphWindow()

        self.graph_window.add_experimental_data(
            frequency_hz=experimental_data.frequency_hz,
            values=experimental_data.values,
            label=experimental_data.label,
            plot_style=experimental_data.plot_style,
        )
        self.graph_window.show()

    def overlay_experimental_data_csv(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "実験データCSVを読み込み",
            "",
            "CSV files (*.csv)",
        )

        if not file_path:
            return

        try:
            experimental_data = load_experimental_data_from_csv(file_path)

            self.overlay_experimental_data(experimental_data)

        except Exception as error:
            QMessageBox.critical(
                self,
                "実験データCSV読み込みエラー",
                f"実験データCSVを読み込めませんでした。\n\n原因:\n{error}",
            )

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
