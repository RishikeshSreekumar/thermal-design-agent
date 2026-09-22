"""
End-to-end regression checks for completed candidate-state
integrity through ThermalOptimizer.
 
The regression verifies that:
 
- Fixed-velocity optimization produces only complete,
  physically valid evaluated candidates.
- Fan-coupled optimization produces only complete,
  physically valid evaluated candidates.
- Every optimizer-produced candidate can pass through
  the unified candidate-selection boundary.
- Hydraulic diameter remains preserved from airflow
  evaluation through DesignCandidate.
- Legacy, weighted, and Pareto selection remain available
  for optimizer-produced candidates.
"""
 
import math
 
from core.candidate_selector import (
    select_candidates,
)
from core.candidate_state_validator import (
    validate_completed_candidate,
    validate_completed_candidates,
)
from core.thermal_optimizer import ThermalOptimizer
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    FanSpecification,
    Requirements,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def create_fixed_velocity_requirements(
) -> EngineeringRequirements:
    """
    Create a small fixed-velocity optimizer design space.
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
            max_height=8.0,
        ),
    )
 
 
def create_fan_coupled_requirements(
) -> EngineeringRequirements:
    """
    Create a small fan-coupled optimizer design space.
    """
 
    return EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        requirements=Requirements(
            heat_load=165.0,
            ambient_temperature=30.0,
            air_velocity=None,
        ),
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=8.0,
        ),
        fan=FanSpecification(
            fan_name="demo_120mm",
        ),
    )
 
 
def create_weighted_configuration(
) -> OptimizationSelectionConfiguration:
    """
    Create a valid multi-objective weighted selection
    configuration.
    """
 
    return OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .WEIGHTED_SCORE
        ),
        scoring_configuration=(
            ScoringConfiguration(
                objective_weights=(
                    ObjectiveWeight(
                        objective_key=(
                            "thermal_resistance"
                        ),
                        weight=0.6,
                    ),
                    ObjectiveWeight(
                        objective_key=(
                            "pressure_drop"
                        ),
                        weight=0.3,
                    ),
                    ObjectiveWeight(
                        objective_key=(
                            "pumping_power"
                        ),
                        weight=0.1,
                    ),
                )
            )
        ),
    )
 
 
def verify_candidate_state(
    candidate,
    candidate_index: int,
    airflow_mode: str,
) -> None:
    """
    Verify state completeness beyond the central validator's
    public contract.
    """
 
    validate_completed_candidate(
        candidate
    )
 
    assert math.isfinite(
        candidate.hydraulic_diameter
    ), (
        f"{airflow_mode} candidate {candidate_index}: "
        "hydraulic diameter is not finite."
    )
 
    assert candidate.hydraulic_diameter > 0.0, (
        f"{airflow_mode} candidate {candidate_index}: "
        "hydraulic diameter must be positive."
    )
 
    assert math.isfinite(
        candidate.reynolds_number
    )
 
    assert candidate.reynolds_number > 0.0
 
    assert math.isfinite(
        candidate.pressure_drop
    )
 
    assert candidate.pressure_drop >= 0.0
 
    assert math.isfinite(
        candidate.pumping_power
    )
 
    assert candidate.pumping_power >= 0.0
 
    assert math.isfinite(
        candidate.thermal_resistance
    )
 
    assert candidate.thermal_resistance > 0.0
 
    assert math.isfinite(
        candidate.estimated_base_temperature
    )
 
 
def verify_optimizer_result(
    optimization_result,
    airflow_mode: str,
) -> None:
    """
    Verify one complete optimizer result and its candidate
    collection.
    """
 
    assert optimization_result.has_feasible_design
 
    assert (
        optimization_result
        .feasible_candidate_count
        > 0
    )
 
    assert (
        optimization_result
        .feasible_candidate_count
        == len(
            optimization_result.candidates
        )
    )
 
    candidate_tuple = tuple(
        optimization_result.candidates
    )
 
    validate_completed_candidates(
        candidate_tuple
    )
 
    for index, candidate in enumerate(
        candidate_tuple,
        start=1,
    ):
        verify_candidate_state(
            candidate,
            index,
            airflow_mode,
        )
 
    assert (
        optimization_result.selection_result
        is not None
    )
 
    assert (
        optimization_result.selected_candidate
        is not None
    )
 
    assert (
        optimization_result.selected_candidate
        in optimization_result.candidates
    )
 
    assert (
        optimization_result
        .selection_result
        .uses_legacy_selection
    )
 
    # --------------------------------------------------
    # Legacy selection accepts optimizer candidates
    # --------------------------------------------------
 
    legacy_selection = select_candidates(
        candidate_tuple
    )
 
    assert (
        legacy_selection
        .uses_legacy_selection
    )
 
    assert (
        legacy_selection.selected_candidate
        is not None
    )
 
    lowest_resistance_candidate = min(
        candidate_tuple,
        key=lambda candidate: (
            candidate.thermal_resistance
        ),
    )
 
    assert (
        legacy_selection.selected_candidate
        is lowest_resistance_candidate
    )
 
    # --------------------------------------------------
    # Weighted selection accepts optimizer candidates
    # --------------------------------------------------
 
    weighted_selection = select_candidates(
        candidate_tuple,
        create_weighted_configuration(),
    )
 
    assert (
        weighted_selection
        .uses_weighted_selection
    )
 
    assert (
        weighted_selection.selected_candidate
        is not None
    )
 
    assert (
        weighted_selection.selected_candidate
        in candidate_tuple
    )
 
    # --------------------------------------------------
    # Pareto selection accepts optimizer candidates
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
        candidate_tuple,
        pareto_configuration,
    )
 
    assert (
        pareto_selection
        .uses_pareto_selection
    )
 
    assert (
        pareto_selection.selected_candidate_count
        >= 1
    )
 
    assert all(
        selected_candidate
        in candidate_tuple
        for selected_candidate
        in pareto_selection.selected_candidates
    )
 
 
def verify_selected_result_consistency(
    optimization_result,
) -> None:
    """
    Verify consistency between the selected DesignCandidate
    and the reporting-oriented ThermalResults object.
    """
 
    selected_candidate = (
        optimization_result.selected_candidate
    )
 
    thermal_result = (
        optimization_result.best_result
    )
 
    assert selected_candidate is not None
    assert thermal_result is not None
 
    assert math.isclose(
        thermal_result.hydraulic_diameter,
        (
            selected_candidate
            .hydraulic_diameter
            * 1000.0
        ),
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        thermal_result.reynolds_number,
        selected_candidate.reynolds_number,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        thermal_result.pressure_drop,
        selected_candidate.pressure_drop,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        thermal_result.pumping_power,
        selected_candidate.pumping_power,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        thermal_result.thermal_resistance,
        selected_candidate.thermal_resistance,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        thermal_result.estimated_base_temperature,
        (
            selected_candidate
            .estimated_base_temperature
        ),
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
 
def main() -> None:
    optimizer = ThermalOptimizer()
 
    # --------------------------------------------------
    # Fixed-velocity optimizer path
    # --------------------------------------------------
 
    fixed_velocity_result = (
        optimizer.optimize_with_details(
            create_fixed_velocity_requirements()
        )
    )
 
    verify_optimizer_result(
        fixed_velocity_result,
        "Fixed-velocity",
    )
 
    verify_selected_result_consistency(
        fixed_velocity_result
    )
 
    # --------------------------------------------------
    # Fan-coupled optimizer path
    # --------------------------------------------------
 
    fan_coupled_result = (
        optimizer.optimize_with_details(
            create_fan_coupled_requirements()
        )
    )
 
    verify_optimizer_result(
        fan_coupled_result,
        "Fan-coupled",
    )
 
    verify_selected_result_consistency(
        fan_coupled_result
    )
 
    print(
        "ALL OPTIMIZER CANDIDATE STATE "
        "INTEGRITY CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()