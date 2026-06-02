import numpy as np
import pytest

from dep_cm_sim.optimization import find_optimal_frequency


def test_find_optimal_frequency_returns_max_difference_point() -> None:
    frequencies = np.array([1.0, 10.0, 100.0, 1000.0])
    values_1 = np.array([0.0, 0.2, 0.8, 0.1])
    values_2 = np.array([0.0, -0.1, -0.4, 0.0])

    result = find_optimal_frequency(frequencies, values_1, values_2)

    assert result.index == 2
    assert result.frequency_hz == 100.0
    assert result.value_1 == 0.8
    assert result.value_2 == -0.4
    assert result.difference == pytest.approx(1.2)


def test_find_optimal_frequency_rejects_empty_arrays() -> None:
    frequencies = np.array([])
    values_1 = np.array([])
    values_2 = np.array([])

    with pytest.raises(ValueError, match="must not be empty"):
        find_optimal_frequency(frequencies, values_1, values_2)


def test_find_optimal_frequency_rejects_different_lengths() -> None:
    frequencies = np.array([1.0, 10.0])
    values_1 = np.array([0.1])
    values_2 = np.array([0.2, 0.3])

    with pytest.raises(ValueError, match="same length"):
        find_optimal_frequency(frequencies, values_1, values_2)


def test_find_optimal_frequency_accepts_single_point() -> None:
    frequencies = np.array([1000.0])
    values_1 = np.array([0.4])
    values_2 = np.array([-0.2])

    result = find_optimal_frequency(frequencies, values_1, values_2)

    assert result.index == 0
    assert result.frequency_hz == 1000.0
    assert result.difference == pytest.approx(0.6)


def test_find_optimal_frequency_returns_zero_for_same_curves() -> None:
    frequencies = np.array([1.0, 10.0, 100.0])
    values_1 = np.array([0.1, 0.2, 0.3])
    values_2 = np.array([0.1, 0.2, 0.3])

    result = find_optimal_frequency(frequencies, values_1, values_2)

    assert result.index == 0
    assert result.frequency_hz == 1.0
    assert result.difference == 0.0
