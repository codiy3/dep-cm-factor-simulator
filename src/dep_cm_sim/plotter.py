from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray


def plot_cm_factor_real(
    frequency_hz: NDArray[np.float64],
    cm_factor_real: NDArray[np.float64],
    label: str,
    output_path: str | Path | None = None,
) -> None:
    """
    CM因子の実部 Re[K] と周波数の関係を描画する。

    Parameters
    ----------
    frequency_hz:
        周波数 [Hz]
    cm_factor_real:
        CM因子の実部 Re[K]
    label:
        凡例に表示する条件名
    output_path:
        PNG保存先。Noneの場合は画面表示のみ。
    """

    if frequency_hz.size == 0:
        raise ValueError("frequency_hz must not be empty.")
    if cm_factor_real.size == 0:
        raise ValueError("cm_factor_real must not be empty.")
    if frequency_hz.shape != cm_factor_real.shape:
        raise ValueError("frequency_hz and cm_factor_real must have the same shape.")
    if np.any(frequency_hz <= 0):
        raise ValueError("frequency_hz must be positive.")
    if np.isnan(cm_factor_real).any():
        raise ValueError("cm_factor_real must not contain NaN.")

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(frequency_hz, cm_factor_real, label=label)
    ax.set_xscale("log")
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Re[K]")
    ax.set_title("Real part of Clausius-Mossotti factor")
    ax.grid(True, which="both")
    ax.legend()

    fig.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300)

    plt.show()
