from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OptimalFrequencyResult:
    frequency_hz: float
    index: int
    value_1: float
    value_2: float
    difference: float


def find_optimal_frequency(
    frequencies: np.ndarray,
    values_1: np.ndarray,
    values_2: np.ndarray,
) -> OptimalFrequencyResult:
    if len(frequencies) == 0:
        raise ValueError("frequencies must not be empty.")

    if len(frequencies) != len(values_1) or len(frequencies) != len(values_2):
        raise ValueError("frequencies, values_1, and values_2 must have the same length.")

    differences = np.abs(values_1 - values_2)
    index = int(np.argmax(differences))

    return OptimalFrequencyResult(
        frequency_hz=float(frequencies[index]),
        index=index,
        value_1=float(values_1[index]),
        value_2=float(values_2[index]),
        difference=float(differences[index]),
    )
