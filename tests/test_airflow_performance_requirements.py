"""
Focused regression checks for optional airflow
performance requirements.
"""
 
from core.parser import parse_requirements
from core.validator import review_requirements
from models.requirements import (
    EngineeringRequirements,
    Requirements,
)
from llm.mock_provider import MockProvider
 
 
# --------------------------------------------------
# Model defaults
# --------------------------------------------------
 
default_requirements = Requirements()
 
assert (
    default_requirements.maximum_pressure_drop
    is None
)
 
assert (
    default_requirements.maximum_pumping_power
    is None
)
 
 
# --------------------------------------------------
# Parser preserves supplied limits
# --------------------------------------------------
 
parsed = parse_requirements(
    {
        "component_type": "heat_sink",
        "convection_mode": "forced",
        "requirements": {
            "heat_load": 165.0,
            "ambient_temperature": 30.0,
            "maximum_base_temperature": 100.0,
            "maximum_pressure_drop": 80.0,
            "maximum_pumping_power": 0.25,
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
    parsed.requirements.maximum_pressure_drop
    == 80.0
)
 
assert (
    parsed.requirements.maximum_pumping_power
    == 0.25
)
 
 
# --------------------------------------------------
# Missing limits remain optional
# --------------------------------------------------
 
missing_limits = parse_requirements(
    {
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
            "max_height": 30.0,
        },
    }
)
 
assert (
    missing_limits
    .requirements
    .maximum_pressure_drop
    is None
)
 
assert (
    missing_limits
    .requirements
    .maximum_pumping_power
    is None
)
 
missing_review = review_requirements(
    missing_limits
)
 
assert not any(
    question.field_name
    in {
        "maximum_pressure_drop",
        "maximum_pumping_power",
    }
    for question in (
        missing_review.clarification_questions
    )
)
 
 
# --------------------------------------------------
# Valid limits pass review
# --------------------------------------------------
 
valid_requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
    requirements=Requirements(
        heat_load=165.0,
        ambient_temperature=30.0,
        maximum_pressure_drop=80.0,
        maximum_pumping_power=0.25,
        air_velocity=5.0,
    ),
    constraints=parsed.constraints,
)
 
valid_review = review_requirements(
    valid_requirements
)
 
assert not any(
    "pressure drop"
    in error.lower()
    for error in valid_review.validation_errors
)
 
assert not any(
    "pumping power"
    in error.lower()
    for error in valid_review.validation_errors
)
 
 
# --------------------------------------------------
# Invalid pressure-drop limit
# --------------------------------------------------
 
invalid_pressure_drop = (
    EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        requirements=Requirements(
            heat_load=165.0,
            ambient_temperature=30.0,
            maximum_pressure_drop=-1.0,
            maximum_pumping_power=0.25,
            air_velocity=5.0,
        ),
        constraints=parsed.constraints,
    )
)
 
invalid_pressure_review = review_requirements(
    invalid_pressure_drop
)
 
assert (
    "Maximum pressure drop must be greater "
    "than 0 Pa."
    in invalid_pressure_review.validation_errors
)
 
 
# --------------------------------------------------
# Invalid pumping-power limit
# --------------------------------------------------
 
invalid_pumping_power = (
    EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        requirements=Requirements(
            heat_load=165.0,
            ambient_temperature=30.0,
            maximum_pressure_drop=80.0,
            maximum_pumping_power=0.0,
            air_velocity=5.0,
        ),
        constraints=parsed.constraints,
    )
)
 
invalid_power_review = review_requirements(
    invalid_pumping_power
)
 
assert (
    "Maximum pumping power must be greater "
    "than 0 W."
    in invalid_power_review.validation_errors
)
 
 
# --------------------------------------------------
# Parser zero placeholders remain missing
# --------------------------------------------------
 
zero_placeholders = parse_requirements(
    {
        "requirements": {
            "maximum_pressure_drop": 0.0,
            "maximum_pumping_power": 0.0,
        }
    }
)
 
assert (
    zero_placeholders
    .requirements
    .maximum_pressure_drop
    is None
)
 
assert (
    zero_placeholders
    .requirements
    .maximum_pumping_power
    is None
)

# --------------------------------------------------
# Requirement extraction preserves optional limits
# --------------------------------------------------
mock_extracted = MockProvider().extract_requirements(
    (
        "Design a 165 W heat sink under forced convection. "
        "Ambient temperature is 30 C. Air velocity is 5 m/s. "
        "Base is 50 x 50 mm. Maximum height is 30 mm. "
        "Maximum base temperature: 105 C. "
        "Maximum pressure drop: 25 Pa. "
        "Maximum pumping power: 0.1 W."
    )
)
mock_parsed = parse_requirements(
    mock_extracted
)
assert (
    mock_parsed
    .requirements
    .maximum_base_temperature
    == 105.0
)
assert (
    mock_parsed
    .requirements
    .maximum_pressure_drop
    == 25.0
)
assert (
    mock_parsed
    .requirements
    .maximum_pumping_power
    == 0.1
)
 
 
print(
    "ALL AIRFLOW PERFORMANCE REQUIREMENT "
    "CHECKS PASSED"
)