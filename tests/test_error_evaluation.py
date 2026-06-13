from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from dep_cm_sim.error_evaluation import (
    evaluate_simulation_error,
    save_error_evaluation_result_to_csv,
    validate_error_evaluation_inputs,
)


def test_evaluate_simulation_error_returns_zero_for_identical_values() -> None:
    simulation_frequency = np.array([1.0, 10.0, 100.0])
    simulation_values = np.array([0.1, 0.2, 0.3])
    experimental_frequency = np.array([1.0, 10.0, 100.0])
    experimental_values = np.array([0.1, 0.2, 0.3])

    result = evaluate_simulation_error(
        simulation_frequency_hz=simulation_frequency,
        simulation_values=simulation_values,
        experimental_frequency_hz=experimental_frequency,
        experimental_values=experimental_values,
    )

    np.testing.assert_allclose(result.simulated_values, experimental_values)
    np.testing.assert_allclose(result.errors, np.array([0.0, 0.0, 0.0]))
    assert result.mae == pytest.approx(0.0)
    assert result.rmse == pytest.approx(0.0)
    assert result.max_absolute_error == pytest.approx(0.0)
    assert result.num_points == 3


def test_evaluate_simulation_error_interpolates_simulation_values() -> None:
    simulation_frequency = np.array([1.0, 10.0, 100.0])
    simulation_values = np.array([0.0, 0.9, 1.8])
    experimental_frequency = np.array([5.5])
    experimental_values = np.array([0.50])

    result = evaluate_simulation_error(
        simulation_frequency_hz=simulation_frequency,
        simulation_values=simulation_values,
        experimental_frequency_hz=experimental_frequency,
        experimental_values=experimental_values,
    )

    np.testing.assert_allclose(result.simulated_values, np.array([0.45]))
    np.testing.assert_allclose(result.errors, np.array([0.05]))
    assert result.mae == pytest.approx(0.05)
    assert result.rmse == pytest.approx(0.05)


def test_evaluate_simulation_error_calculates_metrics() -> None:
    simulation_frequency = np.array([1.0, 10.0, 100.0])
    simulation_values = np.array([0.1, 0.2, 0.3])
    experimental_frequency = np.array([1.0, 10.0, 100.0])
    experimental_values = np.array([0.2, 0.0, 0.6])

    result = evaluate_simulation_error(
        simulation_frequency_hz=simulation_frequency,
        simulation_values=simulation_values,
        experimental_frequency_hz=experimental_frequency,
        experimental_values=experimental_values,
    )

    np.testing.assert_allclose(result.errors, np.array([0.1, -0.2, 0.3]))
    np.testing.assert_allclose(result.absolute_errors, np.array([0.1, 0.2, 0.3]))
    assert result.mae == pytest.approx(0.2)
    assert result.rmse == pytest.approx(np.sqrt((0.01 + 0.04 + 0.09) / 3.0))
    assert result.max_absolute_error == pytest.approx(0.3)


def test_validate_error_evaluation_inputs_rejects_experimental_frequency_below_range() -> None:
    with pytest.raises(ValueError, match="within the simulation frequency range"):
        validate_error_evaluation_inputs(
            simulation_frequency_hz=np.array([10.0, 100.0]),
            simulation_values=np.array([0.1, 0.2]),
            experimental_frequency_hz=np.array([1.0]),
            experimental_values=np.array([0.1]),
        )


def test_validate_error_evaluation_inputs_rejects_experimental_frequency_above_range() -> None:
    with pytest.raises(ValueError, match="within the simulation frequency range"):
        validate_error_evaluation_inputs(
            simulation_frequency_hz=np.array([10.0, 100.0]),
            simulation_values=np.array([0.1, 0.2]),
            experimental_frequency_hz=np.array([1000.0]),
            experimental_values=np.array([0.1]),
        )


def test_validate_error_evaluation_inputs_rejects_non_increasing_simulation_frequency() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_error_evaluation_inputs(
            simulation_frequency_hz=np.array([10.0, 10.0, 100.0]),
            simulation_values=np.array([0.1, 0.2, 0.3]),
            experimental_frequency_hz=np.array([10.0]),
            experimental_values=np.array([0.1]),
        )


def test_validate_error_evaluation_inputs_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="same shape"):
        validate_error_evaluation_inputs(
            simulation_frequency_hz=np.array([1.0, 10.0]),
            simulation_values=np.array([0.1]),
            experimental_frequency_hz=np.array([1.0]),
            experimental_values=np.array([0.1]),
        )


def test_save_error_evaluation_result_to_csv(tmp_path: Path) -> None:
    result = evaluate_simulation_error(
        simulation_frequency_hz=np.array([1.0, 10.0, 100.0]),
        simulation_values=np.array([0.1, 0.2, 0.3]),
        experimental_frequency_hz=np.array([1.0, 10.0, 100.0]),
        experimental_values=np.array([0.2, 0.0, 0.6]),
    )

    csv_path = tmp_path / "error_result.csv"
    save_error_evaluation_result_to_csv(result, csv_path)

    text = csv_path.read_text(encoding="utf-8")

    assert "frequency_hz,experimental_value,simulated_value,error,absolute_error" in text
    assert "metric,value" in text
    assert "mae" in text
    assert "rmse" in text
    assert "max_absolute_error" in text
    assert "num_points" in text
