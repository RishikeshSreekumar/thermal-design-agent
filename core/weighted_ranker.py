"""
weighted_ranker.py
 
Ranks candidate weighted scores from best to worst.
"""
 
import math
 
from models.weighted_ranking import (
    RankedCandidate,
    WeightedRankingResult,
)
from models.weighted_score import (
    CandidateWeightedScore,
)
 
 
class WeightedRankingError(ValueError):
    """
    Raised when weighted candidates cannot be ranked.
    """
 
 
def rank_weighted_candidates(
    scored_candidates: tuple[
        CandidateWeightedScore,
        ...
    ],
    *,
    score_tolerance: float = 1e-12,
) -> WeightedRankingResult:
    """
    Rank weighted candidates using ascending total score.
 
    Candidates whose scores are equal within the supplied
    tolerance receive the same rank.
    """
 
    if not scored_candidates:
        raise WeightedRankingError(
            "At least one scored candidate is required."
        )
 
    if (
        not math.isfinite(score_tolerance)
        or score_tolerance < 0.0
    ):
        raise WeightedRankingError(
            "Score tolerance must be finite and "
            "non-negative."
        )
 
    for candidate_index, scored_candidate in enumerate(
        scored_candidates
    ):
        if not math.isfinite(
            scored_candidate.total_score
        ):
            raise WeightedRankingError(
                (
                    "Candidate score at index "
                    f"{candidate_index} is not finite."
                )
            )
 
    sorted_candidates = tuple(
        sorted(
            scored_candidates,
            key=lambda candidate: (
                candidate.total_score
            ),
        )
    )
 
    ranked_candidates: list[
        RankedCandidate
    ] = []
 
    previous_score: float | None = None
    current_rank = 0
 
    for position, scored_candidate in enumerate(
        sorted_candidates,
        start=1,
    ):
        if (
            previous_score is None
            or not math.isclose(
                scored_candidate.total_score,
                previous_score,
                rel_tol=0.0,
                abs_tol=score_tolerance,
            )
        ):
            current_rank = position
 
        ranked_candidates.append(
            RankedCandidate(
                rank=current_rank,
                scored_candidate=scored_candidate,
            )
        )
 
        previous_score = scored_candidate.total_score
 
    return WeightedRankingResult(
        ranked_candidates=tuple(
            ranked_candidates
        )
    )