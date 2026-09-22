"""
Models representing ranked weighted-scoring results.
"""
 
from dataclasses import dataclass
 
from models.weighted_score import (
    CandidateWeightedScore,
)
 
 
@dataclass(frozen=True)
class RankedCandidate:
    """
    One candidate with its weighted ranking position.
    """
 
    rank: int
 
    scored_candidate: CandidateWeightedScore
 
 
@dataclass(frozen=True)
class WeightedRankingResult:
    """
    Complete weighted ranking of candidate designs.
    """
 
    ranked_candidates: tuple[
        RankedCandidate,
        ...
    ]
 
    @property
    def best_candidate(
        self,
    ) -> RankedCandidate:
        if not self.ranked_candidates:
            raise ValueError(
                "Weighted ranking contains no candidates."
            )
 
        return self.ranked_candidates[0]