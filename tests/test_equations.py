import numpy as np
import pytest

from dep_cm_sim.equations import calculate_cm_factor_real


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
