"""
Regression checks for the unified candidate-selection
result model.
"""
 
from dataclasses import replace
 
from core.pareto_optimization_pipeline import (
    optimize_candidates_by_pareto_front,
)
from core.weighted_optimization_pipeline import (
    optimize_candidates_by_weighted_score,
)
from models.candidate_selection_result import (
    CandidateSelectionResult,
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
    # Legacy selection
    # --------------------------------------------------
 
    legacy_configuration = (
        OptimizationSelectionConfiguration()
    )
 
    legacy_result = CandidateSelectionResult(
        configuration=legacy_configuration,
        selected_candidates=(
            thermal_focused_candidate,
        ),
    )
 
    assert (
        legacy_result.mode
        == OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    )
 
    assert legacy_result.uses_legacy_selection
 
    assert not legacy_result.uses_weighted_selection
 
    assert not legacy_result.uses_pareto_selection
 
    assert legacy_result.has_single_selected_candidate
 
    assert legacy_result.selected_candidate_count == 1
 
    assert (
        legacy_result.selected_candidate
        is thermal_focused_candidate
    )
 
    assert legacy_result.weighted_result is None
 
    assert legacy_result.pareto_result is None
 
    # --------------------------------------------------
    # Weighted selection
    # --------------------------------------------------
 
    scoring_configuration = (
        create_scoring_configuration()
    )
 
    weighted_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .WEIGHTED_SCORE
            ),
            scoring_configuration=(
                scoring_configuration
            ),
        )
    )
 
    weighted_optimization_result = (
        optimize_candidates_by_weighted_score(
            candidates,
            scoring_configuration,
        )
    )
 
    weighted_best_candidate = (
        weighted_optimization_result
        .best_candidate
        .scored_candidate
        .analysis
        .candidate
    )
 
    weighted_result = CandidateSelectionResult(
        configuration=weighted_configuration,
        selected_candidates=(
            weighted_best_candidate,
        ),
        weighted_result=(
            weighted_optimization_result
        ),
    )
 
    assert weighted_result.uses_weighted_selection
 
    assert not weighted_result.uses_legacy_selection
 
    assert not weighted_result.uses_pareto_selection
 
    assert weighted_result.has_single_selected_candidate
 
    assert weighted_result.selected_candidate_count == 1
 
    assert (
        weighted_result.selected_candidate
        is weighted_best_candidate
    )
 
    assert (
        weighted_result.weighted_result
        is weighted_optimization_result
    )
 
    assert weighted_result.pareto_result is None
 
    # --------------------------------------------------
    # Pareto selection
    # --------------------------------------------------
 
    pareto_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .PARETO_FRONT
            )
        )
    )
 
    pareto_optimization_result = (
        optimize_candidates_by_pareto_front(
            candidates
        )
    )
 
    expected_pareto_candidates = tuple(
        analysis.candidate
        for analysis
        in pareto_optimization_result
        .pareto_candidates
    )
 
    pareto_result = CandidateSelectionResult(
        configuration=pareto_configuration,
        selected_candidates=(
            expected_pareto_candidates
        ),
        pareto_result=(
            pareto_optimization_result
        ),
    )
 
    assert pareto_result.uses_pareto_selection
 
    assert not pareto_result.uses_legacy_selection
 
    assert not pareto_result.uses_weighted_selection
 
    assert pareto_result.selected_candidate_count == 3
 
    assert not pareto_result.has_single_selected_candidate
 
    assert pareto_result.selected_candidate is None
 
    assert (
        pareto_result.selected_candidates
        == expected_pareto_candidates
    )
 
    assert (
        pareto_result.pareto_result
        is pareto_optimization_result
    )
 
    assert pareto_result.weighted_result is None
 
    # --------------------------------------------------
    # Invalid empty selection
    # --------------------------------------------------
 
    try:
        CandidateSelectionResult(
            configuration=legacy_configuration,
            selected_candidates=(),
        )
 
    except ValueError as exc:
        assert (
            "At least one selected candidate"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Empty selected-candidate collection must "
            "be rejected."
        )
 
    # --------------------------------------------------
    # Invalid legacy result
    # --------------------------------------------------
 
    try:
        CandidateSelectionResult(
            configuration=legacy_configuration,
            selected_candidates=(
                thermal_focused_candidate,
                balanced_candidate,
            ),
        )
 
    except ValueError as exc:
        assert (
            "exactly one candidate"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Legacy selection with multiple candidates "
            "must be rejected."
        )
 
    # --------------------------------------------------
    # Invalid weighted result
    # --------------------------------------------------
 
    try:
        CandidateSelectionResult(
            configuration=weighted_configuration,
            selected_candidates=(
                weighted_best_candidate,
            ),
        )
 
    except ValueError as exc:
        assert (
            "requires a weighted optimization result"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Weighted selection without weighted result "
            "must be rejected."
        )
 
    wrong_weighted_candidate = next(
        candidate
        for candidate in candidates
        if candidate is not weighted_best_candidate
    )
 
    try:
        CandidateSelectionResult(
            configuration=weighted_configuration,
            selected_candidates=(
                wrong_weighted_candidate,
            ),
            weighted_result=(
                weighted_optimization_result
            ),
        )
 
    except ValueError as exc:
        assert (
            "does not match the best ranked candidate"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Weighted selection with the wrong candidate "
            "must be rejected."
        )
 
    # --------------------------------------------------
    # Invalid Pareto result
    # --------------------------------------------------
 
    try:
        CandidateSelectionResult(
            configuration=pareto_configuration,
            selected_candidates=(
                expected_pareto_candidates[0],
            ),
            pareto_result=(
                pareto_optimization_result
            ),
        )
 
    except ValueError as exc:
        assert (
            "candidate count does not match"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Incomplete Pareto selection must be "
            "rejected."
        )
 
    print(
        "ALL CANDIDATE SELECTION RESULT "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()