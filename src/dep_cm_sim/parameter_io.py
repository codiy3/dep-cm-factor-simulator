from __future__ import annotations

import csv
from pathlib import Path


ParameterValue = float | int
ParameterDict = dict[str, ParameterValue]


def save_parameters_to_csv(
    parameters: ParameterDict,
    output_path: str | Path,
) -> None:
    """
    パラメータ辞書をCSVファイルへ保存する。

    CSV format:
        key,value
        membrane_capacitance,0.015
        radius_m,6.7e-6
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["key", "value"])

        for key, value in parameters.items():
            writer.writerow([key, value])


def load_parameters_from_csv(
    input_path: str | Path,
) -> ParameterDict:
    """
    CSVファイルからパラメータ辞書を読み込む。

    value は基本的に float として読み込む。
    num_points のみ int として扱う。
    """

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"CSV file not found: {input_path}")

    parameters: ParameterDict = {}

    with input_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames != ["key", "value"]:
            raise ValueError("CSV header must be: key,value")

        for row in reader:
            key = row["key"]
            raw_value = row["value"]

            if key == "num_points":
                parameters[key] = int(float(raw_value))
            else:
                parameters[key] = float(raw_value)

    return parameters
