from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from dep_cm_sim.experimental_data import (
    load_experimental_data_from_csv,
    validate_experimental_data,
)


def test_load_experimental_data_from_csv_with_label(tmp_path: Path) -> None:
    csv_path = tmp_path / "experiment.csv"
    csv_path.write_text(
        "frequency_hz,value,label\n"
        "1.0,0.1,exp_A\n"
        "10.0,0.2,exp_A\n",
        encoding="utf-8",
    )

    data = load_experimental_data_from_csv(csv_path)

    assert data.label == "exp_A"
    np.testing.assert_allclose(data.frequency_hz, np.array([1.0, 10.0]))
    np.testing.assert_allclose(data.values, np.array([0.1, 0.2]))


def test_load_experimental_data_from_csv_uses_file_stem_without_label(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "experiment_without_label.csv"
    csv_path.write_text(
        "frequency_hz,value\n"
        "1.0,0.1\n"
        "10.0,0.2\n",
        encoding="utf-8",
    )

    data = load_experimental_data_from_csv(csv_path)

    assert data.label == "experiment_without_label"
    np.testing.assert_allclose(data.frequency_hz, np.array([1.0, 10.0]))
    np.testing.assert_allclose(data.values, np.array([0.1, 0.2]))


def test_load_experimental_data_from_csv_rejects_missing_required_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text(
        "frequency_hz,response\n"
        "1.0,0.1\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing required columns"):
        load_experimental_data_from_csv(csv_path)


def test_load_experimental_data_from_csv_rejects_empty_data(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text(
        "frequency_hz,value\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="must not be empty"):
        load_experimental_data_from_csv(csv_path)


def test_load_experimental_data_from_csv_rejects_non_numeric_value(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text(
        "frequency_hz,value\n"
        "1.0,abc\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-numeric"):
        load_experimental_data_from_csv(csv_path)


def test_validate_experimental_data_rejects_non_positive_frequency() -> None:
    with pytest.raises(ValueError, match="frequency_hz must be positive"):
        validate_experimental_data(
            frequency_hz=np.array([0.0, 10.0]),
            values=np.array([0.1, 0.2]),
            label="exp",
        )


def test_validate_experimental_data_rejects_nan_frequency() -> None:
    with pytest.raises(ValueError, match="frequency_hz must not contain NaN"):
        validate_experimental_data(
            frequency_hz=np.array([1.0, np.nan]),
            values=np.array([0.1, 0.2]),
            label="exp",
        )


def test_validate_experimental_data_rejects_nan_value() -> None:
    with pytest.raises(ValueError, match="values must not contain NaN"):
        validate_experimental_data(
            frequency_hz=np.array([1.0, 10.0]),
            values=np.array([0.1, np.nan]),
            label="exp",
        )


def test_validate_experimental_data_rejects_empty_label() -> None:
    with pytest.raises(ValueError, match="label must not be empty"):
        validate_experimental_data(
            frequency_hz=np.array([1.0, 10.0]),
            values=np.array([0.1, 0.2]),
            label="",
        )


def test_load_experimental_data_from_csv_with_plot_style(tmp_path: Path) -> None:
    csv_path = tmp_path / "experiment_line.csv"
    csv_path.write_text(
        "frequency_hz,value,label,plot_style\n"
        "1.0,0.1,exp_A,line\n"
        "10.0,0.2,exp_A,line\n",
        encoding="utf-8",
    )

    data = load_experimental_data_from_csv(csv_path)

    assert data.label == "exp_A"
    assert data.plot_style == "line"


def test_load_experimental_data_from_csv_uses_scatter_as_default_plot_style(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "experiment_default_style.csv"
    csv_path.write_text(
        "frequency_hz,value,label\n"
        "1.0,0.1,exp_A\n"
        "10.0,0.2,exp_A\n",
        encoding="utf-8",
    )

    data = load_experimental_data_from_csv(csv_path)

    assert data.plot_style == "scatter"


def test_validate_experimental_data_rejects_invalid_plot_style() -> None:
    with pytest.raises(ValueError, match="plot_style"):
        validate_experimental_data(
            frequency_hz=np.array([1.0, 10.0]),
            values=np.array([0.1, 0.2]),
            label="exp",
            plot_style="invalid",
        )


def test_save_experimental_data_to_csv_and_load_again(tmp_path: Path) -> None:
    from dep_cm_sim.experimental_data import (
        ExperimentalData,
        save_experimental_data_to_csv,
    )

    csv_path = tmp_path / "saved_experiment.csv"

    data = ExperimentalData(
        frequency_hz=np.array([1.0, 10.0, 100.0]),
        values=np.array([0.1, 0.2, 0.3]),
        label="saved_exp",
        plot_style="scatter_line",
    )

    save_experimental_data_to_csv(data, csv_path)
    loaded = load_experimental_data_from_csv(csv_path)

    assert loaded.label == "saved_exp"
    assert loaded.plot_style == "scatter_line"
    np.testing.assert_allclose(loaded.frequency_hz, data.frequency_hz)
    np.testing.assert_allclose(loaded.values, data.values)
