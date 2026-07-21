from dep_cm_sim.crossover_display import build_crossover_summary
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
