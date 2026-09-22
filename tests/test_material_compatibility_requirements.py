"""
Focused regression checks for optional allowed-material
requirements.
"""
 
from core.parser import parse_requirements
from core.validator import review_requirements
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
from llm.mock_provider import MockProvider
 
 
# --------------------------------------------------
# Default material restriction
# --------------------------------------------------
 
default_requirements = EngineeringRequirements()
 
assert (
    default_requirements.allowed_materials
    == ()
)
 
 
# --------------------------------------------------
# Parser accepts a material list
# --------------------------------------------------
 
parsed_list = parse_requirements(
    {
        "component_type": "heat_sink",
        "convection_mode": "forced",
        "allowed_materials": [
            "Al6063",
            "Al6061",
        ],
        "requirements": {
            "heat_load": 165.0,
            "ambient_temperature": 30.0,
            "maximum_base_temperature": 105.0,
            "maximum_pressure_drop": 25.0,
            "maximum_pumping_power": 0.10,
            "air_velocity": 5.0,
        },
        "constraints": {
            "base_length": 50.0,
            "base_width": 50.0,
            "max_height": 30.0,
        },
    }
)
 
assert (
    parsed_list.allowed_materials
    == (
        "Al6063",
        "Al6061",
    )
)
 
 
# --------------------------------------------------
# Parser accepts a comma-separated string
# --------------------------------------------------
 
parsed_string = parse_requirements(
    {
        "allowed_materials": (
            "Al6063, Al6061, Copper C110"
        ),
    }
)
 
assert (
    parsed_string.allowed_materials
    == (
        "Al6063",
        "Al6061",
        "Copper C110",
    )
)
 
 
# --------------------------------------------------
# Empty and missing inputs remain unrestricted
# --------------------------------------------------
 
missing_materials = parse_requirements(
    {}
)
 
assert (
    missing_materials.allowed_materials
    == ()
)
 
empty_materials = parse_requirements(
    {
        "allowed_materials": [],
    }
)
 
assert (
    empty_materials.allowed_materials
    == ()
)
 
placeholder_materials = parse_requirements(
    {
        "allowed_materials": [
            "",
            "unknown",
            "not provided",
        ],
    }
)
 
assert (
    placeholder_materials.allowed_materials
    == ()
)
 
 
# --------------------------------------------------
# Duplicate entries are removed
# --------------------------------------------------
 
duplicate_materials = parse_requirements(
    {
        "allowed_materials": [
            "Al6063",
            "Al6063",
            "Al6061",
        ],
    }
)
 
assert (
    duplicate_materials.allowed_materials
    == (
        "Al6063",
        "Al6061",
    )
)
 
 
# --------------------------------------------------
# Valid material requirements pass review
# --------------------------------------------------
 
valid_review = review_requirements(
    parsed_list
)
 
assert not any(
    "allowed material"
    in error.lower()
    for error in valid_review.validation_errors
)
 
 
# --------------------------------------------------
# Missing restriction creates no clarification
# --------------------------------------------------
 
missing_review = review_requirements(
    missing_materials
)
 
assert not any(
    question.field_name
    == "allowed_materials"
    for question in (
        missing_review.clarification_questions
    )
)
 
 
# --------------------------------------------------
# Direct invalid tuple values are rejected
# --------------------------------------------------
 
invalid_name_requirements = (
    EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        allowed_materials=(
            "Al6063",
            "",
        ),
        requirements=Requirements(),
        constraints=Constraints(),
    )
)
 
invalid_name_review = review_requirements(
    invalid_name_requirements
)
 
assert (
    "Allowed material names must not be empty."
    in invalid_name_review.validation_errors
)

# --------------------------------------------------
# Mock extraction preserves explicit materials
# --------------------------------------------------
mock_material_input = (
    MockProvider().extract_requirements(
        (
            "Design a forced-convection heat sink. "
            "Allowed materials: Al6063, Al6061."
        )
    )
)
mock_material_requirements = (
    parse_requirements(
        mock_material_input
    )
)
assert (
    mock_material_requirements.allowed_materials
    == (
        "al6063",
        "al6061",
    )
)
# --------------------------------------------------
# Unsupported material-only restriction is rejected
# --------------------------------------------------
unsupported_material_requirements = (
    EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        allowed_materials=(
            "Copper C110",
        ),
        requirements=Requirements(),
        constraints=Constraints(),
    )
)
unsupported_material_review = (
    review_requirements(
        unsupported_material_requirements
    )
)
assert (
    "The current V2 optimizer supports "
    "Aluminium 6063-T5 only. The supplied "
    "allowed materials exclude the currently "
    "supported design material."
    in unsupported_material_review.validation_errors
)
 
 
print(
    "ALL MATERIAL COMPATIBILITY REQUIREMENT "
    "CHECKS PASSED"
)