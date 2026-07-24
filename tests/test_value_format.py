import pytest

from dep_cm_sim.gui.value_format import (
    format_conductivity_s_m,
    format_dimensionless,
    format_force_pn,
    format_frequency_hz,
    format_length_m,
    format_permittivity_f_m,
    format_power_of_ten,
    format_voltage_v,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (668.28, "668.28 Hz"),
        (1.2345e4, "12.345 kHz"),
        (1.3392e8, "133.92 MHz"),
        (1.0e10, "10.000 GHz"),
    ],
)
def test_format_frequency_hz(
    value: float,
    expected: str,
) -> None:
    assert format_frequency_hz(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (2.0e-4, "0.20000 mS/m"),
        (0.1, "100.00 mS/m"),
        (1.0, "1.0000 S/m"),
        (5.0e-7, "0.50000 µS/m"),
    ],
)
def test_format_conductivity_s_m(
    value: float,
    expected: str,
) -> None:
    assert format_conductivity_s_m(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.96778, "0.96778"),
        (-0.5, "-0.50000"),
        (1.4678, "1.4678"),
    ],
)
def test_format_dimensionless(
    value: float,
    expected: str,
) -> None:
    assert format_dimensionless(value) == expected


def test_format_force_pn() -> None:
    assert format_force_pn(1.2954) == "1.2954 pN"
    assert format_force_pn(-0.66929) == "-0.66929 pN"


def test_format_voltage_v() -> None:
    assert format_voltage_v(10.0) == "10.000 V"
    assert format_voltage_v(0.005) == "5.0000 mV"


def test_format_length_m() -> None:
    assert format_length_m(6.7e-6) == "6.7000 µm"


def test_format_permittivity_f_m() -> None:
    assert format_permittivity_f_m(7.08335e-10) == (
        "708.34 pF/m"
    )


def test_format_power_of_ten() -> None:
    assert format_power_of_ten(
        1.25e12,
        "V²/m³",
    ) == "1.25000 × 10¹² V²/m³"

    assert format_power_of_ten(
        1.0e11,
        "m⁻³",
    ) == "1.00000 × 10¹¹ m⁻³"


@pytest.mark.parametrize(
    "formatter",
    [
        format_frequency_hz,
        format_conductivity_s_m,
        format_dimensionless,
        format_force_pn,
        format_voltage_v,
        format_length_m,
        format_permittivity_f_m,
    ],
)
def test_formatters_reject_non_finite_values(formatter) -> None:
    with pytest.raises(ValueError, match="finite"):
        formatter(float("nan"))


def test_conductivity_rejects_negative_value() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        format_conductivity_s_m(-0.1)
