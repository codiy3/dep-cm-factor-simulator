import math

import pytest

from dep_cm_sim.dep_force import (
    ElectricFieldMode,
    calculate_dep_force,
    calculate_gradient_from_vpp,
    classify_dep_force,
    create_direct_electric_field,
    vpp_to_vpeak,
    vpp_to_vrms,
)


def calculate_example_force(
    *,
    re_k: float = 0.25,
    eps_s_relative: float = 80.0,
    radius_m: float = 6.7e-6,
    gradient_v2_m3: float = 1.0e12,
):
    return calculate_dep_force(
        frequency_hz=1.0e5,
        re_k=re_k,
        eps_s_relative=eps_s_relative,
        radius_m=radius_m,
        electric_field=create_direct_electric_field(gradient_v2_m3),
    )


def test_vpp_to_vpeak_returns_zero_for_zero_vpp() -> None:
    assert vpp_to_vpeak(0.0) == 0.0


def test_vpp_to_vrms_returns_zero_for_zero_vpp() -> None:
    assert vpp_to_vrms(0.0) == 0.0


def test_vpp_to_vrms_converts_two_sqrt_two_to_one() -> None:
    assert vpp_to_vrms(2.0 * math.sqrt(2.0)) == pytest.approx(1.0)


@pytest.mark.parametrize("invalid_value", [-1.0, math.nan, math.inf, -math.inf])
def test_vpp_conversion_rejects_invalid_values(invalid_value: float) -> None:
    with pytest.raises(ValueError):
        vpp_to_vrms(invalid_value)


def test_create_direct_electric_field_preserves_gradient() -> None:
    result = create_direct_electric_field(1.0e12)

    assert result.mode is ElectricFieldMode.DIRECT_GRADIENT
    assert result.gradient_v2_m3 == pytest.approx(1.0e12)
    assert result.voltage_vpp is None
    assert result.voltage_peak is None
    assert result.voltage_rms is None
    assert result.gradient_factor_m_inv3 is None


@pytest.mark.parametrize("invalid_value", [-1.0, math.nan, math.inf, -math.inf])
def test_create_direct_electric_field_rejects_invalid_gradient(
    invalid_value: float,
) -> None:
    with pytest.raises(ValueError):
        create_direct_electric_field(invalid_value)


def test_calculate_gradient_from_vpp_uses_rms_voltage_squared() -> None:
    result = calculate_gradient_from_vpp(
        voltage_vpp=2.0 * math.sqrt(2.0),
        gradient_factor_m_inv3=1.0e12,
    )

    assert result.mode is ElectricFieldMode.VPP_AND_FACTOR
    assert result.voltage_peak == pytest.approx(math.sqrt(2.0))
    assert result.voltage_rms == pytest.approx(1.0)
    assert result.gradient_v2_m3 == pytest.approx(1.0e12)


def test_calculate_gradient_from_vpp_returns_zero_for_zero_vpp() -> None:
    result = calculate_gradient_from_vpp(
        voltage_vpp=0.0,
        gradient_factor_m_inv3=1.0e12,
    )

    assert result.gradient_v2_m3 == 0.0


def test_calculate_gradient_from_vpp_returns_zero_for_zero_factor() -> None:
    result = calculate_gradient_from_vpp(
        voltage_vpp=10.0,
        gradient_factor_m_inv3=0.0,
    )

    assert result.gradient_v2_m3 == 0.0


@pytest.mark.parametrize("invalid_value", [-1.0, math.nan, math.inf, -math.inf])
def test_calculate_gradient_from_vpp_rejects_invalid_factor(
    invalid_value: float,
) -> None:
    with pytest.raises(ValueError):
        calculate_gradient_from_vpp(
            voltage_vpp=1.0,
            gradient_factor_m_inv3=invalid_value,
        )


def test_calculate_dep_force_returns_positive_force_for_positive_re_k() -> None:
    result = calculate_example_force(re_k=0.25)

    assert result.force_n > 0.0
    assert result.classification == "pDEP"


def test_calculate_dep_force_returns_negative_force_for_negative_re_k() -> None:
    result = calculate_example_force(re_k=-0.25)

    assert result.force_n < 0.0
    assert result.classification == "nDEP"


def test_calculate_dep_force_returns_zero_for_zero_re_k() -> None:
    result = calculate_example_force(re_k=0.0)

    assert result.force_n == 0.0
    assert result.force_pn == 0.0
    assert result.classification == "zero"


def test_calculate_dep_force_returns_zero_for_zero_gradient() -> None:
    result = calculate_example_force(gradient_v2_m3=0.0)

    assert result.force_n == 0.0
    assert result.classification == "zero"


def test_calculate_dep_force_is_proportional_to_radius_cubed() -> None:
    smaller = calculate_example_force(radius_m=1.0e-6)
    larger = calculate_example_force(radius_m=2.0e-6)

    assert larger.force_n == pytest.approx(8.0 * smaller.force_n)


def test_calculate_dep_force_is_proportional_to_medium_permittivity() -> None:
    lower = calculate_example_force(eps_s_relative=40.0)
    higher = calculate_example_force(eps_s_relative=80.0)

    assert higher.force_n == pytest.approx(2.0 * lower.force_n)


def test_direct_and_vpp_modes_return_same_force_for_same_gradient() -> None:
    direct_field = create_direct_electric_field(1.0e12)
    vpp_field = calculate_gradient_from_vpp(
        voltage_vpp=2.0 * math.sqrt(2.0),
        gradient_factor_m_inv3=1.0e12,
    )

    direct_result = calculate_dep_force(
        frequency_hz=1.0e5,
        re_k=0.25,
        eps_s_relative=80.0,
        radius_m=6.7e-6,
        electric_field=direct_field,
    )
    vpp_result = calculate_dep_force(
        frequency_hz=1.0e5,
        re_k=0.25,
        eps_s_relative=80.0,
        radius_m=6.7e-6,
        electric_field=vpp_field,
    )

    assert vpp_result.force_n == pytest.approx(direct_result.force_n)
    assert vpp_result.force_pn == pytest.approx(direct_result.force_pn)


def test_calculate_dep_force_converts_newtons_to_piconewtons() -> None:
    result = calculate_example_force()

    assert result.force_pn == pytest.approx(result.force_n * 1.0e12)


@pytest.mark.parametrize(
    ("force_n", "expected"),
    [
        (1.0e-300, "pDEP"),
        (-1.0e-300, "nDEP"),
        (0.0, "zero"),
    ],
)
def test_classify_dep_force_does_not_use_arbitrary_zero_threshold(
    force_n: float,
    expected: str,
) -> None:
    assert classify_dep_force(force_n) == expected


@pytest.mark.parametrize(
    ("keyword", "invalid_value"),
    [
        ("frequency_hz", 0.0),
        ("frequency_hz", -1.0),
        ("frequency_hz", math.nan),
        ("re_k", math.nan),
        ("re_k", math.inf),
        ("eps_s_relative", 0.0),
        ("eps_s_relative", -1.0),
        ("radius_m", 0.0),
        ("radius_m", -1.0),
    ],
)
def test_calculate_dep_force_rejects_invalid_values(
    keyword: str,
    invalid_value: float,
) -> None:
    arguments = {
        "frequency_hz": 1.0e5,
        "re_k": 0.25,
        "eps_s_relative": 80.0,
        "radius_m": 6.7e-6,
        "electric_field": create_direct_electric_field(1.0e12),
    }
    arguments[keyword] = invalid_value

    with pytest.raises(ValueError):
        calculate_dep_force(**arguments)
