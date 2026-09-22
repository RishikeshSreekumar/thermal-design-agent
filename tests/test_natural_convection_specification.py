"""
Regression checks for the natural-convection
configuration requirement model.
"""
 
from models.requirements import (
    EngineeringRequirements,
    NATURAL_CONVECTION_ORIENTATIONS,
    NaturalConvectionSpecification,
)
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Legacy compatibility
    # --------------------------------------------------
 
    legacy_requirements = EngineeringRequirements()
 
    assert (
        legacy_requirements.natural_convection
        is None
    )
 
    # --------------------------------------------------
    # Supported orientations
    # --------------------------------------------------
 
    assert NATURAL_CONVECTION_ORIENTATIONS == (
        "vertical",
        "horizontal_fins_up",
        "horizontal_fins_down",
    )
 
    vertical = NaturalConvectionSpecification(
        orientation="vertical",
    )
 
    upward_horizontal = (
        NaturalConvectionSpecification(
            orientation="horizontal_fins_up",
        )
    )
 
    downward_horizontal = (
        NaturalConvectionSpecification(
            orientation="horizontal_fins_down",
        )
    )
 
    assert vertical.orientation == "vertical"
 
    assert (
        upward_horizontal.orientation
        == "horizontal_fins_up"
    )
 
    assert (
        downward_horizontal.orientation
        == "horizontal_fins_down"
    )
 
    # --------------------------------------------------
    # Radiation disabled by default
    # --------------------------------------------------
 
    assert vertical.include_radiation is False
    assert vertical.surface_emissivity is None
 
    assert (
        vertical.surroundings_temperature
        is None
    )
 
    # --------------------------------------------------
    # Explicit radiation configuration
    # --------------------------------------------------
 
    radiation_configuration = (
        NaturalConvectionSpecification(
            orientation="horizontal_fins_up",
            include_radiation=True,
            surface_emissivity=0.85,
            surroundings_temperature=30.0,
        )
    )
 
    assert (
        radiation_configuration.include_radiation
        is True
    )
 
    assert (
        radiation_configuration.surface_emissivity
        == 0.85
    )
 
    assert (
        radiation_configuration
        .surroundings_temperature
        == 30.0
    )
 
    # --------------------------------------------------
    # EngineeringRequirements preservation
    # --------------------------------------------------
 
    engineering = EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="natural",
        natural_convection=(
            radiation_configuration
        ),
    )
 
    assert (
        engineering.natural_convection
        is radiation_configuration
    )
 
    print(
        "ALL NATURAL-CONVECTION "
        "SPECIFICATION CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()