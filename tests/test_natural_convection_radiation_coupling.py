"""
Integration regression for radiation coupled with
orientation-aware plate-fin natural convection.
"""
 
import math
 
from core.plate_fin_natural_convection_solver import (
    PlateFinNaturalConvectionSolver,
)
from models.design_candidate import DesignCandidate
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    NaturalConvectionSpecification,
    Requirements,
)
 
 
def build_candidate() -> DesignCandidate:
    return DesignCandidate(
        base_thickness=3.0,
        fin_thickness=0.8,
        fin_height=8.0,
        fin_spacing=1.6,
        fin_count=21,
        total_height=11.0,
 
        gross_frontal_area=0.0,
        open_flow_area=0.0,
        blockage_ratio=0.0,
        approach_velocity=0.0,
        channel_velocity=0.0,
 
        reynolds_number=0.0,
        nusselt_number=1.0,
        heat_transfer_coefficient=1.0,
 
        friction_factor=0.0,
        pressure_drop=0.0,
        pumping_power=0.0,
 
        thermal_resistance=1.0,
        estimated_base_temperature=1.0,
    )
 
 
def build_requirements(
    *,
    orientation: str = "vertical",
    include_radiation: bool = False,
    emissivity: float | None = None,
) -> EngineeringRequirements:
 
    return EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="natural",
 
        requirements=Requirements(
            heat_load=20.0,
            ambient_temperature=30.0,
            air_velocity=None,
        ),
 
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=30.0,
        ),
 
        natural_convection=(
            NaturalConvectionSpecification(
                orientation=orientation,
                include_radiation=(
                    include_radiation
                ),
                surface_emissivity=emissivity,
                surroundings_temperature=30.0,
            )
        ),
    )
 
 
def main() -> None:
 
    candidate = build_candidate()
 
    # --------------------------------------------------
    # Vertical / radiation disabled
    # --------------------------------------------------
 
    convection_only = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(),
            material_conductivity=201.0,
        )
    )
 
    assert math.isclose(
        convection_only
        .radiative_heat_transfer_coefficient,
        0.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        convection_only
        .heat_transfer_coefficient,
        convection_only
        .convective_heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        convection_only
        .effective_heat_transfer_coefficient,
        convection_only
        .heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # Existing vertical reference remains protected.
    assert math.isclose(
        convection_only.thermal_resistance,
        3.6002936376607786,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
 
    # --------------------------------------------------
    # Vertical / radiation enabled
    # --------------------------------------------------
 
    with_radiation = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(
                include_radiation=True,
                emissivity=0.85,
            ),
            material_conductivity=201.0,
        )
    )
 
    assert (
        with_radiation
        .radiative_heat_transfer_coefficient
        > 0.0
    )
 
    assert (
        with_radiation
        .effective_heat_transfer_coefficient
        > with_radiation
        .convective_heat_transfer_coefficient
    )
 
    assert math.isclose(
        with_radiation
        .effective_heat_transfer_coefficient,
        (
            with_radiation
            .convective_heat_transfer_coefficient
            + with_radiation
            .radiative_heat_transfer_coefficient
        ),
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert (
        with_radiation.thermal_resistance
        < convection_only.thermal_resistance
    )
 
    assert (
        with_radiation
        .estimated_base_temperature
        < convection_only
        .estimated_base_temperature
    )
 
    # --------------------------------------------------
    # Zero emissivity must collapse exactly to
    # convection-only behaviour
    # --------------------------------------------------
 
    zero_emissivity = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(
                include_radiation=True,
                emissivity=0.0,
            ),
            material_conductivity=201.0,
        )
    )
 
    assert math.isclose(
        zero_emissivity.thermal_resistance,
        convection_only.thermal_resistance,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        zero_emissivity
        .estimated_base_temperature,
        convection_only
        .estimated_base_temperature,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Horizontal-up radiation coupling
    # --------------------------------------------------
 
    horizontal_up_no_radiation = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(
                orientation="horizontal_fins_up",
            ),
            material_conductivity=201.0,
        )
    )
 
    horizontal_up_with_radiation = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(
                orientation="horizontal_fins_up",
                include_radiation=True,
                emissivity=0.85,
            ),
            material_conductivity=201.0,
        )
    )
 
    assert (
        horizontal_up_with_radiation
        .thermal_resistance
        < horizontal_up_no_radiation
        .thermal_resistance
    )
 
    assert (
        horizontal_up_with_radiation
        .estimated_base_temperature
        < horizontal_up_no_radiation
        .estimated_base_temperature
    )
 
    # --------------------------------------------------
    # Output
    # --------------------------------------------------
 
    print()
 
    print(
        "Vertical convection-only h_conv:",
        convection_only
        .convective_heat_transfer_coefficient,
    )
 
    print(
        "Vertical radiation h_conv:",
        with_radiation
        .convective_heat_transfer_coefficient,
    )
 
    print(
        "Vertical radiation h_rad:",
        with_radiation
        .radiative_heat_transfer_coefficient,
    )
 
    print(
        "Vertical radiation h_effective:",
        with_radiation
        .effective_heat_transfer_coefficient,
    )
 
    print(
        "Vertical convection-only Rth:",
        convection_only.thermal_resistance,
    )
 
    print(
        "Vertical radiation Rth:",
        with_radiation.thermal_resistance,
    )
 
    print(
        "Vertical convection-only base temperature:",
        convection_only
        .estimated_base_temperature,
    )
 
    print(
        "Vertical radiation base temperature:",
        with_radiation
        .estimated_base_temperature,
    )
 
    print(
        "Horizontal-up convection-only Rth:",
        horizontal_up_no_radiation
        .thermal_resistance,
    )
 
    print(
        "Horizontal-up radiation Rth:",
        horizontal_up_with_radiation
        .thermal_resistance,
    )
 
    print()
 
    print(
        "ALL NATURAL-CONVECTION RADIATION "
        "COUPLING CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()