"""
Regression checks for optimizer-side material-cost
budget enforcement.
 
The regression verifies that:
 
- no budget preserves normal optimizer behaviour;
- a generous INR budget preserves every candidate;
- an intermediate INR budget filters candidates;
- an impossible INR budget rejects every candidate.
"""
 
import math
 
from core.thermal_optimizer import (
    ThermalOptimizer,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    MaterialCostBudget,
    Requirements,
)
 
 
def create_requirements(
    material_cost_budget: (
        MaterialCostBudget | None
    ),
) -> EngineeringRequirements:
    """
    Create one deterministic optimizer input.
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
            material_cost_budget=(
                material_cost_budget
            ),
        ),
    )
 
 
def main() -> None:
    optimizer = ThermalOptimizer()
 
    # --------------------------------------------------
    # No budget
    # --------------------------------------------------
 
    unrestricted_result = (
        optimizer.optimize_with_details(
            create_requirements(
                material_cost_budget=None
            )
        )
    )
 
    assert unrestricted_result.has_feasible_design
    assert unrestricted_result.candidates
 
    unrestricted_count = len(
        unrestricted_result.candidates
    )
 
    candidate_costs = [
        candidate.material_cost
        for candidate in unrestricted_result.candidates
        if candidate.material_cost is not None
    ]
 
    assert len(candidate_costs) == unrestricted_count
 
    lowest_candidate_cost = min(
        candidate_costs
    )
 
    highest_candidate_cost = max(
        candidate_costs
    )
 
    assert math.isfinite(
        lowest_candidate_cost
    )
 
    assert math.isfinite(
        highest_candidate_cost
    )
 
    assert lowest_candidate_cost > 0.0
 
    for candidate in unrestricted_result.candidates:
        assert (
            candidate.material_cost_currency
            == "INR"
        )
 
    # --------------------------------------------------
    # Generous INR budget
    # --------------------------------------------------
 
    generous_budget_amount = (
        highest_candidate_cost + 1.0
    )
 
    generous_result = (
        optimizer.optimize_with_details(
            create_requirements(
                material_cost_budget=(
                    MaterialCostBudget(
                        maximum_amount=(
                            generous_budget_amount
                        ),
                        currency_code="INR",
                    )
                )
            )
        )
    )
 
    assert generous_result.has_feasible_design
 
    assert (
        len(generous_result.candidates)
        == unrestricted_count
    )
 
    for candidate in generous_result.candidates:
        assert candidate.material_cost is not None
 
        assert (
            candidate.material_cost
            <= generous_budget_amount
        )
 
        assert (
            candidate.material_cost_currency
            == "INR"
        )
 
    # --------------------------------------------------
    # Intermediate INR budget
    # --------------------------------------------------
 
    intermediate_budget_amount = (
        lowest_candidate_cost
        + (
            highest_candidate_cost
            - lowest_candidate_cost
        )
        * 0.5
    )
 
    limited_result = (
        optimizer.optimize_with_details(
            create_requirements(
                material_cost_budget=(
                    MaterialCostBudget(
                        maximum_amount=(
                            intermediate_budget_amount
                        ),
                        currency_code="INR",
                    )
                )
            )
        )
    )
 
    assert limited_result.has_feasible_design
 
    assert (
        len(limited_result.candidates)
        < unrestricted_count
    )
 
    for candidate in limited_result.candidates:
        assert candidate.material_cost is not None
 
        assert (
            candidate.material_cost
            <= intermediate_budget_amount
        )
 
        assert (
            candidate.material_cost_currency
            == "INR"
        )
 
    # --------------------------------------------------
    # Impossible INR budget
    # --------------------------------------------------
 
    impossible_budget_amount = (
        lowest_candidate_cost * 0.5
    )
 
    impossible_result = (
        optimizer.optimize_with_details(
            create_requirements(
                material_cost_budget=(
                    MaterialCostBudget(
                        maximum_amount=(
                            impossible_budget_amount
                        ),
                        currency_code="INR",
                    )
                )
            )
        )
    )
 
    assert not impossible_result.has_feasible_design
    assert not impossible_result.candidates

    # --------------------------------------------------
    # Currency mismatch
    # --------------------------------------------------
 
    try:
        optimizer.optimize_with_details(
            create_requirements(
                material_cost_budget=MaterialCostBudget(
                    maximum_amount=1000.0,
                    currency_code="USD",
                )
            )
        )
    except ValueError as exc:
        assert "currency" in str(exc).lower()
    else:
        raise AssertionError(
            "Currency mismatch should raise ValueError."
        )
 
    print(
        "ALL OPTIMIZER MATERIAL COST BUDGET "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()
 