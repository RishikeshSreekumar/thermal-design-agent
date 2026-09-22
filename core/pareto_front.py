"""
pareto_front.py
 
Extracts the non-dominated Pareto front from normalized
candidate objective analyses.
"""
 
import math
 
from core.pareto_dominance import (
    candidate_dominates,
)
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.pareto_result import (
    ParetoFrontResult,
)
 
 
class ParetoFrontError(ValueError):
    """
    Raised when a Pareto front cannot be extracted.
    """
 
 
def extract_pareto_front(
    analyses: tuple[
        CandidateObjectiveAnalysis,
        ...
    ],
    *,
    objective_tolerance: float = 1e-12,
) -> ParetoFrontResult:
    """
    Separate non-dominated and dominated candidate
    analyses.
 
    Candidate order is preserved in both returned groups.
    """
 
    if not analyses:
        raise ParetoFrontError(
            "At least one candidate analysis is required."
        )
 
    if (
        not math.isfinite(objective_tolerance)
        or objective_tolerance < 0.0
    ):
        raise ParetoFrontError(
            "Objective tolerance must be finite and "
            "non-negative."
        )
 
    pareto_candidates: list[
        CandidateObjectiveAnalysis
    ] = []
 
    dominated_candidates: list[
        CandidateObjectiveAnalysis
    ] = []
 
    for candidate_index, candidate in enumerate(
        analyses
    ):
        is_dominated = False
 
        for compared_index, compared_candidate in enumerate(
            analyses
        ):
            if candidate_index == compared_index:
                continue
 
            if candidate_dominates(
                compared_candidate,
                candidate,
                objective_tolerance=(
                    objective_tolerance
                ),
            ):
                is_dominated = True
                break
 
        if is_dominated:
            dominated_candidates.append(
                candidate
            )
 
        else:
            pareto_candidates.append(
                candidate
            )
 
    return ParetoFrontResult(
        pareto_candidates=tuple(
            pareto_candidates
        ),
        dominated_candidates=tuple(
            dominated_candidates
        ),
    )