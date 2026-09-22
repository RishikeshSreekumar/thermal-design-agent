"""
weighted_optimization_pipeline.py
 
Coordinates objective analysis, weighted scoring, and
candidate ranking through one public function.
"""
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.weighted_ranker import (
    rank_weighted_candidates,
)
from core.weighted_scorer import (
    score_candidate_analyses,
)
from models.design_candidate import DesignCandidate
from models.optimization_objective import (
    OptimizationObjective,
)
from models.scoring_configuration import (
    ScoringConfiguration,
)
from models.weighted_optimization_result import (
    WeightedOptimizationResult,
)
 
 
class WeightedOptimizationPipelineError(
    ValueError
):
    """
    Raised when the complete weighted optimization
    workflow cannot be performed.
    """
 
 
def optimize_candidates_by_weighted_score(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    configuration: ScoringConfiguration,
    *,
    objectives: tuple[
        OptimizationObjective,
        ...,
    ] | None = None,
    score_tolerance: float = 1e-12,
) -> WeightedOptimizationResult:
    """
    Analyze, score, and rank design candidates using a
    weighted multi-objective configuration.
    """
 
    if not candidates:
        raise WeightedOptimizationPipelineError(
            "At least one design candidate is required."
        )
 
    if objectives is None:
        analyses = analyze_candidate_objectives(
            candidates
        )
 
    else:
        if not objectives:
            raise WeightedOptimizationPipelineError(
                (
                    "Custom optimization objectives "
                    "cannot be empty."
                )
            )
 
        analyses = analyze_candidate_objectives(
            candidates,
            objectives,
        )
 
    scored_candidates = (
        score_candidate_analyses(
            analyses,
            configuration,
        )
    )
 
    ranking = rank_weighted_candidates(
        scored_candidates,
        score_tolerance=score_tolerance,
    )
 
    return WeightedOptimizationResult(
        configuration=configuration,
        analyses=analyses,
        scored_candidates=scored_candidates,
        ranking=ranking,
    )