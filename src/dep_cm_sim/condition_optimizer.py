from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from dep_cm_sim.cell_templates import CellTemplate
from dep_cm_sim.equations import calculate_cm_factor_real
from dep_cm_sim.optimization import find_optimal_frequency


@dataclass(frozen=True)
class SolutionConductivityOptimizationResult:
    optimal_sigma_s: float
    optimal_frequency_hz: float
    max_difference: float
    value_1_at_optimum: float
    value_2_at_optimum: float
    sigma_s_candidates: NDArray[np.float64]
    scores: NDArray[np.float64]


def find_optimal_solution_conductivity(
    cell_1: CellTemplate,
    cell_2: CellTemplate,
    eps_s_relative: float,
    sigma_s_min: float,
    sigma_s_max: float,
    num_sigma_points: int,
    f_min: float,
    f_max: float,
    num_frequency_points: int,
) -> SolutionConductivityOptimizationResult:
    validate_solution_conductivity_optimization_inputs(
        eps_s_relative=eps_s_relative,
        sigma_s_min=sigma_s_min,
        sigma_s_max=sigma_s_max,
        num_sigma_points=num_sigma_points,
        f_min=f_min,
        f_max=f_max,
        num_frequency_points=num_frequency_points,
    )

    sigma_s_candidates = np.logspace(
        np.log10(sigma_s_min),
        np.log10(sigma_s_max),
        num_sigma_points,
    )
    frequency_hz = np.logspace(
        np.log10(f_min),
        np.log10(f_max),
        num_frequency_points,
    )

    scores = np.empty(num_sigma_points, dtype=np.float64)
    best_result_index = 0
    best_frequency_hz = 0.0
    best_value_1 = 0.0
    best_value_2 = 0.0
    best_difference = -1.0

    for index, sigma_s in enumerate(sigma_s_candidates):
        values_1 = calculate_cm_factor_real(
            frequency_hz=frequency_hz,
            membrane_capacitance=cell_1.membrane_capacitance,
            radius_m=cell_1.radius_m,
            eps_c_relative=cell_1.eps_c_relative,
            eps_s_relative=eps_s_relative,
            sigma_c=cell_1.sigma_c,
            sigma_s=float(sigma_s),
        )
        values_2 = calculate_cm_factor_real(
            frequency_hz=frequency_hz,
            membrane_capacitance=cell_2.membrane_capacitance,
            radius_m=cell_2.radius_m,
            eps_c_relative=cell_2.eps_c_relative,
            eps_s_relative=eps_s_relative,
            sigma_c=cell_2.sigma_c,
            sigma_s=float(sigma_s),
        )

        optimal_frequency_result = find_optimal_frequency(
            frequency_hz,
            values_1,
            values_2,
        )

        scores[index] = optimal_frequency_result.difference

        if optimal_frequency_result.difference > best_difference:
            best_result_index = index
            best_frequency_hz = optimal_frequency_result.frequency_hz
            best_value_1 = optimal_frequency_result.value_1
            best_value_2 = optimal_frequency_result.value_2
            best_difference = optimal_frequency_result.difference

    return SolutionConductivityOptimizationResult(
        optimal_sigma_s=float(sigma_s_candidates[best_result_index]),
        optimal_frequency_hz=best_frequency_hz,
        max_difference=best_difference,
        value_1_at_optimum=best_value_1,
        value_2_at_optimum=best_value_2,
        sigma_s_candidates=sigma_s_candidates,
        scores=scores,
    )


def validate_solution_conductivity_optimization_inputs(
    eps_s_relative: float,
    sigma_s_min: float,
    sigma_s_max: float,
    num_sigma_points: int,
    f_min: float,
    f_max: float,
    num_frequency_points: int,
) -> None:
    if eps_s_relative <= 0:
        raise ValueError("eps_s_relative must be positive.")

    if sigma_s_min <= 0:
        raise ValueError("sigma_s_min must be positive.")

    if sigma_s_max <= sigma_s_min:
        raise ValueError("sigma_s_max must be greater than sigma_s_min.")

    if num_sigma_points < 2:
        raise ValueError("num_sigma_points must be greater than or equal to 2.")

    if f_min <= 0:
        raise ValueError("f_min must be positive.")

    if f_max <= f_min:
        raise ValueError("f_max must be greater than f_min.")

    if num_frequency_points < 2:
        raise ValueError("num_frequency_points must be greater than or equal to 2.")
