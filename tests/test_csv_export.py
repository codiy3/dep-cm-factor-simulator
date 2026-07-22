import csv
from pathlib import Path

import numpy as np
import pytest

from dep_cm_sim.csv_export import (
    CurveExportData,
    OptimizationSnapshot,
    ParameterSnapshot,
    build_curve_data_rows,
    build_summary_rows,
    derive_csv_paths,
    save_simulation_csv_files,
)


def make_curve(
    *,
    label: str = "curve A",
    frequencies: np.ndarray | None = None,
    values: np.ndarray | None = None,
    crossovers: tuple[float, ...] = (10.0,),
) -> CurveExportData:
    return CurveExportData(
        label=label,
        frequencies=(
            frequencies
            if frequencies is not None
            else np.array([1.0, 10.0, 100.0], dtype=np.float64)
        ),
        values=(
            values
            if values is not None
            else np.array([-0.5, 0.0, 0.5], dtype=np.float64)
        ),
        parameters=(
            ParameterSnapshot(
                key="sigma_s",
                name="溶液導電率",
                value=2.0e-4,
                unit="S/m",
            ),
        ),
        crossover_frequencies_hz=crossovers,
    )


def test_derive_csv_paths_from_csv_base_name() -> None:
    summary_path, curve_data_path = derive_csv_paths("outputs/experiment_01.csv")

    assert summary_path == Path("outputs/experiment_01_summary.csv")
    assert curve_data_path == Path("outputs/experiment_01_curve_data.csv")


def test_derive_csv_paths_adds_csv_suffix() -> None:
    summary_path, curve_data_path = derive_csv_paths("outputs/experiment_01")

    assert summary_path == Path("outputs/experiment_01_summary.csv")
    assert curve_data_path == Path("outputs/experiment_01_curve_data.csv")


def test_build_summary_rows_contains_parameters_and_multiple_crossovers() -> None:
    curve = make_curve(crossovers=(4.46e2, 1.34e8))

    rows = build_summary_rows([curve])

    parameter_rows = [
        row for row in rows if row["record_type"] == "parameter"
    ]
    crossover_rows = [
        row for row in rows if row["record_type"] == "crossover"
    ]

    assert parameter_rows == [
        {
            "scope": "curve",
            "curve_index": "1",
            "curve_label": "curve A",
            "record_type": "parameter",
            "item_name": "sigma_s",
            "item_index": "1",
            "value": "0.00020000000000000001",
            "unit": "S/m",
            "status": "ok",
        }
    ]

    assert [row["item_index"] for row in crossover_rows] == ["1", "2"]
    assert [float(row["value"]) for row in crossover_rows] == pytest.approx(
        [4.46e2, 1.34e8]
    )
    assert all(row["status"] == "ok" for row in crossover_rows)


def test_build_summary_rows_marks_missing_crossover() -> None:
    rows = build_summary_rows([make_curve(crossovers=())])

    crossover_row = next(
        row for row in rows if row["record_type"] == "crossover"
    )

    assert crossover_row["item_index"] == "0"
    assert crossover_row["value"] == ""
    assert crossover_row["unit"] == "Hz"
    assert crossover_row["status"] == "not_found"


def test_build_summary_rows_adds_optimization_only_when_provided() -> None:
    curve_1 = make_curve(label="cell A")
    curve_2 = make_curve(label="cell B")
    optimization = OptimizationSnapshot(
        mode="opposite_sign",
        frequency_hz=2.01e3,
        value_1=0.4,
        value_2=-0.3,
        difference=0.7,
        curve_1_label="cell A",
        curve_2_label="cell B",
    )

    rows_without_optimization = build_summary_rows([curve_1, curve_2])
    rows_with_optimization = build_summary_rows(
        [curve_1, curve_2],
        optimization,
    )

    assert not any(
        row["record_type"] == "optimization"
        for row in rows_without_optimization
    )

    optimization_rows = [
        row
        for row in rows_with_optimization
        if row["record_type"] == "optimization"
    ]

    assert {row["item_name"] for row in optimization_rows} == {
        "mode",
        "frequency",
        "curve_1_label",
        "curve_1_re_k",
        "curve_2_label",
        "curve_2_re_k",
        "difference",
    }


def test_build_curve_data_rows_supports_different_point_counts() -> None:
    curve_1 = make_curve()
    curve_2 = make_curve(
        label="curve B",
        frequencies=np.array([2.0, 20.0], dtype=np.float64),
        values=np.array([0.1, 0.2], dtype=np.float64),
        crossovers=(),
    )

    rows = build_curve_data_rows([curve_1, curve_2])

    assert len(rows) == 5
    assert [row["curve_index"] for row in rows] == ["1", "1", "1", "2", "2"]
    assert [row["point_index"] for row in rows] == ["1", "2", "3", "1", "2"]
    assert [float(row["frequency_hz"]) for row in rows] == pytest.approx(
        [1.0, 10.0, 100.0, 2.0, 20.0]
    )


def test_save_simulation_csv_files_uses_utf8_bom_and_csv_quoting(
    tmp_path: Path,
) -> None:
    label = '日本語, "quoted"'
    curve = make_curve(label=label)

    summary_path, curve_data_path = save_simulation_csv_files(
        tmp_path / "result.csv",
        [curve],
    )

    assert summary_path.exists()
    assert curve_data_path.exists()
    assert summary_path.read_bytes().startswith(b"\xef\xbb\xbf")
    assert curve_data_path.read_bytes().startswith(b"\xef\xbb\xbf")

    with curve_data_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(csv.DictReader(file))

    assert rows[0]["curve_label"] == label


def test_build_rows_rejects_empty_curve_list() -> None:
    with pytest.raises(ValueError, match="At least one simulation curve"):
        build_summary_rows([])

    with pytest.raises(ValueError, match="At least one simulation curve"):
        build_curve_data_rows([])


def test_build_curve_data_rows_rejects_mismatched_shapes() -> None:
    curve = make_curve(
        frequencies=np.array([1.0, 10.0], dtype=np.float64),
        values=np.array([0.1], dtype=np.float64),
    )

    with pytest.raises(ValueError, match="same shape"):
        build_curve_data_rows([curve])
