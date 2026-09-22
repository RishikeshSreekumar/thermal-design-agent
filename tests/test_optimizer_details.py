"""
test_optimizer_details.py
 
Validates the detailed output of the ThermalOptimizer.
 
Checks:
- A feasible design is found
- Candidate counts are internally consistent
- Every stored candidate satisfies the total-height constraint
- The best result matches the lowest-resistance stored candidate
- Candidate geometry values are physically valid
"""
 
import logging
import math
 
from core.thermal_optimizer import ThermalOptimizer
 
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
 
 
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
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
            max_height=30.0,
        ),
    )
 
    optimizer = ThermalOptimizer()
 
    result = optimizer.optimize_with_details(
        requirements
    )
 
    print()
    print("=" * 70)
    print("DETAILED OPTIMIZATION RESULT")
    print("=" * 70)
 
    print(
        "Feasible candidates:",
        result.feasible_candidate_count,
    )
 
    print(
        "Rejected candidates:",
        result.rejected_candidate_count,
    )
 
    total_candidates = (
        result.feasible_candidate_count
        + result.rejected_candidate_count
    )
 
    print(
        "Total candidates:",
        total_candidates,
    )
 
    print(
        "Has feasible design:",
        result.has_feasible_design,
    )
 
    print()
    print("Best result:")
    print(result.best_result)
 
    # --------------------------------------------------
    # Basic Result Checks
    # --------------------------------------------------
 
    assert result.has_feasible_design, (
        "Optimizer did not find a feasible design."
    )
 
    assert result.best_result is not None, (
        "Best result is missing."
    )
 
    assert result.feasible_candidate_count > 0, (
        "Feasible candidate count must be greater than zero."
    )
 
    assert (
        result.feasible_candidate_count
        == len(result.candidates)
    ), (
        "Stored candidate count does not match "
        "feasible_candidate_count."
    )
 
    assert result.rejected_candidate_count >= 0, (
        "Rejected candidate count cannot be negative."
    )
 
    # --------------------------------------------------
    # Candidate Integrity Checks
    # --------------------------------------------------
 
    maximum_total_height = (
        requirements.constraints.max_height
    )
 
    for index, candidate in enumerate(
        result.candidates,
        start=1,
    ):
        calculated_total_height = (
            candidate.base_thickness
            + candidate.fin_height
        )
 
        assert math.isclose(
            candidate.total_height,
            calculated_total_height,
            rel_tol=0.0,
            abs_tol=1e-9,
        ), (
            f"Candidate {index}: stored total height "
            "does not equal base thickness plus fin height."
        )
 
        assert (
            candidate.total_height
            <= maximum_total_height
        ), (
            f"Candidate {index}: total-height constraint "
            "was violated."
        )
 
        assert candidate.base_thickness > 0, (
            f"Candidate {index}: invalid base thickness."
        )
 
        assert candidate.fin_height > 0, (
            f"Candidate {index}: invalid fin height."
        )
 
        assert candidate.fin_thickness > 0, (
            f"Candidate {index}: invalid fin thickness."
        )
 
        assert candidate.fin_spacing > 0, (
            f"Candidate {index}: invalid fin spacing."
        )
 
        assert candidate.fin_count >= 2, (
            f"Candidate {index}: fewer than two fins."
        )
 
        assert math.isfinite(
            candidate.thermal_resistance
        ), (
            f"Candidate {index}: non-finite thermal resistance."
        )
 
        assert candidate.thermal_resistance > 0, (
            f"Candidate {index}: thermal resistance "
            "must be positive."
        )
 
    # --------------------------------------------------
    # Best-Candidate Consistency Check
    # --------------------------------------------------
 
    lowest_resistance_candidate = min(
        result.candidates,
        key=lambda candidate: (
            candidate.thermal_resistance
        ),
    )
 
    assert math.isclose(
        result.best_result.thermal_resistance,
        lowest_resistance_candidate.thermal_resistance,
        rel_tol=0.0,
        abs_tol=1e-12,
    ), (
        "Best result does not match the candidate with "
        "the lowest thermal resistance."
    )
 
    assert math.isclose(
        result.best_result.base_thickness,
        lowest_resistance_candidate.base_thickness,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        result.best_result.fin_height,
        lowest_resistance_candidate.fin_height,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        result.best_result.fin_thickness,
        lowest_resistance_candidate.fin_thickness,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        result.best_result.fin_spacing,
        lowest_resistance_candidate.fin_spacing,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert (
        result.best_result.fin_count
        == lowest_resistance_candidate.fin_count
    )
 
    print()
    print("=" * 70)
    print("ALL DETAILED OPTIMIZER CHECKS PASSED")
    print("=" * 70)
 
    print()
    print("Lowest-resistance candidate:")
    print(lowest_resistance_candidate)
 
 
if __name__ == "__main__":
    main()