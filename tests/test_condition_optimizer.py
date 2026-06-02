import numpy as np
import pytest

from dep_cm_sim.cell_templates import CellTemplate
from dep_cm_sim.condition_optimizer import (
    find_optimal_solution_conductivity,
    validate_solution_conductivity_optimization_inputs,
)


def make_cell_template(
    name: str,
    membrane_capacitance: float = 0.015,
    radius_m: float = 6.7e-6,
    eps_c_relative: float = 60.0,
    sigma_c: float = 0.5,
) -> CellTemplate:
    return CellTemplate(
        name=name,
        membrane_capacitance=membrane_capacitance,
        radius_m=radius_m,
        eps_c_relative=eps_c_relative,
        sigma_c=sigma_c,
    )


def test_find_optimal_solution_conductivity_returns_result() -> None:
    cell_1 = make_cell_template("cell_1")
    cell_2 = make_cell_template(
        "cell_2",
        membrane_capacitance=0.01,
        sigma_c=0.2,
    )

    result = find_optimal_solution_conductivity(
        cell_1=cell_1,
        cell_2=cell_2,
        eps_s_relative=80.0,
        sigma_s_min=1.0e-4,
        sigma_s_max=1.0,
        num_sigma_points=8,
        f_min=1.0,
        f_max=1.0e8,
        num_frequency_points=100,
    )

    assert 1.0e-4 <= result.optimal_sigma_s <= 1.0
    assert 1.0 <= result.optimal_frequency_hz <= 1.0e8
    assert result.max_difference >= 0.0
    assert len(result.sigma_s_candidates) == 8
    assert len(result.scores) == 8
    assert np.all(result.sigma_s_candidates > 0)
    assert np.all(result.scores >= 0)


def test_find_optimal_solution_conductivity_returns_zero_difference_for_same_cells() -> None:
    cell_1 = make_cell_template("cell_1")
    cell_2 = make_cell_template("cell_2")

    result = find_optimal_solution_conductivity(
        cell_1=cell_1,
        cell_2=cell_2,
        eps_s_relative=80.0,
        sigma_s_min=1.0e-4,
        sigma_s_max=1.0,
        num_sigma_points=5,
        f_min=1.0,
        f_max=1.0e6,
        num_frequency_points=50,
    )

    assert result.max_difference == pytest.approx(0.0)
    assert np.all(result.scores == pytest.approx(0.0))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"eps_s_relative": 0.0}, "eps_s_relative must be positive"),
        ({"sigma_s_min": 0.0}, "sigma_s_min must be positive"),
        ({"sigma_s_max": 1.0e-4}, "sigma_s_max must be greater"),
        ({"num_sigma_points": 1}, "num_sigma_points must be greater"),
        ({"f_min": 0.0}, "f_min must be positive"),
        ({"f_max": 1.0}, "f_max must be greater"),
        ({"num_frequency_points": 1}, "num_frequency_points must be greater"),
    ],
)
def test_validate_solution_conductivity_optimization_inputs_rejects_invalid_values(
    kwargs: dict[str, float | int],
    message: str,
) -> None:
    params: dict[str, float | int] = {
        "eps_s_relative": 80.0,
        "sigma_s_min": 1.0e-4,
        "sigma_s_max": 1.0,
        "num_sigma_points": 5,
        "f_min": 1.0,
        "f_max": 1.0e6,
        "num_frequency_points": 50,
    }
    params.update(kwargs)

    with pytest.raises(ValueError, match=message):
        validate_solution_conductivity_optimization_inputs(**params)
