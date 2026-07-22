import pytest
from PySide6.QtWidgets import QApplication


from dep_cm_sim.gui.parameter_window import (
    PARAMETER_DEFINITIONS,
    ParameterWindow,
    build_parameter_snapshots,
)


pytestmark = pytest.mark.usefixtures("qt_event_loop")


def make_parameters() -> dict[str, float | int | str]:
    parameters: dict[str, float | int | str] = {}

    for definition in PARAMETER_DEFINITIONS:
        if definition.value_type == "str":
            parameters[definition.key] = "curve label"
        elif definition.value_type == "int":
            parameters[definition.key] = int(definition.default_value)
        else:
            parameters[definition.key] = float(definition.default_value)

    return parameters


def create_parameter_window() -> ParameterWindow:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return ParameterWindow()


def test_build_parameter_snapshots_uses_existing_definitions() -> None:
    parameters = make_parameters()

    snapshots = build_parameter_snapshots(parameters)

    expected_definitions = [
        definition
        for definition in PARAMETER_DEFINITIONS
        if definition.key != "graph_label"
    ]

    assert [snapshot.key for snapshot in snapshots] == [
        definition.key for definition in expected_definitions
    ]
    assert [snapshot.name for snapshot in snapshots] == [
        definition.name for definition in expected_definitions
    ]
    assert [snapshot.unit for snapshot in snapshots] == [
        definition.unit for definition in expected_definitions
    ]


def test_build_parameter_snapshots_applies_curve_specific_overrides() -> None:
    parameters = make_parameters()

    snapshots = build_parameter_snapshots(
        parameters,
        overrides={
            "radius_m": 9.9e-6,
            "sigma_s": 0.1,
        },
    )

    values = {snapshot.key: snapshot.value for snapshot in snapshots}

    assert values["radius_m"] == pytest.approx(9.9e-6)
    assert values["sigma_s"] == pytest.approx(0.1)

    assert parameters["radius_m"] != pytest.approx(9.9e-6)
    assert parameters["sigma_s"] != pytest.approx(0.1)


def test_build_parameter_snapshots_rejects_missing_parameter() -> None:
    parameters = make_parameters()
    del parameters["sigma_s"]

    with pytest.raises(ValueError, match="sigma_s"):
        build_parameter_snapshots(parameters)


def test_parameter_window_contains_only_dep_force_window_button() -> None:
    window = create_parameter_window()

    try:
        assert window.dep_force_window_button.text() == (
            "DEP力計算ウィンドウを開く"
        )
        assert window.dep_force_window is None

        assert not hasattr(window, "dep_force_group")
        assert not hasattr(window, "dep_frequency_input")
        assert not hasattr(window, "dep_force_result_output")
    finally:
        window.close()


def test_parameter_window_restores_original_size() -> None:
    window = create_parameter_window()

    try:
        assert window.size().width() == 1200
        assert window.size().height() == 650
    finally:
        window.close()


def test_parameter_window_opens_dep_force_window() -> None:
    window = create_parameter_window()

    try:
        window.open_dep_force_window()

        assert window.dep_force_window is not None
        assert window.dep_force_window.isVisible()
        assert window.dep_force_window.parameter_provider() == (
            window.read_parameters()
        )
    finally:
        if window.dep_force_window is not None:
            window.dep_force_window.close()
        window.close()


def test_parameter_window_reuses_dep_force_window() -> None:
    window = create_parameter_window()

    try:
        window.open_dep_force_window()
        first_window = window.dep_force_window

        window.open_dep_force_window()

        assert window.dep_force_window is first_window
    finally:
        if window.dep_force_window is not None:
            window.dep_force_window.close()
        window.close()


def test_dep_force_window_provider_reads_latest_parameter_values() -> None:
    window = create_parameter_window()

    try:
        window.open_dep_force_window()

        assert window.dep_force_window is not None

        window.input_widgets["radius_m"].setText("9.9e-6")
        parameters = window.dep_force_window.parameter_provider()

        assert float(parameters["radius_m"]) == pytest.approx(9.9e-6)
    finally:
        if window.dep_force_window is not None:
            window.dep_force_window.close()
        window.close()


def test_dep_force_window_does_not_change_parameter_snapshot_schema() -> None:
    window = create_parameter_window()

    try:
        window.open_dep_force_window()

        parameters = window.read_parameters()
        snapshots = build_parameter_snapshots(parameters)

        assert len(PARAMETER_DEFINITIONS) == 10
        assert len(snapshots) == 9
        assert all(
            not snapshot.key.startswith("dep_")
            for snapshot in snapshots
        )
    finally:
        if window.dep_force_window is not None:
            window.dep_force_window.close()
        window.close()
