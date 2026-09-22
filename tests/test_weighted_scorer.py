"""
Regression checks for weighted multi-objective scoring.
"""
 
import math
from dataclasses import replace
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.weighted_scorer import (
    WeightedScoringError,
    score_candidate_analyses,
)
from models.design_candidate import DesignCandidate
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
        pumping_power=0.1,
 
        thermal_resistance=0.5,
        estimated_base_temperature=112.5,
    )
 
 
def main() -> None:
    first_candidate = create_base_candidate()
 
    second_candidate = replace(
        first_candidate,
        thermal_resistance=0.7,
        pressure_drop=60.0,
        pumping_power=0.2,
    )
 
    third_candidate = replace(
        first_candidate,
        thermal_resistance=0.9,
        pressure_drop=20.0,
        pumping_power=0.3,
    )
 
    analyses = analyze_candidate_objectives(
        (
            first_candidate,
            second_candidate,
            third_candidate,
        )
    )
 
    configuration = ScoringConfiguration(
        objective_weights=(
            ObjectiveWeight(
                objective_key=(
                    "thermal_resistance"
                ),
                weight=60.0,
            ),
            ObjectiveWeight(
                objective_key="pressure_drop",
                weight=25.0,
            ),
            ObjectiveWeight(
                objective_key="pumping_power",
                weight=15.0,
            ),
        )
    )
 
    scored_candidates = (
        score_candidate_analyses(
            analyses,
            configuration,
        )
    )
 
    assert len(scored_candidates) == 3
 
    assert math.isclose(
        scored_candidates[0].total_score,
        0.25,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        scored_candidates[1].total_score,
        0.50,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        scored_candidates[2].total_score,
        0.75,
        abs_tol=1e-12,
    )
 
    thermal_contribution = (
        scored_candidates[1]
        .get_contribution(
            "thermal_resistance"
        )
    )
 
    assert math.isclose(
        thermal_contribution.normalized_value,
        0.5,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        thermal_contribution.normalized_weight,
        0.6,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        thermal_contribution.weighted_value,
        0.3,
        abs_tol=1e-12,
    )
 
    best_scored_candidate = min(
        scored_candidates,
        key=lambda result: result.total_score,
    )
 
    assert (
        best_scored_candidate.analysis.candidate
        is first_candidate
    )
 
    incomplete_configuration = (
        ScoringConfiguration(
            objective_weights=(
                ObjectiveWeight(
                    objective_key=(
                        "unknown_objective"
                    ),
                    weight=1.0,
                ),
            )
        )
    )
 
    try:
        score_candidate_analyses(
            analyses,
            incomplete_configuration,
        )
 
    except WeightedScoringError:
        pass
 
    else:
        raise AssertionError(
            "Missing configured objectives must raise "
            "WeightedScoringError."
        )
 
    try:
        score_candidate_analyses(
            (),
            configuration,
        )
 
    except WeightedScoringError:
        pass
 
    else:
        raise AssertionError(
            "Empty analyses must raise "
            "WeightedScoringError."
        )
 
    print(
        "ALL WEIGHTED SCORER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()