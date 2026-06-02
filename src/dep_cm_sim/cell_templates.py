from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CellTemplate:
    name: str
    membrane_capacitance: float
    radius_m: float
    eps_c_relative: float
    sigma_c: float
    description: str = ""


def get_default_cell_templates() -> list[CellTemplate]:
    return [
        CellTemplate(
            name="reference_cell",
            membrane_capacitance=0.015,
            radius_m=6.7e-6,
            eps_c_relative=60.0,
            sigma_c=0.5,
            description="Default reference cell parameter set based on the reference Figure 1 conditions.",
        )
    ]


def validate_cell_template(template: CellTemplate) -> None:
    if not template.name.strip():
        raise ValueError("Cell template name must not be empty.")

    if template.membrane_capacitance <= 0:
        raise ValueError("membrane_capacitance must be greater than 0.")

    if template.radius_m <= 0:
        raise ValueError("radius_m must be greater than 0.")

    if template.eps_c_relative <= 0:
        raise ValueError("eps_c_relative must be greater than 0.")

    if template.sigma_c <= 0:
        raise ValueError("sigma_c must be greater than 0.")


def save_cell_templates_to_json(
    templates: list[CellTemplate],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for template in templates:
        validate_cell_template(template)

    data = {"templates": [asdict(template) for template in templates]}

    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_cell_templates_from_json(
    input_path: str | Path,
) -> list[CellTemplate]:
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Cell template file not found: {input_path}")

    data = json.loads(input_path.read_text(encoding="utf-8"))

    if "templates" not in data:
        raise ValueError("JSON must contain a 'templates' field.")

    templates: list[CellTemplate] = []

    for raw_template in data["templates"]:
        template = CellTemplate(
            name=str(raw_template["name"]),
            membrane_capacitance=float(raw_template["membrane_capacitance"]),
            radius_m=float(raw_template["radius_m"]),
            eps_c_relative=float(raw_template["eps_c_relative"]),
            sigma_c=float(raw_template["sigma_c"]),
            description=str(raw_template.get("description", "")),
        )
        validate_cell_template(template)
        templates.append(template)

    return templates


def find_cell_template_by_name(
    templates: list[CellTemplate],
    name: str,
) -> CellTemplate | None:
    for template in templates:
        if template.name == name:
            return template

    return None


USER_CELL_TEMPLATES_PATH = Path("templates/user_cell_templates.json")


def load_user_cell_templates(
    input_path: str | Path = USER_CELL_TEMPLATES_PATH,
) -> list[CellTemplate]:
    input_path = Path(input_path)

    if not input_path.exists():
        return []

    return load_cell_templates_from_json(input_path)


def load_available_cell_templates(
    user_template_path: str | Path = USER_CELL_TEMPLATES_PATH,
) -> list[CellTemplate]:
    templates = get_default_cell_templates()
    templates.extend(load_user_cell_templates(user_template_path))
    return templates


def save_user_cell_template(
    template: CellTemplate,
    output_path: str | Path = USER_CELL_TEMPLATES_PATH,
) -> list[CellTemplate]:
    output_path = Path(output_path)

    templates = load_user_cell_templates(output_path)

    existing_index = find_cell_template_index_by_name(templates, template.name)

    if existing_index is None:
        templates.append(template)
    else:
        templates[existing_index] = template

    save_cell_templates_to_json(templates, output_path)

    return templates


def find_cell_template_index_by_name(
    templates: list[CellTemplate],
    name: str,
) -> int | None:
    for index, template in enumerate(templates):
        if template.name == name:
            return index

    return None
