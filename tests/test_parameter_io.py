from pathlib import Path

import pytest

from dep_cm_sim.parameter_io import load_parameters_from_csv, save_parameters_to_csv


def test_save_and_load_parameters_to_csv(tmp_path: Path) -> None:
    parameters = {
        "graph_label": "HL60_default",
        "membrane_capacitance": 0.015,
        "radius_m": 6.7e-6,
        "eps_c_relative": 60.0,
        "eps_s_relative": 80.0,
        "sigma_c": 0.5,
        "sigma_s": 2.0e-4,
        "f_min": 1.0,
        "f_max": 1.0e10,
        "num_points": 1000,
    }

    output_path = tmp_path / "parameters.csv"

    save_parameters_to_csv(parameters, output_path)
    loaded_parameters = load_parameters_from_csv(output_path)

    assert loaded_parameters == parameters


def test_save_and_load_parameters_to_csv_accepts_empty_graph_label(tmp_path: Path) -> None:
    parameters = {
        "graph_label": "",
        "membrane_capacitance": 0.015,
        "radius_m": 6.7e-6,
        "eps_c_relative": 60.0,
        "eps_s_relative": 80.0,
        "sigma_c": 0.5,
        "sigma_s": 2.0e-4,
        "f_min": 1.0,
        "f_max": 1.0e10,
        "num_points": 1000,
    }

    output_path = tmp_path / "parameters.csv"

    save_parameters_to_csv(parameters, output_path)
    loaded_parameters = load_parameters_from_csv(output_path)

    assert loaded_parameters["graph_label"] == ""


def test_load_parameters_from_csv_rejects_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_parameters_from_csv(missing_path)


def test_load_parameters_from_csv_rejects_invalid_header(tmp_path: Path) -> None:
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("name,value\nsigma_s,0.001\n", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV header must be"):
        load_parameters_from_csv(invalid_csv)
