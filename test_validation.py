"""
test_validation.py
 
Regression checks for the engineering requirement
parsing, review, and strict-validation boundaries.
 
Current contract:
 
raw data
    ↓
parse_requirements()
    Structural parsing only
    ↓
review_requirements()
    Clarifications, assumptions, validation errors
    ↓
validate_requirements()
    Strict raise-on-incomplete-or-invalid boundary
"""
 
from core.parser import parse_requirements
from core.validator import (
    RequirementsValidationError,
    review_requirements,
    validate_requirements,
)
 
 
def test_valid_case() -> None:
    """
    A complete valid requirement must parse, review,
    and pass strict validation.
    """
 
    data = {
        "component_type": "heat_sink",
        "convection_mode": "forced",
        "requirements": {
            "heat_load": 165.0,
            "ambient_temperature": 30.0,
            "air_velocity": 5.0,
        },
        "constraints": {
            "base_length": 50.0,
            "base_width": 50.0,
            "max_height": 25.0,
        },
    }
 
    engineering = parse_requirements(
        data
    )
 
    review = review_requirements(
        engineering
    )
 
    assert review.can_proceed
    assert not review.needs_clarification
    assert not review.has_validation_errors
 
    validated = validate_requirements(
        engineering
    )
 
    assert validated is engineering
 
    print(
        "VALID REQUIREMENT PIPELINE CHECK PASSED"
    )
 
 
def test_invalid_case() -> None:
    """
    Parsing must preserve the structurally parseable
    request, while engineering review and strict
    validation must reject its invalid values.
    """
 
    data = {
        "component_type": "heat_sink",
        "convection_mode": "forced",
        "requirements": {
            "heat_load": -100.0,
            "ambient_temperature": 150.0,
            "air_velocity": -2.0,
        },
        "constraints": {
            "base_length": -50.0,
            "base_width": -40.0,
            "max_height": -20.0,
        },
    }
 
    engineering = parse_requirements(
        data
    )
 
    # Structural parsing itself must not perform
    # engineering rejection.
    assert engineering.requirements.heat_load == -100.0
    assert engineering.constraints.base_length == -50.0
 
    review = review_requirements(
        engineering
    )
 
    assert review.has_validation_errors
    assert not review.can_proceed
 
    assert (
        "Heat load must be greater than 0 W."
        in review.validation_errors
    )
 
    assert (
        "Ambient temperature is above the currently "
        "supported range of 100 °C."
        in review.validation_errors
    )
 
    assert (
        "Base length must be greater than 0 mm."
        in review.validation_errors
    )
 
    assert (
        "Base width must be greater than 0 mm."
        in review.validation_errors
    )
 
    assert (
        "Maximum total height must be greater than 0 mm."
        in review.validation_errors
    )
 
    assert (
        "Air velocity must be greater than 0 m/s for "
        "forced convection."
        in review.validation_errors
    )
 
    try:
        validate_requirements(
            engineering
        )
 
    except RequirementsValidationError as exc:
        message = str(exc)
 
        assert (
            "Engineering requirements are not ready"
            in message
        )
 
        assert (
            "Heat load must be greater than 0 W."
            in message
        )
 
        print(
            "INVALID REQUIREMENT CORRECTLY "
            "REJECTED BY STRICT VALIDATION"
        )
 
    else:
        raise AssertionError(
            "Strict validation accepted invalid "
            "engineering requirements."
        )
 
 
def main() -> None:
    test_valid_case()
    test_invalid_case()
 
    print(
        "ALL REQUIREMENT VALIDATION BOUNDARY "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()