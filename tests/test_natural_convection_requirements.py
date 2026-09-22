"""
Regression checks for natural-convection requirement
parsing and deterministic validation.
"""
 
from core.parser import parse_requirements
from core.validator import review_requirements
 
 
def complete_natural_input() -> dict:
    """
    Return a complete natural-convection requirement
    dictionary without natural-convection configuration.
    """
 
    return {
        "component_type": "heat_sink",
        "convection_mode": "natural",
        "requirements": {
            "heat_load": 20.0,
            "ambient_temperature": 30.0,
            "air_velocity": None,
        },
        "constraints": {
            "base_length": 50.0,
            "base_width": 50.0,
            "max_height": 30.0,
        },
    }
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Legacy parsing remains configuration-free
    # --------------------------------------------------
 
    legacy_input = complete_natural_input()
 
    legacy_engineering = parse_requirements(
        legacy_input
    )
 
    assert (
        legacy_engineering.natural_convection
        is None
    )
 
    # --------------------------------------------------
    # Review preserves established V2 baseline
    # --------------------------------------------------
 
    legacy_review = review_requirements(
        legacy_engineering
    )
 
    legacy_specification = (
        legacy_review
        .engineering_requirements
        .natural_convection
    )
 
    assert legacy_specification is not None
 
    assert (
        legacy_specification.orientation
        == "vertical"
    )
 
    assert (
        legacy_specification.include_radiation
        is False
    )
 
    assert not any(
        question.field_name
        == "surface_emissivity"
        for question
        in legacy_review.clarification_questions
    )
 
    # --------------------------------------------------
    # Explicit horizontal-up + radiation parsing
    # --------------------------------------------------
 
    radiation_input = complete_natural_input()
 
    radiation_input["natural_convection"] = {
        "orientation": "Horizontal fins up",
        "include_radiation": True,
        "surface_emissivity": "0.85",
        "surroundings_temperature": "30",
    }
 
    radiation_engineering = parse_requirements(
        radiation_input
    )
 
    radiation_specification = (
        radiation_engineering
        .natural_convection
    )
 
    assert radiation_specification is not None
 
    assert (
        radiation_specification.orientation
        == "Horizontal fins up"
    )
 
    assert (
        radiation_specification.include_radiation
        is True
    )
 
    assert (
        radiation_specification.surface_emissivity
        == 0.85
    )
 
    assert (
        radiation_specification
        .surroundings_temperature
        == 30.0
    )
 
    radiation_review = review_requirements(
        radiation_engineering
    )
 
    assert (
        radiation_engineering
        .natural_convection
        .orientation
        == "horizontal_fins_up"
    )
 
    assert not radiation_review.validation_errors
 
    # --------------------------------------------------
    # Horizontal-down normalization
    # --------------------------------------------------
 
    downward_input = complete_natural_input()
 
    downward_input["natural_convection"] = {
        "orientation": "fins downward",
        "include_radiation": False,
    }
 
    downward_engineering = parse_requirements(
        downward_input
    )
 
    downward_review = review_requirements(
        downward_engineering
    )
 
    assert not downward_review.validation_errors
 
    assert (
        downward_engineering
        .natural_convection
        .orientation
        == "horizontal_fins_down"
    )
 
    # --------------------------------------------------
    # Missing emissivity requires clarification
    # --------------------------------------------------
 
    missing_emissivity_input = (
        complete_natural_input()
    )
 
    missing_emissivity_input[
        "natural_convection"
    ] = {
        "orientation": "vertical",
        "include_radiation": True,
        "surface_emissivity": None,
        "surroundings_temperature": 30.0,
    }
 
    missing_emissivity_engineering = (
        parse_requirements(
            missing_emissivity_input
        )
    )
 
    missing_emissivity_review = (
        review_requirements(
            missing_emissivity_engineering
        )
    )
 
    assert any(
        question.field_name
        == "surface_emissivity"
        for question
        in (
            missing_emissivity_review
            .clarification_questions
        )
    )
 
    # --------------------------------------------------
    # Missing surroundings temperature defaults ambient
    # --------------------------------------------------
 
    default_surroundings_input = (
        complete_natural_input()
    )
 
    default_surroundings_input[
        "natural_convection"
    ] = {
        "orientation": "vertical",
        "include_radiation": True,
        "surface_emissivity": 0.90,
        "surroundings_temperature": None,
    }
 
    default_surroundings_engineering = (
        parse_requirements(
            default_surroundings_input
        )
    )
 
    default_surroundings_review = (
        review_requirements(
            default_surroundings_engineering
        )
    )
 
    assert not (
        default_surroundings_review
        .validation_errors
    )
 
    assert (
        default_surroundings_engineering
        .natural_convection
        .surroundings_temperature
        == 30.0
    )
 
    # --------------------------------------------------
    # Unsupported orientation is rejected
    # --------------------------------------------------
 
    invalid_orientation_input = (
        complete_natural_input()
    )
 
    invalid_orientation_input[
        "natural_convection"
    ] = {
        "orientation": "sideways diagonal",
        "include_radiation": False,
    }
 
    invalid_orientation_review = (
        review_requirements(
            parse_requirements(
                invalid_orientation_input
            )
        )
    )
 
    assert any(
        "orientation must be one of"
        in error.lower()
        for error
        in invalid_orientation_review.validation_errors
    )
 
    # --------------------------------------------------
    # Invalid emissivity is rejected
    # --------------------------------------------------
 
    invalid_emissivity_input = (
        complete_natural_input()
    )
 
    invalid_emissivity_input[
        "natural_convection"
    ] = {
        "orientation": "vertical",
        "include_radiation": True,
        "surface_emissivity": 1.2,
        "surroundings_temperature": 30.0,
    }
 
    invalid_emissivity_review = (
        review_requirements(
            parse_requirements(
                invalid_emissivity_input
            )
        )
    )
 
    assert any(
        "surface emissivity"
        in error.lower()
        for error
        in invalid_emissivity_review.validation_errors
    )
 
    # --------------------------------------------------
    # Invalid surroundings temperature is rejected
    # --------------------------------------------------
 
    invalid_surroundings_input = (
        complete_natural_input()
    )
 
    invalid_surroundings_input[
        "natural_convection"
    ] = {
        "orientation": "vertical",
        "include_radiation": True,
        "surface_emissivity": 0.85,
        "surroundings_temperature": -300.0,
    }
 
    invalid_surroundings_review = (
        review_requirements(
            parse_requirements(
                invalid_surroundings_input
            )
        )
    )
 
    assert any(
        "surroundings temperature"
        in error.lower()
        for error
        in invalid_surroundings_review.validation_errors
    )

    # --------------------------------------------------
    # Different radiative surroundings are not yet
    # supported by the single-environment thermal model
    # --------------------------------------------------
 
    different_surroundings_input = (
        complete_natural_input()
    )
 
    different_surroundings_input[
        "natural_convection"
    ] = {
        "orientation": "vertical",
        "include_radiation": True,
        "surface_emissivity": 0.85,
        "surroundings_temperature": 20.0,
    }
 
    different_surroundings_review = (
        review_requirements(
            parse_requirements(
                different_surroundings_input
            )
        )
    )
 
    assert any(
        "requires radiative surroundings temperature "
        "to equal ambient air temperature"
        in error
        for error
        in (
            different_surroundings_review
            .validation_errors
        )
    )
 
    print(
        "ALL NATURAL-CONVECTION REQUIREMENT "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()