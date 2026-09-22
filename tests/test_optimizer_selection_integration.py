"""
Regression checks for optimization-selection integration
with ThermalOptimizer.
"""
 
import math
 
from core.candidate_selector import (
    select_candidates,
)
from core.thermal_optimizer import ThermalOptimizer
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
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
 
    # --------------------------------------------------
    # Existing default behavior
    # --------------------------------------------------
 
    result = optimizer.optimize_with_details(
        requirements
    )
 
    assert result.has_feasible_design
 
    assert result.has_single_selected_design
 
    assert result.best_result is not None
 
    assert result.selection_result is not None
 
    assert (
        result.selection_result.mode
        == OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    )
 
    assert (
        result.selection_result
        .uses_legacy_selection
    )
 
    assert result.selected_candidate is not None
 
    expected_candidate = min(
        result.candidates,
        key=lambda candidate: (
            candidate.thermal_resistance
        ),
    )
 
    assert (
        result.selected_candidate
        is expected_candidate
    )
 
    assert result.selected_candidates == (
        expected_candidate,
    )
 
    assert math.isclose(
        result.best_result.thermal_resistance,
        expected_candidate.thermal_resistance,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    direct_result = optimizer.optimize(
        requirements
    )
 
    assert math.isclose(
        direct_result.thermal_resistance,
        result.best_result.thermal_resistance,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Pareto selection contract using the same evaluated
    # candidates
    # --------------------------------------------------
 
    pareto_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .PARETO_FRONT
            )
        )
    )
 
    pareto_selection = select_candidates(
        tuple(result.candidates),
        pareto_configuration,
    )
 
    assert pareto_selection.uses_pareto_selection
 
    assert (
        pareto_selection
        .selected_candidate_count
        >= 1
    )
 
    assert pareto_selection.pareto_result is not None
 
    assert pareto_selection.weighted_result is None
 
    # --------------------------------------------------
    # OptimizationResult properties remain coherent
    # --------------------------------------------------
 
    assert (
        result.feasible_candidate_count
        == len(result.candidates)
    )
 
    assert (
        result.total_candidate_count
        == (
            result.feasible_candidate_count
            + result.rejected_candidate_count
        )
    )
 
    print(
        "ALL OPTIMIZER SELECTION INTEGRATION "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()