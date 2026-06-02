from pathlib import Path

import pytest

from dep_cm_sim.cell_templates import (
    CellTemplate,
    find_cell_template_by_name,
    get_default_cell_templates,
    load_cell_templates_from_json,
    load_available_cell_templates,
    load_user_cell_templates,
    save_cell_templates_to_json,
    save_user_cell_template,
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



def test_load_user_cell_templates_returns_empty_list_when_file_missing(
    tmp_path: Path,
) -> None:
    missing_path = tmp_path / "user_cell_templates.json"

    templates = load_user_cell_templates(missing_path)

    assert templates == []


def test_load_available_cell_templates_includes_default_and_user_templates(
    tmp_path: Path,
) -> None:
    user_template_path = tmp_path / "user_cell_templates.json"
    user_template = CellTemplate(
        name="condition_B_cell",
        membrane_capacitance=0.02,
        radius_m=7.0e-6,
        eps_c_relative=55.0,
        sigma_c=0.4,
    )

    save_cell_templates_to_json([user_template], user_template_path)

    templates = load_available_cell_templates(user_template_path)

    assert find_cell_template_by_name(templates, "reference_cell") is not None
    assert find_cell_template_by_name(templates, "condition_B_cell") == user_template


def test_save_user_cell_template_adds_new_template(tmp_path: Path) -> None:
    user_template_path = tmp_path / "user_cell_templates.json"
    template = CellTemplate(
        name="condition_C_cell",
        membrane_capacitance=0.02,
        radius_m=8.0e-6,
        eps_c_relative=50.0,
        sigma_c=0.3,
    )

    templates = save_user_cell_template(template, user_template_path)

    assert templates == [template]
    assert load_user_cell_templates(user_template_path) == [template]


def test_save_user_cell_template_overwrites_existing_template(tmp_path: Path) -> None:
    user_template_path = tmp_path / "user_cell_templates.json"
    original_template = CellTemplate(
        name="condition_D_cell",
        membrane_capacitance=0.02,
        radius_m=8.0e-6,
        eps_c_relative=50.0,
        sigma_c=0.3,
    )
    updated_template = CellTemplate(
        name="condition_D_cell",
        membrane_capacitance=0.03,
        radius_m=9.0e-6,
        eps_c_relative=45.0,
        sigma_c=0.2,
    )

    save_user_cell_template(original_template, user_template_path)
    templates = save_user_cell_template(updated_template, user_template_path)

    assert templates == [updated_template]
    assert load_user_cell_templates(user_template_path) == [updated_template]
