import math

import numpy as np
import pytest

from dep_cm_sim.dep_force import (
    calculate_gradient_from_vpp,
    create_direct_electric_field,
)
from dep_cm_sim.dep_force_sweep import calculate_dep_force_sweep


def calculate_example_sweep(
    *,
    f_min: float = 1.0,
    f_max: float = 1.0e10,
    num_points: int = 1000,
):
    return calculate_dep_force_sweep(
        f_min=f_min,
        f_max=f_max,
        num_points=num_points,
        membrane_capacitance=0.015,
        radius_m=6.7e-6,
        eps_c_relative=60.0,
        eps_s_relative=80.0,
        sigma_c=0.5,
        sigma_s=2.0e-4,
        electric_field=create_direct_electric_field(1.0e12),
    )


def test_calculate_dep_force_sweep_returns_requested_number_of_points() -> None:
    result = calculate_example_sweep(num_points=25)

    assert result.frequency_hz.shape == (25,)
    assert result.re_k_values.shape == (25,)
    assert result.force_n_values.shape == (25,)
    assert result.force_pn_values.shape == (25,)
    assert len(result.point_results) == 25


def test_calculate_dep_force_sweep_uses_logarithmic_frequency_spacing() -> None:
    result = calculate_example_sweep(
        f_min=1.0,
        f_max=1.0e4,
        num_points=5,
    )

    assert result.frequency_hz == pytest.approx(
        np.array([1.0, 10.0, 100.0, 1000.0, 10000.0])
    )


def test_calculate_dep_force_sweep_force_matches_re_k_sign() -> None:
    result = calculate_example_sweep()

    positive_mask = result.re_k_values > 0.0
    negative_mask = result.re_k_values < 0.0
    zero_mask = result.re_k_values == 0.0

    assert np.all(result.force_n_values[positive_mask] > 0.0)
    assert np.all(result.force_n_values[negative_mask] < 0.0)
    assert np.all(result.force_n_values[zero_mask] == 0.0)


def test_calculate_dep_force_sweep_converts_newtons_to_piconewtons() -> None:
    result = calculate_example_sweep(num_points=20)

    assert result.force_pn_values == pytest.approx(
        result.force_n_values * 1.0e12
    )


def test_calculate_dep_force_sweep_point_results_match_arrays() -> None:
    result = calculate_example_sweep(num_points=20)

    for index, point in enumerate(result.point_results):
        assert point.frequency_hz == pytest.approx(
            result.frequency_hz[index]
        )
        assert point.re_k == pytest.approx(result.re_k_values[index])
        assert point.force_n == pytest.approx(
            result.force_n_values[index]
        )
        assert point.force_pn == pytest.approx(
            result.force_pn_values[index]
        )


def test_calculate_dep_force_sweep_direct_and_vpp_modes_are_equivalent() -> None:
    common_arguments = {
        "f_min": 1.0,
        "f_max": 1.0e6,
        "num_points": 50,
        "membrane_capacitance": 0.015,
        "radius_m": 6.7e-6,
        "eps_c_relative": 60.0,
        "eps_s_relative": 80.0,
        "sigma_c": 0.5,
        "sigma_s": 2.0e-4,
    }

    direct_result = calculate_dep_force_sweep(
        **common_arguments,
        electric_field=create_direct_electric_field(1.0e12),
    )
    vpp_result = calculate_dep_force_sweep(
        **common_arguments,
        electric_field=calculate_gradient_from_vpp(
            voltage_vpp=2.0 * math.sqrt(2.0),
            gradient_factor_m_inv3=1.0e12,
        ),
    )

    assert vpp_result.force_n_values == pytest.approx(
        direct_result.force_n_values
    )


def test_calculate_dep_force_sweep_returns_crossover_results() -> None:
    result = calculate_example_sweep()

    assert len(result.crossover_results) >= 1

    for crossover in result.crossover_results:
        assert result.frequency_hz[0] <= crossover.frequency_hz
        assert crossover.frequency_hz <= result.frequency_hz[-1]


@pytest.mark.parametrize(
    ("keyword", "invalid_value", "message"),
    [
        ("f_min", 0.0, "最小周波数"),
        ("f_min", -1.0, "最小周波数"),
        ("f_min", math.nan, "最小周波数"),
        ("f_max", 0.0, "最大周波数"),
        ("f_max", math.inf, "最大周波数"),
        ("num_points", 1, "2以上"),
        ("num_points", 2.5, "整数"),
        ("num_points", True, "整数"),
    ],
)
def test_calculate_dep_force_sweep_rejects_invalid_sweep_conditions(
    keyword: str,
    invalid_value: float | int | bool,
    message: str,
) -> None:
    arguments = {
        "f_min": 1.0,
        "f_max": 1.0e10,
        "num_points": 1000,
        "membrane_capacitance": 0.015,
        "radius_m": 6.7e-6,
        "eps_c_relative": 60.0,
        "eps_s_relative": 80.0,
        "sigma_c": 0.5,
        "sigma_s": 2.0e-4,
        "electric_field": create_direct_electric_field(1.0e12),
    }
    arguments[keyword] = invalid_value

    with pytest.raises(ValueError, match=message):
        calculate_dep_force_sweep(**arguments)


def test_calculate_dep_force_sweep_rejects_reversed_frequency_range() -> None:
    with pytest.raises(ValueError, match="最大周波数"):
        calculate_example_sweep(
            f_min=1.0e6,
            f_max=1.0e3,
        )
