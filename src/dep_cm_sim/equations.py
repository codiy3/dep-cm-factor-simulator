from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class CrossoverFrequencyResult:
    """Re[K] = 0となる周波数と補間区間を保持する。"""

    frequency_hz: float
    lower_index: int
    upper_index: int


def find_crossover_frequencies(
    frequency_hz: NDArray[np.float64],
    re_k_values: NDArray[np.float64],
) -> tuple[CrossoverFrequencyResult, ...]:
    """
    Re[K] = 0となるcrossover frequencyを探索する。

    隣接する2点の間でRe[K]の符号が反転する場合は、
    log10(frequency)上でRe[K]を線形補間する。

    サンプル点のRe[K]が厳密に0の場合は、その周波数を返す。
    crossover frequencyが存在しない場合は空のタプルを返す。
    """

    if frequency_hz.ndim != 1 or re_k_values.ndim != 1:
        raise ValueError(
            "frequency_hz and re_k_values must be one-dimensional."
        )

    if frequency_hz.size == 0:
        raise ValueError("frequency_hz must not be empty.")

    if frequency_hz.size != re_k_values.size:
        raise ValueError(
            "frequency_hz and re_k_values must have the same length."
        )

    if not np.all(np.isfinite(frequency_hz)):
        raise ValueError("frequency_hz must contain only finite values.")

    if not np.all(np.isfinite(re_k_values)):
        raise ValueError("re_k_values must contain only finite values.")

    if np.any(frequency_hz <= 0.0):
        raise ValueError("frequency_hz must be positive.")

    if np.any(np.diff(frequency_hz) <= 0.0):
        raise ValueError("frequency_hz must be strictly increasing.")

    results: list[CrossoverFrequencyResult] = []

    for index, current_value_raw in enumerate(re_k_values):
        current_value = float(current_value_raw)

        if current_value == 0.0:
            results.append(
                CrossoverFrequencyResult(
                    frequency_hz=float(frequency_hz[index]),
                    lower_index=index,
                    upper_index=index,
                )
            )

        if index == re_k_values.size - 1:
            continue

        next_value = float(re_k_values[index + 1])

        # 端点が厳密に0の場合は、サンプル点として登録するため、
        # 補間結果として重複登録しない。
        if current_value == 0.0 or next_value == 0.0:
            continue

        crosses_zero = (
            current_value < 0.0 < next_value
            or next_value < 0.0 < current_value
        )
        if not crosses_zero:
            continue

        interpolation_fraction = -current_value / (
            next_value - current_value
        )

        lower_log_frequency = np.log10(float(frequency_hz[index]))
        upper_log_frequency = np.log10(float(frequency_hz[index + 1]))
        crossover_log_frequency = lower_log_frequency + (
            interpolation_fraction
            * (upper_log_frequency - lower_log_frequency)
        )

        results.append(
            CrossoverFrequencyResult(
                frequency_hz=float(10.0**crossover_log_frequency),
                lower_index=index,
                upper_index=index + 1,
            )
        )

    return tuple(results)
