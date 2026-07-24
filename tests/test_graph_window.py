import numpy as np
import pytest
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
)

from dep_cm_sim.csv_export import ParameterSnapshot
from dep_cm_sim.gui.graph_window import GraphWindow


@pytest.fixture(scope="module")
def application() -> QApplication:
    return QApplication.instance() or QApplication([])


@pytest.fixture
def graph_window(application: QApplication) -> GraphWindow:
    window = GraphWindow()
    yield window
    window.close()


EXPECTED_FREQUENCY_TICKS = np.logspace(
    0,
    10,
    11,
    dtype=np.float64,
)

EXPECTED_FREQUENCY_LABELS = [
    "1",
    "10",
    r"$10^{2}$",
    r"$10^{3}$",
    r"$10^{4}$",
    r"$10^{5}$",
    r"$10^{6}$",
    r"$10^{7}$",
    r"$10^{8}$",
    r"$10^{9}$",
    r"$10^{10}$",
]


def assert_frequency_axis(window: GraphWindow) -> None:
    window.canvas.draw()

    assert window.ax.get_xscale() == "log"
    assert window.ax.get_xlim() == pytest.approx((1.0, 1.0e10))
    assert window.ax.get_xticks(minor=False) == pytest.approx(
        EXPECTED_FREQUENCY_TICKS
    )
    tick_labels = window.ax.get_xticklabels()

    assert [label.get_text() for label in tick_labels] == EXPECTED_FREQUENCY_LABELS
    assert window.ax.get_xticks(minor=True).size == 0


def assert_grid_styles(window: GraphWindow) -> None:
    window.canvas.draw()

    x_major_gridline = window.ax.xaxis.get_major_ticks()[0].gridline
    y_major_gridline = window.ax.yaxis.get_major_ticks()[0].gridline

    assert window.ax.get_xscale() == "log"

    assert x_major_gridline.get_visible()
    assert x_major_gridline.get_linestyle() == "--"
    assert x_major_gridline.get_linewidth() == pytest.approx(0.8)
    assert x_major_gridline.get_alpha() == pytest.approx(0.5)

    assert window.ax.get_xticks(minor=True).size == 0

    assert y_major_gridline.get_visible()
    assert y_major_gridline.get_linestyle() == "--"
    assert y_major_gridline.get_linewidth() == pytest.approx(0.8)
    assert y_major_gridline.get_alpha() == pytest.approx(0.5)


def test_graph_window_configures_frequency_grid(
    graph_window: GraphWindow,
) -> None:
    assert_frequency_axis(graph_window)
    assert_grid_styles(graph_window)


def test_clear_graph_reapplies_grid_and_zero_line(
    graph_window: GraphWindow,
) -> None:
    graph_window.clear_graph()

    assert_frequency_axis(graph_window)
    assert_grid_styles(graph_window)

    assert len(graph_window.ax.lines) == 1
    zero_line = graph_window.ax.lines[0]

    assert zero_line.get_linestyle() == "-"
    assert zero_line.get_linewidth() == pytest.approx(1.2)
    assert zero_line.get_alpha() == pytest.approx(0.9)
    assert zero_line.get_zorder() == pytest.approx(1.5)
    assert zero_line.get_label() == "_nolegend_"


def test_add_curve_keeps_fixed_frequency_axis(
    graph_window: GraphWindow,
) -> None:
    frequencies = np.array([1.0e3, 1.0e4, 1.0e5], dtype=np.float64)
    values = np.array([0.1, 0.2, 0.3], dtype=np.float64)

    graph_window.add_curve(frequencies, values, "limited range")

    assert_frequency_axis(graph_window)


def test_crossover_and_optimal_markers_use_different_styles(
    graph_window: GraphWindow,
) -> None:
    frequencies = np.array([1.0, 10.0, 100.0], dtype=np.float64)
    values = np.array([-0.5, 0.0, 0.5], dtype=np.float64)

    graph_window.add_curve(frequencies, values, "curve")
    graph_window.show_optimization_result_marker(
        frequency_hz=10.0,
        value_1=-0.5,
        value_2=0.5,
        difference=1.0,
    )

    assert len(graph_window.crossover_marker_handles) == 1

    crossover_line = graph_window.crossover_marker_handles[0]
    optimal_line = graph_window.optimal_marker_handles[0]

    assert crossover_line.get_linestyle() == ":"
    assert crossover_line.get_linewidth() == pytest.approx(1.2)
    assert crossover_line.get_alpha() == pytest.approx(0.8)
    assert crossover_line.get_zorder() == pytest.approx(2.5)

    assert optimal_line.get_linestyle() == "--"
    assert optimal_line.get_linewidth() == pytest.approx(1.6)
    assert optimal_line.get_alpha() == pytest.approx(0.9)
    assert optimal_line.get_zorder() == pytest.approx(3.0)

    assert crossover_line.get_linestyle() != optimal_line.get_linestyle()



def test_add_curve_keeps_export_snapshot(
    graph_window: GraphWindow,
) -> None:
    frequencies = np.array([1.0, 10.0, 100.0], dtype=np.float64)
    values = np.array([-0.5, 0.0, 0.5], dtype=np.float64)
    parameters = (
        ParameterSnapshot(
            key="sigma_s",
            name="溶液導電率",
            value=2.0e-4,
            unit="S/m",
        ),
    )

    graph_window.add_curve(
        frequencies,
        values,
        "curve",
        parameters=parameters,
    )

    stored_curve = graph_window.curve_data_list[0]

    assert stored_curve.parameters == parameters
    assert stored_curve.crossover_frequencies_hz == pytest.approx((10.0,))

    frequencies[0] = 999.0
    values[0] = 999.0

    assert stored_curve.frequencies[0] == pytest.approx(1.0)
    assert stored_curve.values[0] == pytest.approx(-0.5)


def test_show_optimal_frequency_keeps_export_snapshot(
    graph_window: GraphWindow,
) -> None:
    frequencies = np.array([1.0, 10.0, 100.0], dtype=np.float64)
    values_1 = np.array([-0.4, 0.1, 0.3], dtype=np.float64)
    values_2 = np.array([0.4, -0.2, -0.1], dtype=np.float64)

    graph_window.add_curve(frequencies, values_1, "curve A")
    graph_window.add_curve(frequencies, values_2, "curve B")
    graph_window.show_optimal_frequency()

    snapshot = graph_window.optimization_snapshot

    assert snapshot is not None
    assert snapshot.mode == "difference_only"
    assert snapshot.curve_1_label == "curve A"
    assert snapshot.curve_2_label == "curve B"


def test_clear_graph_clears_csv_export_state(
    graph_window: GraphWindow,
) -> None:
    frequencies = np.array([1.0, 10.0, 100.0], dtype=np.float64)
    values_1 = np.array([-0.4, 0.1, 0.3], dtype=np.float64)
    values_2 = np.array([0.4, -0.2, -0.1], dtype=np.float64)

    graph_window.add_curve(frequencies, values_1, "curve A")
    graph_window.add_curve(frequencies, values_2, "curve B")
    graph_window.show_optimal_frequency()

    graph_window.clear_graph()

    assert graph_window.curve_data_list == []
    assert graph_window.optimization_snapshot is None
    assert graph_window.crossover_summaries == []


def test_save_csv_warns_when_no_curve_exists(
    graph_window: GraphWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    warnings: list[tuple[object, ...]] = []

    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args: warnings.append(args),
    )

    graph_window.save_csv()

    assert len(warnings) == 1
    assert "保存対象" in str(warnings[0])


def test_save_csv_creates_summary_and_curve_data_files(
    graph_window: GraphWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    frequencies = np.array([1.0, 10.0, 100.0], dtype=np.float64)
    values = np.array([-0.5, 0.0, 0.5], dtype=np.float64)
    base_path = tmp_path / "simulation.csv"

    graph_window.add_curve(frequencies, values, "curve")

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args: (str(base_path), "CSV files (*.csv)"),
    )
    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args: None,
    )

    graph_window.save_csv()

    assert (tmp_path / "simulation_summary.csv").exists()
    assert (tmp_path / "simulation_curve_data.csv").exists()


def test_add_curve_displays_re_k_metric_summary(
    graph_window: GraphWindow,
) -> None:
    frequencies = np.array(
        [1.0, 10.0, 100.0],
        dtype=np.float64,
    )
    values = np.array(
        [-0.5, 0.0, 0.75],
        dtype=np.float64,
    )
    parameters = (
        ParameterSnapshot(
            key="sigma_s",
            name="溶液導電率",
            value=2.0e-4,
            unit="S/m",
        ),
    )

    graph_window.add_curve(
        frequencies,
        values,
        "curve",
        parameters=parameters,
    )

    assert graph_window.crossover_info_handle is not None

    assert graph_window.crossover_info_handle.get_text() == (
        "Solution Cond: 0.200 mS/m\n"
        "Crossover Freq:\n"
        "  1: 10.000 Hz\n"
        "Re[K]_Max: 0.75000\n"
        "Re[K]_Min: -0.50000\n"
        "Re[K]_Magnitude: 1.2500"
    )
