from __future__ import annotations

import csv
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
from numpy.typing import NDArray


ParameterValue = float | int | str

SUMMARY_FIELDNAMES: Final[tuple[str, ...]] = (
    "scope",
    "curve_index",
    "curve_label",
    "record_type",
    "item_name",
    "item_index",
    "value",
    "unit",
    "status",
)

CURVE_DATA_FIELDNAMES: Final[tuple[str, ...]] = (
    "curve_index",
    "curve_label",
    "point_index",
    "frequency_hz",
    "re_k",
)


@dataclass(frozen=True)
class ParameterSnapshot:
    """曲線作成時点のシミュレーションパラメータを保持する。"""

    key: str
    name: str
    value: ParameterValue
    unit: str


@dataclass(frozen=True)
class OptimizationSnapshot:
    """グラフ上に表示した最適周波数情報を保持する。"""

    mode: str
    frequency_hz: float
    value_1: float
    value_2: float
    difference: float
    curve_1_label: str
    curve_2_label: str


@dataclass(frozen=True)
class CurveExportData:
    """1本のシミュレーション曲線に対応するCSV出力情報。"""

    label: str
    frequencies: NDArray[np.float64]
    values: NDArray[np.float64]
    parameters: tuple[ParameterSnapshot, ...] = ()
    crossover_frequencies_hz: tuple[float, ...] = ()


class CsvExportError(RuntimeError):
    """CSV保存中に発生したエラーと保存済みファイルを保持する。"""

    def __init__(
        self,
        message: str,
        *,
        summary_path: Path,
        curve_data_path: Path,
        saved_paths: tuple[Path, ...],
    ) -> None:
        super().__init__(message)
        self.summary_path = summary_path
        self.curve_data_path = curve_data_path
        self.saved_paths = saved_paths


def derive_csv_paths(base_path: str | Path) -> tuple[Path, Path]:
    """基準パスからsummary CSVとcurve data CSVのパスを生成する。"""

    path = Path(base_path)

    if path.suffix.lower() != ".csv":
        path = path.with_suffix(".csv")

    summary_path = path.with_name(f"{path.stem}_summary.csv")
    curve_data_path = path.with_name(f"{path.stem}_curve_data.csv")
    return summary_path, curve_data_path


def build_summary_rows(
    curves: Sequence[CurveExportData],
    optimization: OptimizationSnapshot | None = None,
) -> list[dict[str, str]]:
    """サマリーCSVへ書き込む縦持ち行を生成する。"""

    if not curves:
        raise ValueError("At least one simulation curve is required.")

    rows: list[dict[str, str]] = []

    for curve_index, curve in enumerate(curves, start=1):
        _validate_curve(curve)

        for parameter_index, parameter in enumerate(curve.parameters, start=1):
            rows.append(
                _build_summary_row(
                    scope="curve",
                    curve_index=str(curve_index),
                    curve_label=curve.label,
                    record_type="parameter",
                    item_name=parameter.key,
                    item_index=str(parameter_index),
                    value=_format_value(parameter.value),
                    unit=parameter.unit,
                    status="ok",
                )
            )

        if curve.crossover_frequencies_hz:
            for crossover_index, frequency_hz in enumerate(
                curve.crossover_frequencies_hz,
                start=1,
            ):
                if not math.isfinite(frequency_hz) or frequency_hz <= 0.0:
                    raise ValueError(
                        "crossover frequencies must be finite and positive."
                    )

                rows.append(
                    _build_summary_row(
                        scope="curve",
                        curve_index=str(curve_index),
                        curve_label=curve.label,
                        record_type="crossover",
                        item_name="crossover_frequency",
                        item_index=str(crossover_index),
                        value=_format_value(frequency_hz),
                        unit="Hz",
                        status="ok",
                    )
                )
        else:
            rows.append(
                _build_summary_row(
                    scope="curve",
                    curve_index=str(curve_index),
                    curve_label=curve.label,
                    record_type="crossover",
                    item_name="crossover_frequency",
                    item_index="0",
                    value="",
                    unit="Hz",
                    status="not_found",
                )
            )

    if optimization is not None:
        rows.extend(_build_optimization_rows(optimization))

    return rows


def build_curve_data_rows(
    curves: Sequence[CurveExportData],
) -> list[dict[str, str]]:
    """曲線データCSVへ書き込む縦持ち行を生成する。"""

    if not curves:
        raise ValueError("At least one simulation curve is required.")

    rows: list[dict[str, str]] = []

    for curve_index, curve in enumerate(curves, start=1):
        _validate_curve(curve)

        for point_index, (frequency_hz, re_k) in enumerate(
            zip(curve.frequencies, curve.values, strict=True),
            start=1,
        ):
            rows.append(
                {
                    "curve_index": str(curve_index),
                    "curve_label": curve.label,
                    "point_index": str(point_index),
                    "frequency_hz": _format_value(float(frequency_hz)),
                    "re_k": _format_value(float(re_k)),
                }
            )

    return rows


def save_simulation_csv_files(
    base_path: str | Path,
    curves: Sequence[CurveExportData],
    optimization: OptimizationSnapshot | None = None,
) -> tuple[Path, Path]:
    """1回の保存処理でsummary CSVとcurve data CSVを生成する。"""

    summary_path, curve_data_path = derive_csv_paths(base_path)

    # 両方の行を先に生成し、入力不正時に片方だけ保存されることを防ぐ。
    summary_rows = build_summary_rows(curves, optimization)
    curve_data_rows = build_curve_data_rows(curves)

    saved_paths: list[Path] = []

    try:
        _write_csv(summary_path, SUMMARY_FIELDNAMES, summary_rows)
        saved_paths.append(summary_path)

        _write_csv(curve_data_path, CURVE_DATA_FIELDNAMES, curve_data_rows)
        saved_paths.append(curve_data_path)
    except Exception as error:
        raise CsvExportError(
            str(error),
            summary_path=summary_path,
            curve_data_path=curve_data_path,
            saved_paths=tuple(saved_paths),
        ) from error

    return summary_path, curve_data_path


def _build_summary_row(
    *,
    scope: str,
    curve_index: str,
    curve_label: str,
    record_type: str,
    item_name: str,
    item_index: str,
    value: str,
    unit: str,
    status: str,
) -> dict[str, str]:
    return {
        "scope": scope,
        "curve_index": curve_index,
        "curve_label": curve_label,
        "record_type": record_type,
        "item_name": item_name,
        "item_index": item_index,
        "value": value,
        "unit": unit,
        "status": status,
    }


def _build_optimization_rows(
    optimization: OptimizationSnapshot,
) -> list[dict[str, str]]:
    numeric_values = (
        optimization.frequency_hz,
        optimization.value_1,
        optimization.value_2,
        optimization.difference,
    )

    if not all(math.isfinite(value) for value in numeric_values):
        raise ValueError("optimization values must be finite.")

    if optimization.frequency_hz <= 0.0:
        raise ValueError("optimization frequency must be positive.")

    items = (
        ("mode", optimization.mode, ""),
        ("frequency", _format_value(optimization.frequency_hz), "Hz"),
        ("curve_1_label", optimization.curve_1_label, ""),
        ("curve_1_re_k", _format_value(optimization.value_1), ""),
        ("curve_2_label", optimization.curve_2_label, ""),
        ("curve_2_re_k", _format_value(optimization.value_2), ""),
        ("difference", _format_value(optimization.difference), ""),
    )

    return [
        _build_summary_row(
            scope="graph",
            curve_index="",
            curve_label="",
            record_type="optimization",
            item_name=item_name,
            item_index="1",
            value=value,
            unit=unit,
            status="ok",
        )
        for item_name, value, unit in items
    ]


def _validate_curve(curve: CurveExportData) -> None:
    if not curve.label.strip():
        raise ValueError("curve label must not be empty.")

    if curve.frequencies.ndim != 1 or curve.values.ndim != 1:
        raise ValueError("curve frequencies and values must be one-dimensional.")

    if curve.frequencies.size == 0:
        raise ValueError("curve frequencies must not be empty.")

    if curve.frequencies.shape != curve.values.shape:
        raise ValueError("curve frequencies and values must have the same shape.")

    if not np.all(np.isfinite(curve.frequencies)):
        raise ValueError("curve frequencies must contain only finite values.")

    if not np.all(np.isfinite(curve.values)):
        raise ValueError("curve values must contain only finite values.")

    if np.any(curve.frequencies <= 0.0):
        raise ValueError("curve frequencies must be positive.")


def _format_value(value: ParameterValue) -> str:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("CSV values must be finite.")
        return format(value, ".17g")

    return str(value)


def _write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)
