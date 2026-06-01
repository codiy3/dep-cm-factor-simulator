from __future__ import annotations

import numpy as np

from dep_cm_sim.equations import calculate_cm_factor_real
from dep_cm_sim.plotter import plot_cm_factor_real


def main() -> None:
    frequency_hz = np.logspace(0, 10, 1000)

    cm_factor_real = calculate_cm_factor_real(
        frequency_hz=frequency_hz,
        membrane_capacitance=0.015,
        radius_m=6.7e-6,
        eps_c_relative=60.0,
        eps_s_relative=80.0,
        sigma_c=0.5,
        sigma_s=2.0e-4,
    )

    plot_cm_factor_real(
        frequency_hz=frequency_hz,
        cm_factor_real=cm_factor_real,
        label="sigma_s=2.0e-4 S/m",
        output_path="outputs/cm_factor_sigma_s_2e-4.png",
    )


if __name__ == "__main__":
    main()
