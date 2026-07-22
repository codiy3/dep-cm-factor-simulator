from __future__ import annotations

import math
from collections.abc import Callable, Mapping

import numpy as np
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dep_cm_sim.dep_force import (
    DepForceResult,
    ElectricFieldMode,
    calculate_dep_force,
    calculate_gradient_from_vpp,
    create_direct_electric_field,
)
from dep_cm_sim.equations import calculate_cm_factor_real

ParameterProvider = Callable[[], Mapping[str, float | int | str]]


def format_dep_force_result(result: DepForceResult) -> str:
    """構造化されたDEP力計算結果をGUI表示用文字列へ変換する。"""

    electric_field = result.electric_field

    lines = [
        "DEP force calculation result",
        "",
        f"mode: {electric_field.mode.value}",
        f"frequency: {result.frequency_hz:.4e} Hz",
        f"Re[K]: {result.re_k:.6e}",
        f"epsilon_m: {result.epsilon_m_f_m:.6e} F/m",
        f"radius: {result.radius_m:.6e} m",
    ]

    if electric_field.mode is ElectricFieldMode.VPP_AND_FACTOR:
        voltage_vpp = electric_field.voltage_vpp
        voltage_peak = electric_field.voltage_peak
        voltage_rms = electric_field.voltage_rms
        gradient_factor = electric_field.gradient_factor_m_inv3

        if (
            voltage_vpp is None
            or voltage_peak is None
            or voltage_rms is None
            or gradient_factor is None
        ):
            raise ValueError("Vp-p方式の途中値が不足しています。")

        lines.extend(
            [
                f"Vp-p: {voltage_vpp:.6e} V",
                f"V_peak: {voltage_peak:.6e} V",
                f"V_rms: {voltage_rms:.6e} V",
                f"gradient_factor: {gradient_factor:.6e} m^-3",
            ]
        )

    lines.extend(
        [
            (
                "gradient of |E_rms|^2: "
                f"{electric_field.gradient_v2_m3:.6e} V^2/m^3"
            ),
            f"F_DEP: {result.force_n:.6e} N",
            f"F_DEP: {result.force_pn:.6e} pN",
            f"classification: {result.classification}",
            "",
            "注: 球形粒子・双極子近似によるスカラーDEP力です。",
            "三次元の力ベクトル方向を計算した結果ではありません。",
        ]
    )

    return "\n".join(lines)


class DepForceWindow(QWidget):
    """ParameterWindowの現在値を使ってDEP力を計算する専用ウィンドウ。"""

    def __init__(
        self,
        parameter_provider: ParameterProvider,
    ) -> None:
        super().__init__()

        self.parameter_provider = parameter_provider

        self.setWindowTitle("DEP CM Factor Simulator - DEP Force")
        self.resize(900, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("DEP力計算（RMS電場・スカラー力モデル）")
        layout.addWidget(title)

        parameter_note = QLabel(
            "細胞・溶液パラメータには、ParameterWindowの現在の入力値を使用します。"
        )
        parameter_note.setWordWrap(True)
        layout.addWidget(parameter_note)

        input_layout = QGridLayout()

        input_layout.addWidget(QLabel("計算周波数 [Hz]"), 0, 0)
        self.frequency_input = QLineEdit()
        self.frequency_input.setPlaceholderText("例: 1.0e5")
        input_layout.addWidget(self.frequency_input, 0, 1)

        input_layout.addWidget(QLabel("電場入力方式"), 0, 2)
        self.mode_combo = QComboBox()
        self.mode_combo.addItem(
            "電場勾配を直接入力",
            ElectricFieldMode.DIRECT_GRADIENT.value,
        )
        self.mode_combo.addItem(
            "Vp-pと変換係数から計算",
            ElectricFieldMode.VPP_AND_FACTOR.value,
        )
        self.mode_combo.currentIndexChanged.connect(
            self.update_input_state
        )
        input_layout.addWidget(self.mode_combo, 0, 3)

        input_layout.addWidget(
            QLabel("∇|E_rms|² [V²/m³]"),
            1,
            0,
        )
        self.direct_gradient_input = QLineEdit()
        self.direct_gradient_input.setPlaceholderText("例: 1.0e12")
        input_layout.addWidget(self.direct_gradient_input, 1, 1)

        input_layout.addWidget(QLabel("Vp-p [V]"), 1, 2)
        self.voltage_vpp_input = QLineEdit()
        self.voltage_vpp_input.setPlaceholderText("例: 10")
        input_layout.addWidget(self.voltage_vpp_input, 1, 3)

        input_layout.addWidget(
            QLabel("gradient factor [m⁻³]"),
            2,
            2,
        )
        self.gradient_factor_input = QLineEdit()
        self.gradient_factor_input.setPlaceholderText("例: 1.0e11")
        input_layout.addWidget(self.gradient_factor_input, 2, 3)

        electric_field_note = QLabel(
            "Vp-pだけでは電場勾配は決まりません。"
            "gradient factorにはFEM解析・校正値等を入力してください。"
        )
        electric_field_note.setWordWrap(True)
        input_layout.addWidget(electric_field_note, 2, 0, 1, 2)

        layout.addLayout(input_layout)

        action_layout = QGridLayout()

        self.calculate_button = QPushButton("DEP力を計算")
        self.calculate_button.clicked.connect(
            self.calculate_and_display_result
        )
        action_layout.addWidget(self.calculate_button, 0, 0)

        self.reset_button = QPushButton("DEP力入力をクリア")
        self.reset_button.clicked.connect(self.reset_inputs)
        action_layout.addWidget(self.reset_button, 0, 1)

        layout.addLayout(action_layout)

        self.result_output = QPlainTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText(
            "計算結果と途中値がここに表示されます。"
        )
        layout.addWidget(self.result_output)

        self.update_input_state()

    def update_input_state(self, _index: int = 0) -> None:
        """選択中の電場入力方式に合わせて入力欄を切り替える。"""

        mode = self.mode_combo.currentData()
        direct_mode = mode == ElectricFieldMode.DIRECT_GRADIENT.value

        self.direct_gradient_input.setEnabled(direct_mode)
        self.voltage_vpp_input.setEnabled(not direct_mode)
        self.gradient_factor_input.setEnabled(not direct_mode)

    @staticmethod
    def _read_finite_float(
        input_widget: QLineEdit,
        *,
        field_name: str,
    ) -> float:
        raw_value = input_widget.text().strip()

        if not raw_value:
            raise ValueError(f"{field_name}を入力してください。")

        try:
            value = float(raw_value)
        except ValueError as error:
            raise ValueError(
                f"{field_name}には数値を入力してください。"
            ) from error

        if not math.isfinite(value):
            raise ValueError(f"{field_name}は有限値にしてください。")

        return value

    def calculate_result(self) -> DepForceResult:
        """ParameterWindowの現在値と専用入力からDEP力を計算する。"""

        parameters = self.parameter_provider()

        frequency_hz = self._read_finite_float(
            self.frequency_input,
            field_name="計算周波数",
        )

        if frequency_hz <= 0.0:
            raise ValueError("計算周波数は0より大きい値にしてください。")

        mode = self.mode_combo.currentData()

        if mode == ElectricFieldMode.DIRECT_GRADIENT.value:
            gradient_v2_m3 = self._read_finite_float(
                self.direct_gradient_input,
                field_name="電場勾配 ∇|E_rms|²",
            )
            electric_field = create_direct_electric_field(
                gradient_v2_m3
            )

        elif mode == ElectricFieldMode.VPP_AND_FACTOR.value:
            voltage_vpp = self._read_finite_float(
                self.voltage_vpp_input,
                field_name="Vp-p",
            )
            gradient_factor_m_inv3 = self._read_finite_float(
                self.gradient_factor_input,
                field_name="gradient factor",
            )
            electric_field = calculate_gradient_from_vpp(
                voltage_vpp=voltage_vpp,
                gradient_factor_m_inv3=gradient_factor_m_inv3,
            )

        else:
            raise ValueError("電場入力方式を選択してください。")

        re_k_values = calculate_cm_factor_real(
            frequency_hz=np.array([frequency_hz], dtype=np.float64),
            membrane_capacitance=float(
                parameters["membrane_capacitance"]
            ),
            radius_m=float(parameters["radius_m"]),
            eps_c_relative=float(parameters["eps_c_relative"]),
            eps_s_relative=float(parameters["eps_s_relative"]),
            sigma_c=float(parameters["sigma_c"]),
            sigma_s=float(parameters["sigma_s"]),
        )

        if re_k_values.size != 1:
            raise ValueError(
                "指定周波数のRe[K]を1点で計算できませんでした。"
            )

        re_k = float(re_k_values[0])

        if not math.isfinite(re_k):
            raise ValueError(
                "指定周波数のRe[K]が有限値ではありません。"
            )

        return calculate_dep_force(
            frequency_hz=frequency_hz,
            re_k=re_k,
            eps_s_relative=float(parameters["eps_s_relative"]),
            radius_m=float(parameters["radius_m"]),
            electric_field=electric_field,
        )

    def calculate_and_display_result(self) -> None:
        """DEP力を計算し、途中値を含む結果を表示する。"""

        try:
            result = self.calculate_result()
            result_text = format_dep_force_result(result)
        except Exception as error:
            QMessageBox.critical(
                self,
                "DEP力計算エラー",
                (
                    "DEP力を計算できませんでした。\n\n"
                    "入力値または計算条件を確認してください。\n\n"
                    f"原因:\n{error}"
                ),
            )
            return

        self.result_output.setPlainText(result_text)

    def reset_inputs(self) -> None:
        """DEP力専用の入力値と表示結果を初期化する。"""

        self.frequency_input.clear()
        self.direct_gradient_input.clear()
        self.voltage_vpp_input.clear()
        self.gradient_factor_input.clear()
        self.mode_combo.setCurrentIndex(0)
        self.result_output.clear()
        self.update_input_state()
