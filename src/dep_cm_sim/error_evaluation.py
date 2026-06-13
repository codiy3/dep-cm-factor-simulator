from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class ErrorEvaluationResult:
    frequency_hz: NDArray[np.float64]
    experimental_values: NDArray[np.float64]
    simulated_values: NDArray[np.float64]
    errors: NDArray[np.float64]
    absolute_errors: NDArray[np.float64]
    mae: float
    rmse: float
    max_absolute_error: float
    num_points: int


def evaluate_simulation_error(
    simulation_frequency_hz: NDArray[np.float64],
    simulation_values: NDArray[np.float64],
    experimental_frequency_hz: NDArray[np.float64],
    experimental_values: NDArray[np.float64],
) -> ErrorEvaluationResult:
    validate_error_evaluation_inputs(
        simulation_frequency_hz=simulation_frequency_hz,
        simulation_values=simulation_values,
        experimental_frequency_hz=experimental_frequency_hz,
        experimental_values=experimental_values,
    )

    simulated_values_at_experimental_points = np.interp(
        experimental_frequency_hz,
        simulation_frequency_hz,
        simulation_values,
    )

    errors = experimental_values - simulated_values_at_experimental_points
    absolute_errors = np.abs(errors)

    mae = float(np.mean(absolute_errors))
    rmse = float(np.sqrt(np.mean(errors**2)))
    max_absolute_error = float(np.max(absolute_errors))

    return ErrorEvaluationResult(
        frequency_hz=experimental_frequency_hz,
        experimental_values=experimental_values,
        simulated_values=simulated_values_at_experimental_points,
        errors=errors,
        absolute_errors=absolute_errors,
        mae=mae,
        rmse=rmse,
        max_absolute_error=max_absolute_error,
        num_points=int(experimental_frequency_hz.size),
    )


def validate_error_evaluation_inputs(
    simulation_frequency_hz: NDArray[np.float64],
    simulation_values: NDArray[np.float64],
    experimental_frequency_hz: NDArray[np.float64],
    experimental_values: NDArray[np.float64],
) -> None:
    if simulation_frequency_hz.size == 0:
        raise ValueError("simulation_frequency_hz must not be empty.")

    if experimental_frequency_hz.size == 0:
        raise ValueError("experimental_frequency_hz must not be empty.")

    if simulation_frequency_hz.shape != simulation_values.shape:
        raise ValueError(
            "simulation_frequency_hz and simulation_values must have the same shape."
        )

    if experimental_frequency_hz.shape != experimental_values.shape:
        raise ValueError(
            "experimental_frequency_hz and experimental_values must have the same shape."
        )

    if np.isnan(simulation_frequency_hz).any():
        raise ValueError("simulation_frequency_hz must not contain NaN.")

    if np.isnan(simulation_values).any():
        raise ValueError("simulation_values must not contain NaN.")

    if np.isnan(experimental_frequency_hz).any():
        raise ValueError("experimental_frequency_hz must not contain NaN.")

    if np.isnan(experimental_values).any():
        raise ValueError("experimental_values must not contain NaN.")

    if np.any(simulation_frequency_hz <= 0):
        raise ValueError("simulation_frequency_hz must be positive.")

    if np.any(experimental_frequency_hz <= 0):
        raise ValueError("experimental_frequency_hz must be positive.")

    if not np.all(np.diff(simulation_frequency_hz) > 0):
        raise ValueError("simulation_frequency_hz must be strictly increasing.")

    if experimental_frequency_hz.min() < simulation_frequency_hz.min():
        raise ValueError(
            "experimental_frequency_hz must be within the simulation frequency range."
        )

    if experimental_frequency_hz.max() > simulation_frequency_hz.max():
        raise ValueError(
            "experimental_frequency_hz must be within the simulation frequency range."
        )


def save_error_evaluation_result_to_csv(
    result: ErrorEvaluationResult,
    path: str | Path,
) -> None:
    csv_path = Path(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "frequency_hz",
                "experimental_value",
                "simulated_value",
                "error",
                "absolute_error",
            ]
        )

        for frequency, experimental_value, simulated_value, error, absolute_error in zip(
            result.frequency_hz,
            result.experimental_values,
            result.simulated_values,
            result.errors,
            result.absolute_errors,
            strict=True,
        ):
            writer.writerow(
                [
                    frequency,
                    experimental_value,
                    simulated_value,
                    error,
                    absolute_error,
                ]
            )

        writer.writerow([])
        writer.writerow(["metric", "value"])
        writer.writerow(["mae", result.mae])
        writer.writerow(["rmse", result.rmse])
        writer.writerow(["max_absolute_error", result.max_absolute_error])
        writer.writerow(["num_points", result.num_points])
