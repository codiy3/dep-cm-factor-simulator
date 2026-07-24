import pytest
from PySide6.QtWidgets import QApplication

from dep_cm_sim.dep_force import create_direct_electric_field
from dep_cm_sim.dep_force_sweep import calculate_dep_force_sweep
from dep_cm_sim.gui.dep_force_sweep_window import (
    DepForceSweepWindow,
    build_dep_force_crossover_summary,
)


pytestmark = pytest.mark.usefixtures("qt_event_loop")


def create_sweep_result():
    return calculate_dep_force_sweep(
        f_min=1.0,
        f_max=1.0e10,
        num_points=1000,
        membrane_capacitance=0.015,
        radius_m=6.7e-6,
        eps_c_relative=60.0,
        eps_s_relative=80.0,
        sigma_c=0.5,
        sigma_s=2.0e-4,
        electric_field=create_direct_electric_field(1.0e12),
    )


def create_sweep_window() -> DepForceSweepWindow:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return DepForceSweepWindow()


def test_dep_force_sweep_window_creates_graph() -> None:
    window = create_sweep_window()

    try:
        assert window.windowTitle() == (
            "DEP CM Factor Simulator - DEP Force Frequency Sweep"
        )
        assert window.ax.get_xscale() == "log"
        assert window.ax.get_xlabel() == "Frequency [Hz]"
        assert window.ax.get_ylabel() == "F_DEP [pN]"
    finally:
        window.close()


def test_build_dep_force_crossover_summary_without_result() -> None:
    assert (
        build_dep_force_crossover_summary(())
        == "crossover frequency: 該当なし"
    )


def test_build_dep_force_crossover_summary_with_results() -> None:
    result = create_sweep_result()

    summary = build_dep_force_crossover_summary(
        result.crossover_results
    )

    assert "crossover frequency" in summary

    for crossover in result.crossover_results:
        assert f"{crossover.frequency_hz:.4e} Hz" in summary


def test_dep_force_sweep_window_displays_curve() -> None:
    window = create_sweep_window()
    result = create_sweep_result()

    try:
        window.update_result(
            result,
            label="sigma_s=2.00e-04 S/m",
        )

        assert window.current_result is result
        assert window.force_curve_handle is not None
        assert len(window.force_curve_handle.get_xdata()) == 1000
        assert len(window.force_curve_handle.get_ydata()) == 1000
    finally:
        window.close()


def test_dep_force_sweep_window_displays_crossover_markers() -> None:
    window = create_sweep_window()
    result = create_sweep_result()

    try:
        window.update_result(result, label="DEP force")

        assert len(window.crossover_marker_handles) == len(
            result.crossover_results
        )
        assert window.crossover_info_handle is not None
    finally:
        window.close()


def test_dep_force_sweep_window_update_replaces_previous_result() -> None:
    window = create_sweep_window()
    first_result = create_sweep_result()

    second_result = calculate_dep_force_sweep(
        f_min=1.0,
        f_max=1.0e8,
        num_points=100,
        membrane_capacitance=0.015,
        radius_m=6.7e-6,
        eps_c_relative=60.0,
        eps_s_relative=80.0,
        sigma_c=0.5,
        sigma_s=0.1,
        electric_field=create_direct_electric_field(2.0e12),
    )

    try:
        window.update_result(first_result, label="first")
        first_handle = window.force_curve_handle

        window.update_result(second_result, label="second")

        assert window.current_result is second_result
        assert window.force_curve_handle is not None
        assert window.force_curve_handle is not first_handle
        assert len(window.ax.lines) == (
            2 + len(second_result.crossover_results)
        )
    finally:
        window.close()


def test_dep_force_sweep_window_clear_resets_state() -> None:
    window = create_sweep_window()
    result = create_sweep_result()

    try:
        window.update_result(result, label="DEP force")
        window.clear_graph()

        assert window.current_result is None
        assert window.force_curve_handle is None
        assert window.crossover_marker_handles == []
        assert window.crossover_info_handle is None
        assert window.ax.get_xscale() == "log"
        assert window.ax.get_ylabel() == "F_DEP [pN]"
    finally:
        window.close()


def test_dep_force_sweep_window_rejects_empty_label() -> None:
    window = create_sweep_window()
    result = create_sweep_result()

    try:
        with pytest.raises(ValueError, match="ラベル"):
            window.update_result(result, label=" ")
    finally:
        window.close()
