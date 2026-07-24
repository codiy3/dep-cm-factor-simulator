from __future__ import annotations

import math


_SUPERSCRIPT_TRANSLATION = str.maketrans(
    "-0123456789",
    "⁻⁰¹²³⁴⁵⁶⁷⁸⁹",
)


def _validate_finite(value: float, *, field_name: str) -> float:
    numeric_value = float(value)

    if not math.isfinite(numeric_value):
        raise ValueError(f"{field_name} must be finite.")

    return numeric_value


def _format_significant(
    value: float,
    *,
    significant_digits: int = 5,
) -> str:
    """指数表記を使わず、指定有効数字で小数表示する。"""

    if significant_digits < 1:
        raise ValueError("significant_digits must be at least 1.")

    if value == 0.0:
        return "0"

    digits_before_decimal = math.floor(math.log10(abs(value))) + 1
    decimal_places = max(
        0,
        significant_digits - digits_before_decimal,
    )

    formatted = f"{value:.{decimal_places}f}"

    if formatted.startswith("-0") and float(formatted) == 0.0:
        return formatted[1:]

    return formatted


def format_frequency_hz(
    value_hz: float,
    *,
    significant_digits: int = 5,
) -> str:
    """周波数をHz、kHz、MHz、GHzのいずれかで表示する。"""

    value_hz = _validate_finite(
        value_hz,
        field_name="frequency",
    )

    absolute_value = abs(value_hz)

    if absolute_value >= 1.0e9:
        scaled_value = value_hz / 1.0e9
        unit = "GHz"
    elif absolute_value >= 1.0e6:
        scaled_value = value_hz / 1.0e6
        unit = "MHz"
    elif absolute_value >= 1.0e3:
        scaled_value = value_hz / 1.0e3
        unit = "kHz"
    else:
        scaled_value = value_hz
        unit = "Hz"

    return (
        f"{_format_significant(scaled_value, significant_digits=significant_digits)} "
        f"{unit}"
    )


def format_conductivity_s_m(
    value_s_m: float,
    *,
    significant_digits: int = 3,
) -> str:
    """導電率をS/m、mS/m、µS/m、nS/m、pS/mで表示する。"""

    value_s_m = _validate_finite(
        value_s_m,
        field_name="conductivity",
    )

    if value_s_m < 0.0:
        raise ValueError("conductivity must be non-negative.")

    if value_s_m == 0.0:
        return "0 S/m"

    if value_s_m >= 1.0e-1:
        scaled_value = value_s_m
        unit = "S/m"
    elif value_s_m >= 1.0e-4:
        scaled_value = value_s_m * 1.0e3
        unit = "mS/m"
    elif value_s_m >= 1.0e-7:
        scaled_value = value_s_m * 1.0e6
        unit = "µS/m"
    elif value_s_m >= 1.0e-10:
        scaled_value = value_s_m * 1.0e9
        unit = "nS/m"
    else:
        scaled_value = value_s_m * 1.0e12
        unit = "pS/m"

    return (
        f"{_format_significant(scaled_value, significant_digits=significant_digits)} "
        f"{unit}"
    )


def format_dimensionless(
    value: float,
    *,
    significant_digits: int = 5,
) -> str:
    """無次元量を指数表記なしで表示する。"""

    value = _validate_finite(
        value,
        field_name="dimensionless value",
    )

    return _format_significant(
        value,
        significant_digits=significant_digits,
    )


def format_force_pn(
    value_pn: float,
    *,
    significant_digits: int = 5,
) -> str:
    """DEP力をpN単位で表示する。"""

    value_pn = _validate_finite(
        value_pn,
        field_name="force",
    )

    return (
        f"{_format_significant(value_pn, significant_digits=significant_digits)} "
        "pN"
    )


def format_voltage_v(
    value_v: float,
    *,
    significant_digits: int = 5,
) -> str:
    """電圧をV、mV、µVのいずれかで表示する。"""

    value_v = _validate_finite(
        value_v,
        field_name="voltage",
    )

    absolute_value = abs(value_v)

    if absolute_value == 0.0 or absolute_value >= 1.0:
        scaled_value = value_v
        unit = "V"
    elif absolute_value >= 1.0e-3:
        scaled_value = value_v * 1.0e3
        unit = "mV"
    else:
        scaled_value = value_v * 1.0e6
        unit = "µV"

    return (
        f"{_format_significant(scaled_value, significant_digits=significant_digits)} "
        f"{unit}"
    )


def format_length_m(
    value_m: float,
    *,
    significant_digits: int = 5,
) -> str:
    """長さをm、mm、µm、nmのいずれかで表示する。"""

    value_m = _validate_finite(
        value_m,
        field_name="length",
    )

    absolute_value = abs(value_m)

    if absolute_value == 0.0 or absolute_value >= 1.0:
        scaled_value = value_m
        unit = "m"
    elif absolute_value >= 1.0e-3:
        scaled_value = value_m * 1.0e3
        unit = "mm"
    elif absolute_value >= 1.0e-6:
        scaled_value = value_m * 1.0e6
        unit = "µm"
    else:
        scaled_value = value_m * 1.0e9
        unit = "nm"

    return (
        f"{_format_significant(scaled_value, significant_digits=significant_digits)} "
        f"{unit}"
    )


def format_permittivity_f_m(
    value_f_m: float,
    *,
    significant_digits: int = 5,
) -> str:
    """誘電率をF/m、nF/m、pF/mのいずれかで表示する。"""

    value_f_m = _validate_finite(
        value_f_m,
        field_name="permittivity",
    )

    absolute_value = abs(value_f_m)

    if absolute_value == 0.0 or absolute_value >= 1.0:
        scaled_value = value_f_m
        unit = "F/m"
    elif absolute_value >= 1.0e-9:
        scaled_value = value_f_m * 1.0e9
        unit = "nF/m"
    else:
        scaled_value = value_f_m * 1.0e12
        unit = "pF/m"

    return (
        f"{_format_significant(scaled_value, significant_digits=significant_digits)} "
        f"{unit}"
    )


def format_power_of_ten(
    value: float,
    unit: str,
    *,
    significant_digits: int = 6,
) -> str:
    """複合単位などをe表記ではなく×10ⁿ形式で表示する。"""

    value = _validate_finite(
        value,
        field_name="value",
    )

    if value == 0.0:
        return f"0 {unit}"

    exponent = math.floor(math.log10(abs(value)))
    mantissa = value / (10.0**exponent)
    exponent_text = str(exponent).translate(
        _SUPERSCRIPT_TRANSLATION
    )

    mantissa_text = _format_significant(
        mantissa,
        significant_digits=significant_digits,
    )

    return f"{mantissa_text} × 10{exponent_text} {unit}"
