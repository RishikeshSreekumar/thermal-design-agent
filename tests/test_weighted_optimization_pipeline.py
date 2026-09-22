"""
Regression checks for the complete weighted optimization
pipeline.
"""
 
import math
from dataclasses import replace
 
from core.weighted_optimization_pipeline import (
    WeightedOptimizationPipelineError,
    optimize_candidates_by_weighted_score,
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
 
    candidates = (
        third_candidate,
        second_candidate,
        first_candidate,
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
 
    result = (
        optimize_candidates_by_weighted_score(
            candidates,
            configuration,
        )
    )
 
    assert result.configuration is configuration
 
    assert len(result.analyses) == 3
 
    assert len(
        result.scored_candidates
    ) == 3
 
    assert len(
        result.ranking.ranked_candidates
    ) == 3
 
    assert (
        result.best_candidate
        .scored_candidate
        .analysis
        .candidate
        is first_candidate
    )
 
    assert tuple(
        ranked_candidate.rank
        for ranked_candidate
        in result.ranking.ranked_candidates
    ) == (
        1,
        2,
        3,
    )
 
    assert math.isclose(
        result.best_candidate
        .scored_candidate
        .total_score,
        0.25,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        result.ranking
        .ranked_candidates[1]
        .scored_candidate
        .total_score,
        0.5,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        result.ranking
        .ranked_candidates[2]
        .scored_candidate
        .total_score,
        0.75,
        abs_tol=1e-12,
    )
 
    best_thermal_contribution = (
        result.best_candidate
        .scored_candidate
        .get_contribution(
            "thermal_resistance"
        )
    )
 
    assert math.isclose(
        best_thermal_contribution
        .normalized_value,
        0.0,
        abs_tol=1e-12,
    )
 
    try:
        optimize_candidates_by_weighted_score(
            (),
            configuration,
        )
 
    except WeightedOptimizationPipelineError:
        pass
 
    else:
        raise AssertionError(
            "Empty candidate collection must raise "
            "WeightedOptimizationPipelineError."
        )
 
    try:
        optimize_candidates_by_weighted_score(
            candidates,
            configuration,
            objectives=(),
        )
 
    except WeightedOptimizationPipelineError:
        pass
 
    else:
        raise AssertionError(
            "Empty custom objectives must raise "
            "WeightedOptimizationPipelineError."
        )
 
    print(
        "ALL WEIGHTED OPTIMIZATION PIPELINE "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()