"""
Focused checks for the explicit maximum allowable
base-temperature requirement.
"""
 
from core.parser import (
    parse_requirements,
)
from core.validator import (
    review_requirements,
)
 
 
def create_input(
    *,
    ambient_temperature: float = 30.0,
    maximum_base_temperature=None,
) -> dict:
    """
    Create one complete structured requirement input.
    """
 
    return {
        "component_type": "heat_sink",
        "convection_mode": "forced",
        "requirements": {
            "heat_load": 165.0,
            "ambient_temperature": (
                ambient_temperature
            ),
            "maximum_base_temperature": (
                maximum_base_temperature
            ),
            "air_velocity": 5.0,
        },
        "constraints": {
            "base_length": 50.0,
            "base_width": 50.0,
            "max_height": 30.0,
        },
    }
 
 
# --------------------------------------------------
# Valid supplied temperature limit
# --------------------------------------------------
 
valid_engineering = parse_requirements(
    create_input(
        ambient_temperature=30.0,
        maximum_base_temperature=100.0,
    )
)
 
assert (
    valid_engineering
    .requirements
    .maximum_base_temperature
    == 100.0
)
 
valid_review = review_requirements(
    valid_engineering
)
 
assert not any(
    "Maximum base temperature"
    in error
    for error in valid_review.validation_errors
)
 
 
# --------------------------------------------------
# Missing limit remains optional
# --------------------------------------------------
 
missing_engineering = parse_requirements(
    create_input(
        ambient_temperature=30.0,
        maximum_base_temperature=None,
    )
)
 
assert (
    missing_engineering
    .requirements
    .maximum_base_temperature
    is None
)
 
missing_review = review_requirements(
    missing_engineering
)
 
assert not any(
    question.field_name
    == "maximum_base_temperature"
    for question
    in missing_review.clarification_questions
)
 
assert not any(
    "Maximum base temperature"
    in error
    for error in missing_review.validation_errors
)
 
 
# --------------------------------------------------
# Limit equal to ambient is invalid
# --------------------------------------------------
 
equal_engineering = parse_requirements(
    create_input(
        ambient_temperature=30.0,
        maximum_base_temperature=30.0,
    )
)
 
equal_review = review_requirements(
    equal_engineering
)
 
assert (
    "Maximum base temperature must be greater "
    "than ambient temperature."
    in equal_review.validation_errors
)
 
 
# --------------------------------------------------
# Limit below ambient is invalid
# --------------------------------------------------
 
below_engineering = parse_requirements(
    create_input(
        ambient_temperature=30.0,
        maximum_base_temperature=25.0,
    )
)
 
below_review = review_requirements(
    below_engineering
)
 
assert (
    "Maximum base temperature must be greater "
    "than ambient temperature."
    in below_review.validation_errors
)
 
 
# --------------------------------------------------
# Absolute-zero protection
# --------------------------------------------------
 
absolute_zero_engineering = parse_requirements(
    create_input(
        ambient_temperature=-40.0,
        maximum_base_temperature=-273.15,
    )
)
 
absolute_zero_review = review_requirements(
    absolute_zero_engineering
)
 
assert (
    "Maximum base temperature must be above "
    "absolute zero."
    in absolute_zero_review.validation_errors
)
 
 
# --------------------------------------------------
# String-form numerical input
# --------------------------------------------------
 
string_input = create_input()
 
string_input["requirements"][
    "maximum_base_temperature"
] = "95"
 
string_engineering = parse_requirements(
    string_input
)
 
assert (
    string_engineering
    .requirements
    .maximum_base_temperature
    == 95.0
)
 
 
# --------------------------------------------------
# Blank input normalizes to None
# --------------------------------------------------
 
blank_input = create_input()
 
blank_input["requirements"][
    "maximum_base_temperature"
] = ""
 
blank_engineering = parse_requirements(
    blank_input
)
 
assert (
    blank_engineering
    .requirements
    .maximum_base_temperature
    is None
)
 
 
print(
    "ALL THERMAL TEMPERATURE REQUIREMENT "
    "CHECKS PASSED"
)