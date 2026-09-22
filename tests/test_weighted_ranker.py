"""
Regression checks for weighted candidate ranking.
"""
 
from dataclasses import replace
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.weighted_ranker import (
    WeightedRankingError,
    rank_weighted_candidates,
)
from core.weighted_scorer import (
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
            third_candidate,
            first_candidate,
            second_candidate,
        )
    )
 
    configuration = ScoringConfiguration(
        objective_weights=(
            ObjectiveWeight(
                objective_key="thermal_resistance",
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
 
    scored_candidates = score_candidate_analyses(
        analyses,
        configuration,
    )
 
    ranking = rank_weighted_candidates(
        scored_candidates
    )
 
    assert len(ranking.ranked_candidates) == 3
 
    assert tuple(
        ranked_candidate.rank
        for ranked_candidate
        in ranking.ranked_candidates
    ) == (
        1,
        2,
        3,
    )
 
    assert (
        ranking.best_candidate
        .scored_candidate
        .analysis
        .candidate
        is first_candidate
    )
 
    assert (
        ranking.ranked_candidates[1]
        .scored_candidate
        .analysis
        .candidate
        is second_candidate
    )
 
    assert (
        ranking.ranked_candidates[2]
        .scored_candidate
        .analysis
        .candidate
        is third_candidate
    )
 
    tied_scores = (
        replace(
            scored_candidates[0],
            total_score=0.2,
        ),
        replace(
            scored_candidates[1],
            total_score=0.2,
        ),
        replace(
            scored_candidates[2],
            total_score=0.6,
        ),
    )
 
    tied_ranking = rank_weighted_candidates(
        tied_scores
    )
 
    assert tuple(
        ranked_candidate.rank
        for ranked_candidate
        in tied_ranking.ranked_candidates
    ) == (
        1,
        1,
        3,
    )
 
    try:
        rank_weighted_candidates(())
 
    except WeightedRankingError:
        pass
 
    else:
        raise AssertionError(
            "Empty score collection must raise "
            "WeightedRankingError."
        )
 
    try:
        rank_weighted_candidates(
            scored_candidates,
            score_tolerance=-1.0,
        )
 
    except WeightedRankingError:
        pass
 
    else:
        raise AssertionError(
            "Negative score tolerance must raise "
            "WeightedRankingError."
        )
 
    print(
        "ALL WEIGHTED RANKER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()