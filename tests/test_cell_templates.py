from pathlib import Path

import pytest

from dep_cm_sim.cell_templates import (
    CellTemplate,
    find_cell_template_by_name,
    get_default_cell_templates,
    load_cell_templates_from_json,
    save_cell_templates_to_json,
    validate_cell_template,
)


def test_get_default_cell_templates_returns_reference_cell() -> None:
    templates = get_default_cell_templates()

    assert len(templates) == 1
    assert templates[0].name == "reference_cell"
    assert templates[0].membrane_capacitance == 0.015
    assert templates[0].radius_m == 6.7e-6
    assert templates[0].eps_c_relative == 60.0
    assert templates[0].sigma_c == 0.5


def test_save_and_load_cell_templates_to_json(tmp_path: Path) -> None:
    templates = [
        CellTemplate(
            name="condition_A_cell",
            membrane_capacitance=0.015,
            radius_m=6.7e-6,
            eps_c_relative=60.0,
            sigma_c=0.5,
            description="Test cell template",
        )
    ]

    output_path = tmp_path / "cell_templates.json"

    save_cell_templates_to_json(templates, output_path)
    loaded_templates = load_cell_templates_from_json(output_path)

    assert loaded_templates == templates


def test_load_cell_templates_from_json_rejects_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing_cell_templates.json"

    with pytest.raises(FileNotFoundError):
        load_cell_templates_from_json(missing_path)


def test_load_cell_templates_from_json_rejects_missing_templates_field(
    tmp_path: Path,
) -> None:
    invalid_json = tmp_path / "invalid_cell_templates.json"
    invalid_json.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="templates"):
        load_cell_templates_from_json(invalid_json)


@pytest.mark.parametrize(
    ("template", "message"),
    [
        (
            CellTemplate(
                name="",
                membrane_capacitance=0.015,
                radius_m=6.7e-6,
                eps_c_relative=60.0,
                sigma_c=0.5,
            ),
            "name",
        ),
        (
            CellTemplate(
                name="invalid_cell",
                membrane_capacitance=0.0,
                radius_m=6.7e-6,
                eps_c_relative=60.0,
                sigma_c=0.5,
            ),
            "membrane_capacitance",
        ),
        (
            CellTemplate(
                name="invalid_cell",
                membrane_capacitance=0.015,
                radius_m=0.0,
                eps_c_relative=60.0,
                sigma_c=0.5,
            ),
            "radius_m",
        ),
        (
            CellTemplate(
                name="invalid_cell",
                membrane_capacitance=0.015,
                radius_m=6.7e-6,
                eps_c_relative=0.0,
                sigma_c=0.5,
            ),
            "eps_c_relative",
        ),
        (
            CellTemplate(
                name="invalid_cell",
                membrane_capacitance=0.015,
                radius_m=6.7e-6,
                eps_c_relative=60.0,
                sigma_c=0.0,
            ),
            "sigma_c",
        ),
    ],
)
def test_validate_cell_template_rejects_invalid_values(
    template: CellTemplate,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        validate_cell_template(template)


def test_find_cell_template_by_name_returns_matching_template() -> None:
    templates = [
        CellTemplate(
            name="condition_A_cell",
            membrane_capacitance=0.015,
            radius_m=6.7e-6,
            eps_c_relative=60.0,
            sigma_c=0.5,
        )
    ]

    template = find_cell_template_by_name(templates, "condition_A_cell")

    assert template == templates[0]


def test_find_cell_template_by_name_returns_none_for_missing_name() -> None:
    templates = get_default_cell_templates()

    template = find_cell_template_by_name(templates, "missing_cell")

    assert template is None
