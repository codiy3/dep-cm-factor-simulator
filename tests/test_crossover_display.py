import numpy as np

from dep_cm_sim.crossover_display import (
    build_crossover_summary,
    build_re_k_metric_summary,
)
from dep_cm_sim.equations import CrossoverFrequencyResult


def test_build_crossover_summary_with_one_result() -> None:
    results = (
        CrossoverFrequencyResult(
            frequency_hz=1.2345e4,
            lower_index=10,
            upper_index=11,
        ),
    )

    summary = build_crossover_summary("curve A", results)

    assert summary == ("curve A: Re[K] = 0\nf_cross = 1.23e+04 Hz")


def test_build_crossover_summary_with_multiple_results() -> None:
    results = (
        CrossoverFrequencyResult(
            frequency_hz=1.0e3,
            lower_index=1,
            upper_index=2,
        ),
        CrossoverFrequencyResult(
            frequency_hz=2.5e6,
            lower_index=5,
            upper_index=6,
        ),
    )

    summary = build_crossover_summary("curve B", results)

    assert summary == ("curve B: Re[K] = 0\nf_cross,1 = 1.00e+03 Hz\nf_cross,2 = 2.50e+06 Hz")


def test_build_crossover_summary_without_result() -> None:
    summary = build_crossover_summary("curve C", ())

    assert summary == "curve C: crossover frequency 該当なし"


def test_build_crossover_summary_keeps_results_separate_by_curve() -> None:
    curve_a_summary = build_crossover_summary(
        "curve A",
        (
            CrossoverFrequencyResult(
                frequency_hz=1.0e4,
                lower_index=2,
                upper_index=3,
            ),
        ),
    )
    curve_b_summary = build_crossover_summary(
        "curve B",
        (
            CrossoverFrequencyResult(
                frequency_hz=2.0e5,
                lower_index=4,
                upper_index=5,
            ),
        ),
    )

    assert "curve A" in curve_a_summary
    assert "2.00e+05" not in curve_a_summary
    assert "curve B" in curve_b_summary
    assert "1.00e+04" not in curve_b_summary


def test_build_re_k_metric_summary() -> None:
    results = (
        CrossoverFrequencyResult(
            frequency_hz=1.2345e4,
            lower_index=1,
            upper_index=2,
        ),
        CrossoverFrequencyResult(
            frequency_hz=2.5e6,
            lower_index=3,
            upper_index=4,
        ),
    )
    values = np.array(
        [-0.5, 0.25, 0.98],
        dtype=np.float64,
    )

    summary = build_re_k_metric_summary(
        solution_conductivity_s_m=2.0e-4,
        crossover_results=results,
        re_k_values=values,
    )

    assert summary == (
        "Solution Cond: 2.0000e-04 S/m\n"
        "Crossover Freq:\n"
        "  1: 1.2345e+04 Hz\n"
        "  2: 2.5000e+06 Hz\n"
        "Re[K]_Max: 9.8000e-01\n"
        "Re[K]_Min: -5.0000e-01\n"
        "Re[K]_Magnitude: 1.4800e+00"
    )


def test_build_re_k_metric_summary_without_crossover() -> None:
    values = np.array(
        [0.1, 0.2, 0.3],
        dtype=np.float64,
    )

    summary = build_re_k_metric_summary(
        solution_conductivity_s_m=None,
        crossover_results=(),
        re_k_values=values,
    )

    assert summary == (
        "Solution Cond: N/A\n"
        "Crossover Freq: None\n"
        "Re[K]_Max: 3.0000e-01\n"
        "Re[K]_Min: 1.0000e-01\n"
        "Re[K]_Magnitude: 2.0000e-01"
    )
