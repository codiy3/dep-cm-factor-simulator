import numpy as np
import pytest

from dep_cm_sim.equations import (
    calculate_cm_factor_real,
    find_crossover_frequencies,
)


def test_calculate_cm_factor_real_returns_same_shape() -> None:
    frequency_hz = np.logspace(0, 10, 100)

    result = calculate_cm_factor_real(
        frequency_hz=frequency_hz,
        membrane_capacitance=0.015,
        radius_m=6.7e-6,
        eps_c_relative=60.0,
        eps_s_relative=80.0,
        sigma_c=0.5,
        sigma_s=2.0e-4,
    )

    assert result.shape == frequency_hz.shape


def test_calculate_cm_factor_real_has_no_nan() -> None:
    frequency_hz = np.logspace(0, 10, 100)

    result = calculate_cm_factor_real(
        frequency_hz=frequency_hz,
        membrane_capacitance=0.015,
        radius_m=6.7e-6,
        eps_c_relative=60.0,
        eps_s_relative=80.0,
        sigma_c=0.5,
        sigma_s=2.0e-4,
    )

    assert not np.isnan(result).any()


def test_calculate_cm_factor_real_rejects_zero_frequency() -> None:
    frequency_hz = np.array([0.0, 1.0, 10.0])

    with pytest.raises(ValueError, match="frequency_hz must be positive"):
        calculate_cm_factor_real(
            frequency_hz=frequency_hz,
            membrane_capacitance=0.015,
            radius_m=6.7e-6,
            eps_c_relative=60.0,
            eps_s_relative=80.0,
            sigma_c=0.5,
            sigma_s=2.0e-4,
        )


def test_calculate_cm_factor_real_rejects_negative_sigma_s() -> None:
    frequency_hz = np.logspace(0, 10, 100)

    with pytest.raises(ValueError, match="sigma_s must be positive"):
        calculate_cm_factor_real(
            frequency_hz=frequency_hz,
            membrane_capacitance=0.015,
            radius_m=6.7e-6,
            eps_c_relative=60.0,
            eps_s_relative=80.0,
            sigma_c=0.5,
            sigma_s=-1.0,
        )


def test_find_crossover_frequencies_interpolates_on_log_frequency() -> None:
    frequency_hz = np.array([10.0, 100.0], dtype=np.float64)
    re_k_values = np.array([-1.0, 1.0], dtype=np.float64)

    results = find_crossover_frequencies(frequency_hz, re_k_values)

    assert len(results) == 1
    assert results[0].frequency_hz == pytest.approx(np.sqrt(1000.0))
    assert results[0].lower_index == 0
    assert results[0].upper_index == 1


def test_find_crossover_frequencies_returns_exact_zero_sample() -> None:
    frequency_hz = np.array([1.0, 10.0, 100.0], dtype=np.float64)
    re_k_values = np.array([1.0, 0.0, -1.0], dtype=np.float64)

    results = find_crossover_frequencies(frequency_hz, re_k_values)

    assert len(results) == 1
    assert results[0].frequency_hz == 10.0
    assert results[0].lower_index == 1
    assert results[0].upper_index == 1


def test_find_crossover_frequencies_returns_multiple_crossovers() -> None:
    frequency_hz = np.array(
        [1.0, 10.0, 100.0, 1000.0],
        dtype=np.float64,
    )
    re_k_values = np.array(
        [-1.0, 1.0, -1.0, 1.0],
        dtype=np.float64,
    )

    results = find_crossover_frequencies(frequency_hz, re_k_values)

    assert len(results) == 3
    np.testing.assert_allclose(
        [result.frequency_hz for result in results],
        [
            np.sqrt(10.0),
            np.sqrt(1000.0),
            np.sqrt(100000.0),
        ],
    )


def test_find_crossover_frequencies_returns_empty_without_crossover() -> None:
    frequency_hz = np.array([1.0, 10.0, 100.0], dtype=np.float64)
    re_k_values = np.array([0.1, 0.2, 0.3], dtype=np.float64)

    results = find_crossover_frequencies(frequency_hz, re_k_values)

    assert results == ()


def test_find_crossover_frequencies_rejects_different_lengths() -> None:
    frequency_hz = np.array([1.0, 10.0], dtype=np.float64)
    re_k_values = np.array([-1.0], dtype=np.float64)

    with pytest.raises(ValueError, match="must have the same length"):
        find_crossover_frequencies(frequency_hz, re_k_values)


def test_find_crossover_frequencies_rejects_non_increasing_frequency() -> None:
    frequency_hz = np.array([1.0, 10.0, 10.0], dtype=np.float64)
    re_k_values = np.array([-1.0, 0.5, 1.0], dtype=np.float64)

    with pytest.raises(ValueError, match="must be strictly increasing"):
        find_crossover_frequencies(frequency_hz, re_k_values)


@pytest.mark.parametrize(
    ("frequency_hz", "re_k_values", "error_message"),
    [
        (
            np.array([0.0, 10.0], dtype=np.float64),
            np.array([-1.0, 1.0], dtype=np.float64),
            "frequency_hz must be positive",
        ),
        (
            np.array([1.0, np.inf], dtype=np.float64),
            np.array([-1.0, 1.0], dtype=np.float64),
            "frequency_hz must contain only finite values",
        ),
        (
            np.array([1.0, 10.0], dtype=np.float64),
            np.array([-1.0, np.nan], dtype=np.float64),
            "re_k_values must contain only finite values",
        ),
    ],
)
def test_find_crossover_frequencies_rejects_invalid_values(
    frequency_hz: np.ndarray,
    re_k_values: np.ndarray,
    error_message: str,
) -> None:
    with pytest.raises(ValueError, match=error_message):
        find_crossover_frequencies(frequency_hz, re_k_values)
