from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from dep_cm_sim.dep_force import (
    DepForceResult,
    ElectricFieldResult,
    calculate_dep_force,
)
from dep_cm_sim.equations import (
    CrossoverFrequencyResult,
    calculate_cm_factor_real,
    find_crossover_frequencies,
)


@dataclass(frozen=True)
class DepForceSweepResult:
    """周波数掃引によるDEP力計算結果を保持する。"""

    frequency_hz: NDArray[np.float64]
    re_k_values: NDArray[np.float64]
    force_n_values: NDArray[np.float64]
    force_pn_values: NDArray[np.float64]
    point_results: tuple[DepForceResult, ...]
    crossover_results: tuple[CrossoverFrequencyResult, ...]
    solution_conductivity_s_m: float
    electric_field: ElectricFieldResult


def calculate_dep_force_sweep(
    *,
    f_min: float,
    f_max: float,
    num_points: int,
    membrane_capacitance: float,
    radius_m: float,
    eps_c_relative: float,
    eps_s_relative: float,
    sigma_c: float,
    sigma_s: float,
    electric_field: ElectricFieldResult,
) -> DepForceSweepResult:
    """
    対数間隔の周波数配列に対してRe[K]とDEP力を計算する。

    周波数配列はParameterWindowの通常曲線と同じく、
    np.logspace(log10(f_min), log10(f_max), num_points)で生成する。
    """

    if not np.isfinite(f_min) or f_min <= 0.0:
        raise ValueError("最小周波数 f_min は0より大きい有限値にしてください。")

    if not np.isfinite(f_max) or f_max <= 0.0:
        raise ValueError("最大周波数 f_max は0より大きい有限値にしてください。")

    if f_min >= f_max:
        raise ValueError(
            "最大周波数 f_max は最小周波数 f_min より大きい値にしてください。"
        )

    if isinstance(num_points, bool) or not isinstance(num_points, int):
        raise ValueError("計算点数 num_points は整数にしてください。")

    if num_points < 2:
        raise ValueError("計算点数 num_points は2以上にしてください。")

    frequency_hz = np.logspace(
        np.log10(f_min),
        np.log10(f_max),
        num_points,
        dtype=np.float64,
    )

    re_k_values = calculate_cm_factor_real(
        frequency_hz=frequency_hz,
        membrane_capacitance=membrane_capacitance,
        radius_m=radius_m,
        eps_c_relative=eps_c_relative,
        eps_s_relative=eps_s_relative,
        sigma_c=sigma_c,
        sigma_s=sigma_s,
    )

    if re_k_values.shape != frequency_hz.shape:
        raise ValueError(
            "Re[K]配列と周波数配列の形状が一致しません。"
        )

    if not np.all(np.isfinite(re_k_values)):
        raise ValueError("計算されたRe[K]に有限値でない値が含まれています。")

    point_results = tuple(
        calculate_dep_force(
            frequency_hz=float(current_frequency_hz),
            re_k=float(current_re_k),
            eps_s_relative=eps_s_relative,
            radius_m=radius_m,
            electric_field=electric_field,
        )
        for current_frequency_hz, current_re_k in zip(
            frequency_hz,
            re_k_values,
            strict=True,
        )
    )

    force_n_values = np.array(
        [result.force_n for result in point_results],
        dtype=np.float64,
    )
    force_pn_values = np.array(
        [result.force_pn for result in point_results],
        dtype=np.float64,
    )

    crossover_results = find_crossover_frequencies(
        frequency_hz=frequency_hz,
        re_k_values=re_k_values,
    )

    return DepForceSweepResult(
        frequency_hz=frequency_hz,
        re_k_values=re_k_values,
        force_n_values=force_n_values,
        force_pn_values=force_pn_values,
        point_results=point_results,
        crossover_results=crossover_results,
        solution_conductivity_s_m=float(sigma_s),
        electric_field=electric_field,
    )
