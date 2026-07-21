from __future__ import annotations

from collections.abc import Sequence

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
