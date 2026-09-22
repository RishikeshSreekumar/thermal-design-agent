"""
Optimizer integration regression for natural-convection
orientation and thermal radiation.
"""
 
import math
 
from core.candidate_state_validator import (
    validate_completed_candidate,
)
from core.thermal_optimizer import (
    ThermalOptimizer,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    NaturalConvectionSpecification,
    Requirements,
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
 
    optimizer = ThermalOptimizer()
 
    # --------------------------------------------------
    # Established vertical / convection-only baseline
    # --------------------------------------------------
 
    baseline = optimizer.optimize_with_details(
        build_requirements()
    )
 
    assert baseline.has_feasible_design
 
    baseline_selected = (
        baseline.selected_candidate
    )
 
    assert baseline_selected is not None
 
    assert math.isclose(
        baseline_selected
        .radiative_heat_transfer_coefficient,
        0.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        baseline_selected.thermal_resistance,
        3.6002936376607786,
        rel_tol=0.0,
        abs_tol=1e-9,
    )
 
    # --------------------------------------------------
    # Vertical + radiation
    # --------------------------------------------------
 
    radiation = optimizer.optimize_with_details(
        build_requirements(
            include_radiation=True,
            emissivity=0.85,
        )
    )
 
    assert radiation.has_feasible_design
 
    radiation_selected = (
        radiation.selected_candidate
    )
 
    assert radiation_selected is not None
 
    assert (
        radiation_selected
        .radiative_heat_transfer_coefficient
        > 0.0
    )
 
    assert (
        radiation_selected
        .effective_heat_transfer_coefficient
        > radiation_selected
        .convective_heat_transfer_coefficient
    )
 
    assert math.isclose(
        radiation_selected
        .effective_heat_transfer_coefficient,
        (
            radiation_selected
            .convective_heat_transfer_coefficient
            + radiation_selected
            .radiative_heat_transfer_coefficient
        ),
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert (
        radiation_selected.thermal_resistance
        < baseline_selected.thermal_resistance
    )
 
    validate_completed_candidate(
        radiation_selected
    )
 
    # --------------------------------------------------
    # ThermalResults preserves radiation state
    # --------------------------------------------------
 
    assert radiation.best_result is not None
 
    assert math.isclose(
        radiation.best_result
        .radiative_heat_transfer_coefficient,
        radiation_selected
        .radiative_heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        radiation.best_result
        .convective_heat_transfer_coefficient,
        radiation_selected
        .convective_heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Horizontal-up path reaches optimizer
    # --------------------------------------------------
 
    horizontal_up = (
        optimizer.optimize_with_details(
            build_requirements(
                orientation=(
                    "horizontal_fins_up"
                ),
            )
        )
    )
 
    assert horizontal_up.has_feasible_design
    assert horizontal_up.selected_candidate is not None
 
    assert (
        horizontal_up
        .selected_candidate
        .radiative_heat_transfer_coefficient
        == 0.0
    )
 
    validate_completed_candidate(
        horizontal_up.selected_candidate
    )
 
    print()
 
    print(
        "Vertical convection-only selected Rth:",
        baseline_selected.thermal_resistance,
    )
 
    print(
        "Vertical radiation selected h_conv:",
        radiation_selected
        .convective_heat_transfer_coefficient,
    )
 
    print(
        "Vertical radiation selected h_rad:",
        radiation_selected
        .radiative_heat_transfer_coefficient,
    )
 
    print(
        "Vertical radiation selected h_effective:",
        radiation_selected
        .effective_heat_transfer_coefficient,
    )
 
    print(
        "Vertical radiation selected Rth:",
        radiation_selected.thermal_resistance,
    )
 
    print(
        "Horizontal-up selected geometry:",
        (
            horizontal_up
            .selected_candidate
            .base_thickness,
            horizontal_up
            .selected_candidate
            .fin_height,
            horizontal_up
            .selected_candidate
            .fin_thickness,
            horizontal_up
            .selected_candidate
            .fin_spacing,
            horizontal_up
            .selected_candidate
            .fin_count,
        ),
    )
 
    print(
        "Horizontal-up selected Rth:",
        horizontal_up
        .selected_candidate
        .thermal_resistance,
    )
 
    print()
 
    print(
        "ALL NATURAL-CONVECTION RADIATION "
        "OPTIMIZER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()