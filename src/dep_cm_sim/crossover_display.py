from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from dep_cm_sim.equations import CrossoverFrequencyResult
from dep_cm_sim.gui.value_format import (
    format_conductivity_s_m,
    format_dimensionless,
    format_force_pn,
    format_frequency_hz,
)


def build_crossover_summary(
    label: str,
    results: Sequence[CrossoverFrequencyResult],
) -> str:
    """1本のシミュレーション曲線のcrossover表示文字列を生成する。"""

    if not results:
        return f"{label}: crossover frequency 該当なし"

    lines = [f"{label}: Re[K] = 0"]

    if len(results) == 1:
        lines.append(
            f"f_cross = {format_frequency_hz(results[0].frequency_hz)}"
        )
        return "\n".join(lines)

    for index, result in enumerate(results, start=1):
        lines.append(
            f"f_cross,{index} = {format_frequency_hz(result.frequency_hz)}"
        )

    return "\n".join(lines)

def build_re_k_metric_summary(
    *,
    solution_conductivity_s_m: float | None,
    crossover_results: Sequence[CrossoverFrequencyResult],
    re_k_values: NDArray[np.float64],
) -> str:
    """Re[K]曲線の導電率、crossover、統計値を表示用文字列にする。"""

    if re_k_values.size == 0:
        raise ValueError("re_k_values must not be empty.")

    if not np.all(np.isfinite(re_k_values)):
        raise ValueError("re_k_values must contain only finite values.")

    if solution_conductivity_s_m is not None:
        if not np.isfinite(solution_conductivity_s_m):
            raise ValueError(
                "solution conductivity must be finite."
            )
        if solution_conductivity_s_m < 0.0:
            raise ValueError(
                "solution conductivity must be non-negative."
            )

    if solution_conductivity_s_m is None:
        lines = ["Solution Cond: N/A"]
    else:
        lines = [
            (
                "Solution Cond: "
                f"{format_conductivity_s_m(solution_conductivity_s_m)}"
            )
        ]

    if crossover_results:
        lines.append("Crossover Freq:")

        for index, result in enumerate(
            crossover_results,
            start=1,
        ):
            lines.append(
                f"  {index}: {format_frequency_hz(result.frequency_hz)}"
            )
    else:
        lines.append("Crossover Freq: None")

    re_k_max = float(np.max(re_k_values))
    re_k_min = float(np.min(re_k_values))
    re_k_magnitude = re_k_max - re_k_min

    lines.extend(
        [
            f"Re[K]_Max: {format_dimensionless(re_k_max)}",
            f"Re[K]_Min: {format_dimensionless(re_k_min)}",
            (
                "Re[K]_Magnitude: "
                f"{format_dimensionless(re_k_magnitude)}"
            ),
        ]
    )

    return "\n".join(lines)

def build_dep_force_metric_summary(
    *,
    solution_conductivity_s_m: float,
    crossover_results: Sequence[CrossoverFrequencyResult],
    force_pn_values: NDArray[np.float64],
) -> str:
    """DEP力曲線の導電率、crossover、統計値を表示用文字列にする。"""

    if force_pn_values.size == 0:
        raise ValueError("force_pn_values must not be empty.")

    if not np.all(np.isfinite(force_pn_values)):
        raise ValueError(
            "force_pn_values must contain only finite values."
        )

    if not np.isfinite(solution_conductivity_s_m):
        raise ValueError(
            "solution conductivity must be finite."
        )

    if solution_conductivity_s_m < 0.0:
        raise ValueError(
            "solution conductivity must be non-negative."
        )

    lines = [
        (
            "Solution Cond: "
            f"{format_conductivity_s_m(solution_conductivity_s_m)}"
        )
    ]

    if crossover_results:
        lines.append("Crossover Freq:")

        for index, result in enumerate(
            crossover_results,
            start=1,
        ):
            lines.append(
                f"  {index}: {format_frequency_hz(result.frequency_hz)}"
            )
    else:
        lines.append("Crossover Freq: None")

    force_max_pn = float(np.max(force_pn_values))
    force_min_pn = float(np.min(force_pn_values))
    force_magnitude_pn = force_max_pn - force_min_pn

    lines.extend(
        [
            f"F_DEP_Max: {format_force_pn(force_max_pn)}",
            f"F_DEP_Min: {format_force_pn(force_min_pn)}",
            (
                "F_DEP_Magnitude: "
                f"{format_force_pn(force_magnitude_pn)}"
            ),
        ]
    )

    return "\n".join(lines)
