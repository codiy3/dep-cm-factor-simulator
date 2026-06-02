from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


ALLOWED_EXPERIMENTAL_PLOT_STYLES = {"scatter", "line", "scatter_line"}


@dataclass(frozen=True)
class ExperimentalData:
    frequency_hz: NDArray[np.float64]
    values: NDArray[np.float64]
    label: str
    plot_style: str = "scatter"


def load_experimental_data_from_csv(path: str | Path) -> ExperimentalData:
    csv_path = Path(path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Experimental data CSV not found: {csv_path}")

    frequencies: list[float] = []
    values: list[float] = []
    labels: list[str] = []
    plot_styles: list[str] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Experimental data CSV must have a header row.")

        required_columns = {"frequency_hz", "value"}
        missing_columns = required_columns - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(
                "Experimental data CSV is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        for row_number, row in enumerate(reader, start=2):
            frequency_text = row.get("frequency_hz", "").strip()
            value_text = row.get("value", "").strip()

            if not frequency_text or not value_text:
                raise ValueError(
                    "Experimental data CSV has empty frequency_hz or value "
                    f"at row {row_number}."
                )

            try:
                frequency = float(frequency_text)
                value = float(value_text)
            except ValueError as error:
                raise ValueError(
                    f"Experimental data CSV has non-numeric data at row {row_number}."
                ) from error

            frequencies.append(frequency)
            values.append(value)

            label_text = row.get("label", "").strip()
            if label_text:
                labels.append(label_text)

            plot_style_text = row.get("plot_style", "").strip()
            if plot_style_text:
                plot_styles.append(plot_style_text)

    frequency_array = np.array(frequencies, dtype=np.float64)
    value_array = np.array(values, dtype=np.float64)
    label = labels[0] if labels else csv_path.stem
    plot_style = plot_styles[0] if plot_styles else "scatter"

    validate_experimental_data(
        frequency_hz=frequency_array,
        values=value_array,
        label=label,
        plot_style=plot_style,
    )

    return ExperimentalData(
        frequency_hz=frequency_array,
        values=value_array,
        label=label,
        plot_style=plot_style,
    )


def validate_experimental_data(
    frequency_hz: NDArray[np.float64],
    values: NDArray[np.float64],
    label: str,
    plot_style: str = "scatter",
) -> None:
    if frequency_hz.size == 0:
        raise ValueError("Experimental data must not be empty.")

    if frequency_hz.shape != values.shape:
        raise ValueError("frequency_hz and values must have the same shape.")

    if np.isnan(frequency_hz).any():
        raise ValueError("frequency_hz must not contain NaN.")

    if np.any(frequency_hz <= 0):
        raise ValueError("frequency_hz must be positive.")

    if np.isnan(values).any():
        raise ValueError("values must not contain NaN.")

    if not label.strip():
        raise ValueError("label must not be empty.")

    if plot_style not in ALLOWED_EXPERIMENTAL_PLOT_STYLES:
        raise ValueError(
            "plot_style must be one of: "
            + ", ".join(sorted(ALLOWED_EXPERIMENTAL_PLOT_STYLES))
        )
