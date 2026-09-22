"""
Models representing the complete result of weighted
multi-objective candidate optimization.
"""
 
from dataclasses import dataclass
 
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.scoring_configuration import (
    ScoringConfiguration,
)
from models.weighted_ranking import (
    RankedCandidate,
    WeightedRankingResult,
)
from models.weighted_score import (
    CandidateWeightedScore,
)
 
 
@dataclass(frozen=True)
class WeightedOptimizationResult:
    """
    Complete output of the weighted optimization pipeline.
    """
 
    configuration: ScoringConfiguration
 
    analyses: tuple[
        CandidateObjectiveAnalysis,
        ...
    ]
 
    scored_candidates: tuple[
        CandidateWeightedScore,
        ...
    ]
 
    ranking: WeightedRankingResult
 
    @property
    def best_candidate(
        self,
    ) -> RankedCandidate:
        return self.ranking.best_candidate