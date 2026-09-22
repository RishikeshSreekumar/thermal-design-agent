"""
Models representing weighted multi-objective scores for
evaluated design candidates.
"""
 
from dataclasses import dataclass
 
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.optimization_objective import (
    OptimizationObjective,
)
 
 
@dataclass(frozen=True)
class WeightedObjectiveContribution:
    """
    Weighted contribution of one normalized objective.
    """
 
    objective: OptimizationObjective
 
    normalized_value: float
 
    normalized_weight: float
 
    weighted_value: float
 
 
@dataclass(frozen=True)
class CandidateWeightedScore:
    """
    Complete weighted score for one candidate analysis.
 
    Lower total scores represent better candidates.
    """
 
    analysis: CandidateObjectiveAnalysis
 
    contributions: tuple[
        WeightedObjectiveContribution,
        ...
    ]
 
    total_score: float
 
    def get_contribution(
        self,
        objective_key: str,
    ) -> WeightedObjectiveContribution:
 
        normalized_key = (
            objective_key
            .strip()
            .lower()
        )
 
        for contribution in self.contributions:
            if (
                contribution
                .objective
                .candidate_attribute
                == normalized_key
            ):
                return contribution
 
        raise KeyError(
            f"No weighted contribution for objective "
            f"'{objective_key}'."
        )