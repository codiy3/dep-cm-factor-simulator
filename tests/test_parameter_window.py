import pytest

from dep_cm_sim.gui.parameter_window import (
    PARAMETER_DEFINITIONS,
    build_parameter_snapshots,
)


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

    # 元のParameterWindow入力値は変更しない。
    assert parameters["radius_m"] != pytest.approx(9.9e-6)
    assert parameters["sigma_s"] != pytest.approx(0.1)


def test_build_parameter_snapshots_rejects_missing_parameter() -> None:
    parameters = make_parameters()
    del parameters["sigma_s"]

    with pytest.raises(ValueError, match="sigma_s"):
        build_parameter_snapshots(parameters)
