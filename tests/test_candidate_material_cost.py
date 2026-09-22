"""
Regression checks for material-cost preservation in
DesignCandidate and ThermalOptimizer.
 
The regression verifies that:
 
- An unevaluated candidate may have no material cost.
- Candidate convenience properties expose cost safely.
- ThermalOptimizer attaches a complete cost result to every
  feasible evaluated candidate.
- Candidate cost equals candidate mass multiplied by the
  resolved material cost per kilogram.
- Currency and pricing metadata are preserved.
- The selected candidate retains the same evaluated cost.
"""
 
import math
 
from core.thermal_optimizer import (
    ThermalOptimizer,
)
from materials.material_cost_database import (
    get_material_cost_profile_for_material,
)
from manufacturing.extrusion_capability import (
    AL6063_EXTRUSION,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.material_cost_result import (
    MaterialCostResult,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
 
 
def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-12,
) -> None:
    """
    Assert deterministic floating-point equality.
    """
 
    assert math.isclose(
        actual,
        expected,
        rel_tol=0.0,
        abs_tol=tolerance,
    ), (
        f"Expected {expected}, received {actual}."
    )
 
 
def create_manual_candidate(
) -> DesignCandidate:
    """
    Create a candidate without commercial evaluation.
    """
 
    return DesignCandidate(
        base_thickness=3.0,
        fin_thickness=1.0,
        fin_height=8.0,
        fin_spacing=2.0,
        fin_count=10,
        total_height=11.0,
 
        gross_frontal_area=0.001,
        open_flow_area=0.0007,
        blockage_ratio=0.3,
        approach_velocity=5.0,
        channel_velocity=7.0,
 
        reynolds_number=3000.0,
        nusselt_number=15.0,
        heat_transfer_coefficient=75.0,
 
        friction_factor=0.04,
        pressure_drop=20.0,
        pumping_power=0.2,
 
        thermal_resistance=1.2,
        estimated_base_temperature=228.0,
 
        solid_volume=1.0e-5,
        mass=0.027,
    )
 
 
def create_requirements(
) -> EngineeringRequirements:
    """
    Create a compact feasible optimization envelope.
    """
 
    return EngineeringRequirements(
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
            max_height=12.0,
        ),
    )
 
 
def main() -> None:
    # --------------------------------------------------
    # Optional state for manually created or unevaluated
    # candidates
    # --------------------------------------------------
 
    manual_candidate = (
        create_manual_candidate()
    )
 
    assert (
        manual_candidate.material_cost_result
        is None
    )
 
    assert manual_candidate.material_cost is None
 
    assert (
        manual_candidate.material_cost_currency
        is None
    )
 
    assert not manual_candidate.has_material_cost
 
    # --------------------------------------------------
    # End-to-end optimizer evaluation
    # --------------------------------------------------
 
    optimizer = ThermalOptimizer()
 
    result = optimizer.optimize_with_details(
        create_requirements()
    )
 
    assert result.has_feasible_design
 
    assert result.candidates
 
    cost_profile = (
        get_material_cost_profile_for_material(
            AL6063_EXTRUSION.material
        )
    )
 
    for index, candidate in enumerate(
        result.candidates,
        start=1,
    ):
        assert candidate.mass > 0.0
 
        assert math.isfinite(
            candidate.mass
        )
 
        assert candidate.has_material_cost
 
        assert isinstance(
            candidate.material_cost_result,
            MaterialCostResult,
        )
 
        assert (
            candidate.material_cost
            is not None
        )
 
        assert (
            candidate.material_cost_currency
            == cost_profile.currency_code
        )

        assert cost_profile.currency_code == "INR"
 
        expected_cost = (
            candidate.mass
            * cost_profile.cost_per_kg
        )
 
        assert_close(
            candidate.material_cost,
            expected_cost,
        )
 
        assert_close(
            (
                candidate
                .material_cost_result
                .mass_kg
            ),
            candidate.mass,
        )
 
        assert_close(
            (
                candidate
                .material_cost_result
                .cost_per_kg
            ),
            cost_profile.cost_per_kg,
        )
 
        assert (
            candidate
            .material_cost_result
            .material_key
            == cost_profile.material_key
        )
 
        assert (
            candidate
            .material_cost_result
            .currency_code
            == cost_profile.currency_code
        )
 
        assert (
            candidate
            .material_cost_result
            .pricing_basis
            == cost_profile.pricing_basis
        )
 
        assert (
            candidate
            .material_cost_result
            .effective_date
            == cost_profile.effective_date
        )
 
    # --------------------------------------------------
    # Selected candidate preserves its completed cost
    # --------------------------------------------------
 
    selected_candidate = (
        result.selected_candidate
    )
 
    assert selected_candidate is not None
 
    assert selected_candidate in result.candidates
 
    assert selected_candidate.has_material_cost
 
    assert selected_candidate.material_cost is not None
 
    expected_selected_cost = (
        selected_candidate.mass
        * cost_profile.cost_per_kg
    )
 
    assert_close(
        selected_candidate.material_cost,
        expected_selected_cost,
    )
 
    print(
        "ALL CANDIDATE MATERIAL COST CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()