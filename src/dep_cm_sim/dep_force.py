from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from dep_cm_sim.equations import EPSILON_0


class ElectricFieldMode(str, Enum):
    """DEP力計算で使用する電場条件の入力方式。"""

    DIRECT_GRADIENT = "direct_gradient"
    VPP_AND_FACTOR = "vpp_and_factor"


DepClassification = Literal["pDEP", "nDEP", "zero"]


@dataclass(frozen=True)
class ElectricFieldResult:
    """DEP力計算に使用するRMS電場条件を保持する。"""

    mode: ElectricFieldMode
    gradient_v2_m3: float
    voltage_vpp: float | None = None
    voltage_peak: float | None = None
    voltage_rms: float | None = None
    gradient_factor_m_inv3: float | None = None


@dataclass(frozen=True)
class DepForceResult:
    """スカラーDEP力の計算結果と途中値を保持する。"""

    frequency_hz: float
    re_k: float
    epsilon_m_f_m: float
    radius_m: float
    electric_field: ElectricFieldResult
    force_n: float
    force_pn: float
    classification: DepClassification


def _require_finite(value: float, *, name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name}は有限値にしてください。")


def _require_non_negative(value: float, *, name: str) -> None:
    _require_finite(value, name=name)

    if value < 0.0:
        raise ValueError(f"{name}は0以上にしてください。")


def _require_positive(value: float, *, name: str) -> None:
    _require_finite(value, name=name)

    if value <= 0.0:
        raise ValueError(f"{name}は0より大きい値にしてください。")


def vpp_to_vpeak(voltage_vpp: float) -> float:
    """正弦波のpeak-to-peak電圧をpeak電圧へ変換する。"""

    _require_non_negative(voltage_vpp, name="Vp-p")
    voltage_peak = voltage_vpp / 2.0
    _require_finite(voltage_peak, name="V_peak")
    return voltage_peak


def vpp_to_vrms(voltage_vpp: float) -> float:
    """正弦波のpeak-to-peak電圧をRMS電圧へ変換する。"""

    voltage_peak = vpp_to_vpeak(voltage_vpp)
    voltage_rms = voltage_peak / math.sqrt(2.0)
    _require_finite(voltage_rms, name="V_rms")
    return voltage_rms


def create_direct_electric_field(
    gradient_v2_m3: float,
) -> ElectricFieldResult:
    """直接入力された∇|E_rms|²から電場条件を生成する。"""

    _require_non_negative(
        gradient_v2_m3,
        name="電場勾配 ∇|E_rms|²",
    )

    return ElectricFieldResult(
        mode=ElectricFieldMode.DIRECT_GRADIENT,
        gradient_v2_m3=gradient_v2_m3,
    )


def calculate_gradient_from_vpp(
    voltage_vpp: float,
    gradient_factor_m_inv3: float,
) -> ElectricFieldResult:
    """
    Vp-pと変換係数からRMS電場二乗勾配を計算する。

    gradient_factor_m_inv3は、
    ∇|E_rms|² / V_rms² [m^-3] を表す。
    """

    _require_non_negative(
        gradient_factor_m_inv3,
        name="gradient factor",
    )

    voltage_peak = vpp_to_vpeak(voltage_vpp)
    voltage_rms = vpp_to_vrms(voltage_vpp)
    gradient_v2_m3 = gradient_factor_m_inv3 * voltage_rms**2

    _require_finite(
        gradient_v2_m3,
        name="計算された電場勾配 ∇|E_rms|²",
    )

    return ElectricFieldResult(
        mode=ElectricFieldMode.VPP_AND_FACTOR,
        gradient_v2_m3=gradient_v2_m3,
        voltage_vpp=voltage_vpp,
        voltage_peak=voltage_peak,
        voltage_rms=voltage_rms,
        gradient_factor_m_inv3=gradient_factor_m_inv3,
    )


def classify_dep_force(force_n: float) -> DepClassification:
    """丸め前のDEP力の符号からpDEP、nDEP、zeroを判定する。"""

    _require_finite(force_n, name="DEP力")

    if force_n > 0.0:
        return "pDEP"

    if force_n < 0.0:
        return "nDEP"

    return "zero"


def calculate_dep_force(
    *,
    frequency_hz: float,
    re_k: float,
    eps_s_relative: float,
    radius_m: float,
    electric_field: ElectricFieldResult,
) -> DepForceResult:
    """
    RMS電場規約を用いて球形粒子のスカラーDEP力を計算する。

    F_DEP = 2π ε_m r³ Re[K] ∇|E_rms|²
    """

    _require_positive(frequency_hz, name="計算周波数")
    _require_finite(re_k, name="Re[K]")
    _require_positive(eps_s_relative, name="溶液の比誘電率")
    _require_positive(radius_m, name="細胞半径")
    _require_non_negative(
        electric_field.gradient_v2_m3,
        name="電場勾配 ∇|E_rms|²",
    )

    epsilon_m_f_m = EPSILON_0 * eps_s_relative
    _require_finite(epsilon_m_f_m, name="媒質絶対誘電率")

    force_n = (
        2.0
        * math.pi
        * epsilon_m_f_m
        * radius_m**3
        * re_k
        * electric_field.gradient_v2_m3
    )
    _require_finite(force_n, name="DEP力")

    force_pn = force_n * 1.0e12
    _require_finite(force_pn, name="DEP力のpN換算値")

    return DepForceResult(
        frequency_hz=frequency_hz,
        re_k=re_k,
        epsilon_m_f_m=epsilon_m_f_m,
        radius_m=radius_m,
        electric_field=electric_field,
        force_n=force_n,
        force_pn=force_pn,
        classification=classify_dep_force(force_n),
    )
