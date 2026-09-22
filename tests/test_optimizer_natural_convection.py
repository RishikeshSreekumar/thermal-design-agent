"""
End-to-end natural-convection optimizer regression.
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
    Requirements,
)
 
 
def main() -> None:
 
    requirements = EngineeringRequirements(
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
    )
 
    optimizer = ThermalOptimizer()
 
    result = optimizer.optimize_with_details(
        requirements
    )
 
    assert result.has_feasible_design
 
    assert result.candidates
 
    assert result.selected_candidate is not None
 
    for candidate in result.candidates:
 
        assert (
            candidate.convection_mode
            == "natural"
        )
 
        assert candidate.approach_velocity == 0.0
        assert candidate.channel_velocity == 0.0
 
        assert candidate.reynolds_number == 0.0
        assert candidate.hydraulic_diameter == 0.0
 
        assert candidate.friction_factor == 0.0
        assert candidate.pressure_drop == 0.0
        assert candidate.pumping_power == 0.0
 
        assert candidate.nusselt_number > 0.0
 
        assert (
            candidate
            .heat_transfer_coefficient
            > 0.0
        )
 
        assert candidate.thermal_resistance > 0.0
 
        assert (
            candidate.estimated_base_temperature
            > 30.0
        )
 
        assert candidate.mass > 0.0
 
        assert candidate.has_material_cost
 
        validate_completed_candidate(
            candidate
        )
 
    selected = result.selected_candidate
 
    expected = min(
        result.candidates,
        key=lambda candidate: (
            candidate.thermal_resistance
        ),
    )
 
    assert selected is expected
 
    assert math.isclose(
        result.best_result.thermal_resistance,
        selected.thermal_resistance,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    print()
    print(
        "Natural-convection candidates:",
        result.feasible_candidate_count,
    )
 
    print(
        "Selected geometry:",
        (
            selected.base_thickness,
            selected.fin_height,
            selected.fin_thickness,
            selected.fin_spacing,
            selected.fin_count,
        ),
    )
 
    print(
        "Selected h:",
        selected.heat_transfer_coefficient,
    )
 
    print(
        "Selected Rth:",
        selected.thermal_resistance,
    )
 
    print(
        "Selected base temperature:",
        selected.estimated_base_temperature,
    )
 
    print(
        "ALL NATURAL CONVECTION OPTIMIZER "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()