"""
Integration checks for orientation-aware plate-fin
natural-convection solving.
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
 
        hydraulic_diameter=0.0,
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
    specification=None,
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
 
        natural_convection=specification,
    )
 
 
def main() -> None:
 
    candidate = build_candidate()
 
    # --------------------------------------------------
    # Legacy vertical path
    # --------------------------------------------------
 
    legacy_result = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(),
            material_conductivity=201.0,
        )
    )
 
    # --------------------------------------------------
    # Explicit vertical path
    # --------------------------------------------------
 
    explicit_vertical_result = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(
                NaturalConvectionSpecification(
                    orientation="vertical",
                    include_radiation=False,
                )
            ),
            material_conductivity=201.0,
        )
    )
 
    assert math.isclose(
        legacy_result.nusselt_number,
        explicit_vertical_result.nusselt_number,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        legacy_result.heat_transfer_coefficient,
        explicit_vertical_result
        .heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        legacy_result.thermal_resistance,
        explicit_vertical_result
        .thermal_resistance,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        legacy_result.estimated_base_temperature,
        explicit_vertical_result
        .estimated_base_temperature,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # Established V2 reference for this exact
    # optimizer-selected geometry remains protected.
    assert math.isclose(
        legacy_result.thermal_resistance,
        3.6002936376607786,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
 
    # --------------------------------------------------
    # Horizontal — fins upward
    # --------------------------------------------------
 
    upward_result = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(
                NaturalConvectionSpecification(
                    orientation=(
                        "horizontal_fins_up"
                    ),
                    include_radiation=False,
                )
            ),
            material_conductivity=201.0,
        )
    )
 
    assert upward_result.nusselt_number > 0.0
 
    assert (
        upward_result.heat_transfer_coefficient
        > 0.0
    )
 
    assert upward_result.thermal_resistance > 0.0
 
    assert (
        upward_result.estimated_base_temperature
        > 30.0
    )
 
    # --------------------------------------------------
    # Horizontal — fins downward
    # --------------------------------------------------
 
    downward_result = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=build_requirements(
                NaturalConvectionSpecification(
                    orientation=(
                        "horizontal_fins_down"
                    ),
                    include_radiation=False,
                )
            ),
            material_conductivity=201.0,
        )
    )
 
    assert downward_result.nusselt_number > 0.0
 
    assert (
        downward_result.heat_transfer_coefficient
        > 0.0
    )
 
    assert downward_result.thermal_resistance > 0.0
 
    assert (
        downward_result.estimated_base_temperature
        > 30.0
    )
 
    # --------------------------------------------------
    # Orientation must affect the physics
    # --------------------------------------------------
 
    assert not math.isclose(
        upward_result.heat_transfer_coefficient,
        downward_result.heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
 
    assert not math.isclose(
        explicit_vertical_result
        .heat_transfer_coefficient,
        upward_result.heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
 
    print()
    print(
        "Vertical h:",
        explicit_vertical_result
        .heat_transfer_coefficient,
    )
 
    print(
        "Horizontal fins-up h:",
        upward_result.heat_transfer_coefficient,
    )
 
    print(
        "Horizontal fins-down h:",
        downward_result.heat_transfer_coefficient,
    )
 
    print(
        "Vertical Rth:",
        explicit_vertical_result
        .thermal_resistance,
    )
 
    print(
        "Horizontal fins-up Rth:",
        upward_result.thermal_resistance,
    )
 
    print(
        "Horizontal fins-down Rth:",
        downward_result.thermal_resistance,
    )
 
    print(
        "ALL NATURAL-CONVECTION ORIENTATION "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()