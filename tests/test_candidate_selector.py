"""
Regression checks for the unified candidate-selection
coordinator.
"""
 
from dataclasses import replace
 
from core.candidate_selector import (
    CandidateSelectionError,
    select_candidates,
)
from models.design_candidate import DesignCandidate
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def create_base_candidate() -> DesignCandidate:
    return DesignCandidate(
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
        pressure_drop=100.0,
        pumping_power=0.3,
 
        thermal_resistance=0.5,
        estimated_base_temperature=112.5,
 
        hydraulic_diameter=(
            0.0026666666666666666
        ),
    )
 
 
def create_scoring_configuration(
) -> ScoringConfiguration:
    return ScoringConfiguration(
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
 
 
def main() -> None:
    thermal_focused_candidate = (
        create_base_candidate()
    )
 
    balanced_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.7,
        pressure_drop=60.0,
        pumping_power=0.2,
    )
 
    airflow_focused_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.9,
        pressure_drop=20.0,
        pumping_power=0.1,
    )
 
    dominated_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.8,
        pressure_drop=80.0,
        pumping_power=0.25,
    )
 
    candidates = (
        dominated_candidate,
        airflow_focused_candidate,
        balanced_candidate,
        thermal_focused_candidate,
    )
 
    # --------------------------------------------------
    # Default legacy selection
    # --------------------------------------------------
 
    default_result = select_candidates(
        candidates
    )
 
    assert (
        default_result.mode
        == OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    )
 
    assert default_result.uses_legacy_selection
 
    assert default_result.selected_candidate_count == 1
 
    assert (
        default_result.selected_candidate
        is thermal_focused_candidate
    )
 
    assert default_result.weighted_result is None
 
    assert default_result.pareto_result is None
 
    # --------------------------------------------------
    # Explicit legacy selection
    # --------------------------------------------------
 
    legacy_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .MINIMUM_THERMAL_RESISTANCE
            )
        )
    )
 
    explicit_legacy_result = (
        select_candidates(
            candidates,
            legacy_configuration,
        )
    )
 
    assert (
        explicit_legacy_result.selected_candidate
        is thermal_focused_candidate
    )
 
    assert (
        explicit_legacy_result.configuration
        is legacy_configuration
    )
 
    # --------------------------------------------------
    # Legacy tie preserves candidate order
    # --------------------------------------------------
 
    tied_candidate = replace(
        thermal_focused_candidate,
        pressure_drop=90.0,
    )
 
    tie_result = select_candidates(
        (
            tied_candidate,
            thermal_focused_candidate,
        )
    )
 
    assert (
        tie_result.selected_candidate
        is tied_candidate
    )
 
    # --------------------------------------------------
    # Weighted selection
    # --------------------------------------------------
 
    weighted_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .WEIGHTED_SCORE
            ),
            scoring_configuration=(
                create_scoring_configuration()
            ),
        )
    )
 
    weighted_result = select_candidates(
        candidates,
        weighted_configuration,
    )
 
    assert weighted_result.uses_weighted_selection
 
    assert weighted_result.selected_candidate_count == 1
 
    assert weighted_result.selected_candidate is not None
 
    assert weighted_result.weighted_result is not None
 
    assert weighted_result.pareto_result is None
 
    assert (
        weighted_result.selected_candidate
        is weighted_result
        .weighted_result
        .best_candidate
        .scored_candidate
        .analysis
        .candidate
    )
 
    # --------------------------------------------------
    # Pareto-front selection
    # --------------------------------------------------
 
    pareto_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .PARETO_FRONT
            )
        )
    )
 
    pareto_result = select_candidates(
        candidates,
        pareto_configuration,
    )
 
    assert pareto_result.uses_pareto_selection
 
    assert pareto_result.selected_candidate_count == 3
 
    assert pareto_result.selected_candidate is None
 
    assert pareto_result.weighted_result is None
 
    assert pareto_result.pareto_result is not None
 
    assert pareto_result.selected_candidates == (
        airflow_focused_candidate,
        balanced_candidate,
        thermal_focused_candidate,
    )
 
    # --------------------------------------------------
    # Single-candidate Pareto result
    # --------------------------------------------------
 
    single_pareto_result = select_candidates(
        (
            thermal_focused_candidate,
        ),
        pareto_configuration,
    )
 
    assert (
        single_pareto_result
        .selected_candidate_count
        == 1
    )
 
    assert (
        single_pareto_result
        .selected_candidate
        is thermal_focused_candidate
    )
 
    assert (
        single_pareto_result
        .pareto_result
        is not None
    )
 
    # --------------------------------------------------
    # Empty candidates
    # --------------------------------------------------
 
    try:
        select_candidates(())
 
    except CandidateSelectionError as exc:
        assert (
            "At least one evaluated design candidate"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Empty candidate collection must raise "
            "CandidateSelectionError."
        )
 
    # --------------------------------------------------
    # Invalid configuration type
    # --------------------------------------------------
 
    try:
        select_candidates(
            candidates,
            "weighted_score",
        )
 
    except CandidateSelectionError as exc:
        assert (
            "OptimizationSelectionConfiguration or None"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid configuration type must raise "
            "CandidateSelectionError."
        )
 
    print(
        "ALL CANDIDATE SELECTOR CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()