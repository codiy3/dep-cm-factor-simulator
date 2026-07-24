import math

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication


from dep_cm_sim.dep_force import ElectricFieldMode
from dep_cm_sim.equations import calculate_cm_factor_real
from dep_cm_sim.gui.dep_force_window import (
    DepForceWindow,
    format_dep_force_result,
)


pytestmark = pytest.mark.usefixtures("qt_event_loop")


def make_parameters() -> dict[str, float | int | str]:
    return {
        "graph_label": "",
        "membrane_capacitance": 0.015,
        "radius_m": 6.7e-6,
        "eps_c_relative": 60.0,
        "eps_s_relative": 80.0,
        "sigma_c": 0.5,
        "sigma_s": 2.0e-4,
        "f_min": 1.0,
        "f_max": 1.0e10,
        "num_points": 1000,
    }


def create_dep_force_window(
    parameters: dict[str, float | int | str] | None = None,
) -> DepForceWindow:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    current_parameters = parameters or make_parameters()
    return DepForceWindow(
        parameter_provider=lambda: current_parameters,
    )


def test_dep_force_window_creates_required_widgets() -> None:
    window = create_dep_force_window()

    try:
        assert window.windowTitle() == (
            "DEP CM Factor Simulator - DEP Force"
        )
        assert window.mode_combo.count() == 2
        assert window.result_output.isReadOnly()
    finally:
        window.close()


def test_dep_force_window_direct_mode_enables_only_direct_input() -> None:
    window = create_dep_force_window()

    try:
        window.mode_combo.setCurrentIndex(0)

        assert (
            window.mode_combo.currentData()
            == ElectricFieldMode.DIRECT_GRADIENT.value
        )
        assert window.direct_gradient_input.isEnabled()
        assert not window.voltage_vpp_input.isEnabled()
        assert not window.gradient_factor_input.isEnabled()
    finally:
        window.close()


def test_dep_force_window_vpp_mode_enables_only_vpp_inputs() -> None:
    window = create_dep_force_window()

    try:
        window.mode_combo.setCurrentIndex(1)

        assert (
            window.mode_combo.currentData()
            == ElectricFieldMode.VPP_AND_FACTOR.value
        )
        assert not window.direct_gradient_input.isEnabled()
        assert window.voltage_vpp_input.isEnabled()
        assert window.gradient_factor_input.isEnabled()
    finally:
        window.close()


def test_dep_force_window_calculates_direct_force() -> None:
    window = create_dep_force_window()

    try:
        window.frequency_input.setText("1.0e5")
        window.direct_gradient_input.setText("1.0e12")

        result = window.calculate_result()

        expected_re_k = calculate_cm_factor_real(
            frequency_hz=np.array([1.0e5], dtype=np.float64),
            membrane_capacitance=0.015,
            radius_m=6.7e-6,
            eps_c_relative=60.0,
            eps_s_relative=80.0,
            sigma_c=0.5,
            sigma_s=2.0e-4,
        )[0]

        assert result.re_k == pytest.approx(expected_re_k)
        assert result.force_n == pytest.approx(1.309063e-12)
        assert result.classification == "pDEP"
    finally:
        window.close()


def test_dep_force_window_direct_and_vpp_modes_are_equivalent() -> None:
    window = create_dep_force_window()

    try:
        window.frequency_input.setText("1.0e5")

        window.mode_combo.setCurrentIndex(0)
        window.direct_gradient_input.setText("1.0e12")
        direct_result = window.calculate_result()

        window.mode_combo.setCurrentIndex(1)
        window.voltage_vpp_input.setText(
            str(2.0 * math.sqrt(2.0))
        )
        window.gradient_factor_input.setText("1.0e12")
        vpp_result = window.calculate_result()

        assert vpp_result.electric_field.voltage_rms == pytest.approx(
            1.0
        )
        assert vpp_result.force_n == pytest.approx(
            direct_result.force_n
        )
    finally:
        window.close()


def test_dep_force_window_uses_current_provider_values() -> None:
    parameters = make_parameters()
    window = create_dep_force_window(parameters)

    try:
        window.frequency_input.setText("1.0e5")
        window.direct_gradient_input.setText("1.0e12")

        first_result = window.calculate_result()

        parameters["radius_m"] = 2.0 * float(
            parameters["radius_m"]
        )
        second_result = window.calculate_result()

        assert second_result.force_n == pytest.approx(
            8.0 * first_result.force_n
        )
    finally:
        window.close()


def test_dep_force_window_displays_result() -> None:
    window = create_dep_force_window()

    try:
        window.frequency_input.setText("1.0e5")
        window.direct_gradient_input.setText("1.0e12")

        window.calculate_and_display_result()
        output_text = window.result_output.toPlainText()

        assert "mode: direct_gradient" in output_text
        assert "Re[K]:" in output_text
        assert "F_DEP:" in output_text
        assert "classification: pDEP" in output_text
    finally:
        window.close()


def test_format_dep_force_result_contains_vpp_intermediate_values() -> None:
    window = create_dep_force_window()

    try:
        window.mode_combo.setCurrentIndex(1)
        window.frequency_input.setText("1.0e5")
        window.voltage_vpp_input.setText(
            str(2.0 * math.sqrt(2.0))
        )
        window.gradient_factor_input.setText("1.0e12")

        result_text = format_dep_force_result(
            window.calculate_result()
        )

        assert "Vp-p:" in result_text
        assert "V_peak:" in result_text
        assert "V_rms:" in result_text
        assert "gradient_factor:" in result_text
    finally:
        window.close()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("frequency", "", "計算周波数を入力してください"),
        ("frequency", "abc", "計算周波数には数値"),
        ("frequency", "nan", "計算周波数は有限値"),
        ("frequency", "0", "計算周波数は0より大きい値"),
        ("gradient", "", "電場勾配"),
        ("gradient", "-1", "0以上"),
    ],
)
def test_dep_force_window_rejects_invalid_direct_inputs(
    field: str,
    value: str,
    message: str,
) -> None:
    window = create_dep_force_window()

    try:
        window.frequency_input.setText("1.0e5")
        window.direct_gradient_input.setText("1.0e12")

        if field == "frequency":
            window.frequency_input.setText(value)
        else:
            window.direct_gradient_input.setText(value)

        with pytest.raises(ValueError, match=message):
            window.calculate_result()
    finally:
        window.close()


def test_dep_force_window_reset_clears_only_dep_inputs() -> None:
    window = create_dep_force_window()

    try:
        window.mode_combo.setCurrentIndex(1)
        window.frequency_input.setText("1.0e5")
        window.direct_gradient_input.setText("1.0e12")
        window.voltage_vpp_input.setText("10")
        window.gradient_factor_input.setText("1.0e11")
        window.result_output.setPlainText("result")

        window.reset_inputs()

        assert window.frequency_input.text() == ""
        assert window.direct_gradient_input.text() == ""
        assert window.voltage_vpp_input.text() == ""
        assert window.gradient_factor_input.text() == ""
        assert window.result_output.toPlainText() == ""
        assert window.mode_combo.currentIndex() == 0
        assert window.direct_gradient_input.isEnabled()
        assert not window.voltage_vpp_input.isEnabled()
        assert not window.gradient_factor_input.isEnabled()
    finally:
        window.close()


def test_dep_force_window_creates_frequency_sweep_button() -> None:
    window = create_dep_force_window()

    try:
        assert (
            window.sweep_button.text()
            == "DEP力の周波数掃引グラフを表示"
        )
    finally:
        window.close()


def test_dep_force_window_calculates_frequency_sweep() -> None:
    window = create_dep_force_window()

    try:
        window.direct_gradient_input.setText("1.0e12")

        result = window.calculate_frequency_sweep_result()

        assert result.frequency_hz.size == 1000
        assert result.frequency_hz[0] == pytest.approx(1.0)
        assert result.frequency_hz[-1] == pytest.approx(1.0e10)
        assert result.force_pn_values.size == 1000
    finally:
        window.close()


def test_dep_force_window_frequency_sweep_uses_current_provider_values() -> None:
    parameters = make_parameters()
    window = create_dep_force_window(parameters)

    try:
        window.direct_gradient_input.setText("1.0e12")
        first_result = window.calculate_frequency_sweep_result()

        parameters["f_min"] = 10.0
        parameters["f_max"] = 1.0e6
        parameters["num_points"] = 25

        second_result = window.calculate_frequency_sweep_result()

        assert first_result.frequency_hz.size == 1000
        assert second_result.frequency_hz.size == 25
        assert second_result.frequency_hz[0] == pytest.approx(10.0)
        assert second_result.frequency_hz[-1] == pytest.approx(1.0e6)
    finally:
        window.close()
        if window.sweep_window is not None:
            window.sweep_window.close()


def test_dep_force_window_shows_frequency_sweep_window() -> None:
    window = create_dep_force_window()

    try:
        window.direct_gradient_input.setText("1.0e12")
        window.calculate_and_show_frequency_sweep()

        assert window.sweep_window is not None
        assert window.sweep_window.current_result is not None
        assert window.sweep_window.isVisible()
    finally:
        if window.sweep_window is not None:
            window.sweep_window.close()
        window.close()


def test_dep_force_window_reuses_frequency_sweep_window() -> None:
    window = create_dep_force_window()

    try:
        window.direct_gradient_input.setText("1.0e12")
        window.calculate_and_show_frequency_sweep()
        first_window = window.sweep_window

        window.direct_gradient_input.setText("2.0e12")
        window.calculate_and_show_frequency_sweep()

        assert window.sweep_window is first_window
    finally:
        if window.sweep_window is not None:
            window.sweep_window.close()
        window.close()


def test_dep_force_window_reset_does_not_close_sweep_window() -> None:
    window = create_dep_force_window()

    try:
        window.direct_gradient_input.setText("1.0e12")
        window.calculate_and_show_frequency_sweep()

        assert window.sweep_window is not None

        window.reset_inputs()

        assert window.sweep_window is not None
        assert window.sweep_window.current_result is not None
    finally:
        if window.sweep_window is not None:
            window.sweep_window.close()
        window.close()


def test_dep_force_window_uses_engineering_unit_for_sweep_label() -> None:
    window = create_dep_force_window()

    try:
        window.direct_gradient_input.setText("1.0e12")
        window.calculate_and_show_frequency_sweep()

        assert window.sweep_window is not None

        legend = window.sweep_window.ax.get_legend()
        assert legend is not None
        assert [text.get_text() for text in legend.get_texts()] == [
            "sigma_s=0.20000 mS/m"
        ]
    finally:
        if window.sweep_window is not None:
            window.sweep_window.close()
        window.close()
