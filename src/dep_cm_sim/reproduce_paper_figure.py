from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from dep_cm_sim.equations import calculate_cm_factor_real


PAPER_SIGMA_S_CONDITIONS: list[tuple[str, float]] = [
    ("(a)", 2.0e-4),
    ("(b)", 1.0e-3),
    ("(c)", 1.0e-2),
    ("(d)", 1.0e-1),
    ("(e)", 2.0e-1),
    ("(f)", 4.0e-1),
    ("(g)", 5.0e-1),
    ("(h)", 1.0e0),
]


def reproduce_paper_figure(
    output_path: str | Path = "outputs/paper_figure_reproduction.png",
) -> None:
    frequency_hz = np.logspace(0, 10, 1000)

    fig, ax = plt.subplots(figsize=(7, 6))

    for label, sigma_s in PAPER_SIGMA_S_CONDITIONS:
        cm_factor_real = calculate_cm_factor_real(
            frequency_hz=frequency_hz,
            membrane_capacitance=0.015,
            radius_m=6.7e-6,
            eps_c_relative=60.0,
            eps_s_relative=80.0,
            sigma_c=0.5,
            sigma_s=sigma_s,
        )

        ax.plot(
            frequency_hz,
            cm_factor_real,
            label=f"{label} sigma_s={sigma_s:.1e} S/m",
        )

    ax.set_xscale("log")
    ax.set_xlabel("Frequency [Hz]")
    ax.set_ylabel("Re[K]")
    ax.set_title("Reproduction of CM factor frequency dependence")
    ax.grid(True, which="both")
    ax.axhline(0.0, linewidth=1.0)
    ax.legend(fontsize=8)

    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)

    plt.show()


def main() -> None:
    reproduce_paper_figure()


if __name__ == "__main__":
    main()
