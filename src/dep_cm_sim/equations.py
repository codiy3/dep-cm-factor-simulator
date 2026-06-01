from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

EPSILON_0 = 8.8541878128e-12  # F/m


def calculate_cm_factor_real(
    frequency_hz: NDArray[np.float64],
    membrane_capacitance: float,
    radius_m: float,
    eps_c_relative: float,
    eps_s_relative: float,
    sigma_c: float,
    sigma_s: float,
) -> NDArray[np.float64]:
    """
    添付画像の式(6)に基づき、Clausius-Mossotti因子の実部 Re[K] を計算する。

    Parameters
    ----------
    frequency_hz:
        周波数 [Hz]
    membrane_capacitance:
        細胞膜容量 C_m [F/m^2]
    radius_m:
        細胞半径 r [m]
    eps_c_relative:
        細胞質の比誘電率 [-]
    eps_s_relative:
        溶液の比誘電率 [-]
    sigma_c:
        細胞質導電率 [S/m]
    sigma_s:
        溶液導電率 [S/m]

    Returns
    -------
    NDArray[np.float64]
        CM因子の実部 Re[K]
    """

    if frequency_hz.size == 0:
        raise ValueError("frequency_hz must not be empty.")
    if np.any(frequency_hz <= 0):
        raise ValueError("frequency_hz must be positive.")
    if membrane_capacitance <= 0:
        raise ValueError("membrane_capacitance must be positive.")
    if radius_m <= 0:
        raise ValueError("radius_m must be positive.")
    if eps_c_relative <= 0:
        raise ValueError("eps_c_relative must be positive.")
    if eps_s_relative <= 0:
        raise ValueError("eps_s_relative must be positive.")
    if sigma_c <= 0:
        raise ValueError("sigma_c must be positive.")
    if sigma_s <= 0:
        raise ValueError("sigma_s must be positive.")

    omega = 2.0 * np.pi * frequency_hz

    eps_c = eps_c_relative * EPSILON_0
    eps_s = eps_s_relative * EPSILON_0

    tau_ms = membrane_capacitance * radius_m / sigma_s
    tau_mc = membrane_capacitance * radius_m / sigma_c
    tau_s = eps_s / sigma_s
    tau_c = eps_c / sigma_c

    numerator = (
        1.0
        + omega**2 * (tau_ms * tau_c - tau_mc * tau_s - tau_s * tau_c)
        + 1j * omega * (tau_mc - tau_ms + tau_c + tau_s)
    )

    denominator = (
        2.0
        - omega**2 * (tau_ms * tau_c + 2.0 * tau_mc * tau_s + tau_s * tau_c)
        + 1j * omega * (2.0 * tau_mc + tau_ms + 2.0 * tau_c + 2.0 * tau_s)
    )

    cm_factor = -numerator / denominator
    return np.real(cm_factor).astype(np.float64)
