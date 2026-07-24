from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from dep_cm_sim.equations import CrossoverFrequencyResult


def build_crossover_summary(
    label: str,
    results: Sequence[CrossoverFrequencyResult],
) -> str:
    """1本のシミュレーション曲線のcrossover表示文字列を生成する。"""

    if not results:
        return f"{label}: crossover frequency 該当なし"

    lines = [f"{label}: Re[K] = 0"]

    if len(results) == 1:
        lines.append(f"f_cross = {results[0].frequency_hz:.2e} Hz")
        return "\n".join(lines)

    for index, result in enumerate(results, start=1):
        lines.append(f"f_cross,{index} = {result.frequency_hz:.2e} Hz")

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
                f"{solution_conductivity_s_m:.4e} S/m"
            )
        ]

    if crossover_results:
        lines.append("Crossover Freq:")

        for index, result in enumerate(
            crossover_results,
            start=1,
        ):
            lines.append(
                f"  {index}: {result.frequency_hz:.4e} Hz"
            )
    else:
        lines.append("Crossover Freq: None")

    re_k_max = float(np.max(re_k_values))
    re_k_min = float(np.min(re_k_values))
    re_k_magnitude = re_k_max - re_k_min

    lines.extend(
        [
            f"Re[K]_Max: {re_k_max:.4e}",
            f"Re[K]_Min: {re_k_min:.4e}",
            f"Re[K]_Magnitude: {re_k_magnitude:.4e}",
        ]
    )

    return "\n".join(lines)
