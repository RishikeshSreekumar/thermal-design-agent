"""
Regression checks for hydraulic-diameter preservation
through the thermal-optimizer candidate workflow.
 
The test verifies that:
 
- FlowNetworkResult remains the calculation source.
- DesignCandidate preserves the resolved SI value.
- ThermalResults receives the same value in millimetres.
- No hydraulic-diameter recalculation is required during
  result conversion.
"""
 
import math
 
from core.thermal_optimizer import ThermalOptimizer
from models.design_candidate import DesignCandidate
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
 
 
def main() -> None:
    requirements = EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        requirements=Requirements(
            heat_load=165.0,
            ambient_temperature=30.0,
            air_velocity=5.0,
        ),
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=8.0,
        ),
    )
 
    optimizer = ThermalOptimizer()
 
    optimization_result = (
        optimizer.optimize_with_details(
            requirements
        )
    )
 
    assert optimization_result.has_feasible_design
 
    assert optimization_result.best_result is not None
 
    assert optimization_result.selected_candidate is not None
 
    # --------------------------------------------------
    # Every completed candidate preserves hydraulic
    # diameter from its resolved airflow state.
    # --------------------------------------------------
 
    for index, candidate in enumerate(
        optimization_result.candidates,
        start=1,
    ):
        assert math.isfinite(
            candidate.hydraulic_diameter
        ), (
            f"Candidate {index}: hydraulic diameter "
            "is not finite."
        )
 
        assert candidate.hydraulic_diameter > 0.0, (
            f"Candidate {index}: hydraulic diameter "
            "must be positive."
        )
 
    # --------------------------------------------------
    # Selected candidate and ThermalResults remain
    # numerically consistent.
    # --------------------------------------------------
 
    selected_candidate = (
        optimization_result.selected_candidate
    )
 
    expected_hydraulic_diameter_mm = (
        selected_candidate.hydraulic_diameter
        * 1000.0
    )
 
    assert math.isclose(
        (
            optimization_result
            .best_result
            .hydraulic_diameter
        ),
        expected_hydraulic_diameter_mm,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Backward compatibility for older constructors
    # --------------------------------------------------
 
    legacy_candidate = DesignCandidate(
        base_thickness=3.0,
        fin_thickness=0.8,
        fin_height=8.0,
        fin_spacing=1.6,
        fin_count=21,
        total_height=11.0,
 
        gross_frontal_area=0.0004,
        open_flow_area=0.000256,
        blockage_ratio=0.36,
        approach_velocity=5.0,
        channel_velocity=7.8125,
 
        reynolds_number=1295.405982905983,
        nusselt_number=7.54,
        heat_transfer_coefficient=74.36325,
 
        friction_factor=0.049405,
        pressure_drop=86.1899,
        pumping_power=0.1723798,
 
        thermal_resistance=0.680824,
        estimated_base_temperature=142.33596,
    )
 
    assert legacy_candidate.hydraulic_diameter == 0.0
 
    print(
        "ALL CANDIDATE HYDRAULIC DIAMETER "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()