import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

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
