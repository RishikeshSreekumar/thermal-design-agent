"""
Models representing evaluated and normalized
optimization objectives for design candidates.
"""
 
from dataclasses import dataclass
 
from models.optimization_objective import (
    OptimizationObjective,
)
 
 
@dataclass(frozen=True)
class ObjectiveResult:
    """
    Raw evaluated value of one optimization objective.
    """
 
    objective: OptimizationObjective
 
    value: float
 
 
@dataclass(frozen=True)
class NormalizedObjectiveResult:
    """
    Raw and normalized values of one optimization
    objective.
    """
 
    objective: OptimizationObjective
 
    raw_value: float
 
    normalized_value: float
 
 
@dataclass(frozen=True)
class ObjectiveEvaluationResult:
    """
    Collection of raw evaluated optimization objectives
    for one design candidate.
    """
 
    results: tuple[ObjectiveResult, ...]
 
    def get_value(
        self,
        objective_key: str,
    ) -> float:
 
        normalized_key = objective_key.strip().lower()
 
        for result in self.results:
 
            if (
                result.objective.candidate_attribute
                == normalized_key
            ):
                return result.value
 
        raise KeyError(
            f"No objective named '{objective_key}'."
        )
 
 
@dataclass(frozen=True)
class NormalizedObjectiveEvaluationResult:
    """
    Collection of normalized optimization objectives
    for one design candidate.
    """
 
    results: tuple[NormalizedObjectiveResult, ...]
 
    def get_normalized_value(
        self,
        objective_key: str,
    ) -> float:
 
        normalized_key = objective_key.strip().lower()
 
        for result in self.results:
 
            if (
                result.objective.candidate_attribute
                == normalized_key
            ):
                return result.normalized_value
 
        raise KeyError(
            f"No normalized objective named "
            f"'{objective_key}'."
        )
 
    def get_raw_value(
        self,
        objective_key: str,
    ) -> float:
 
        normalized_key = objective_key.strip().lower()
 
        for result in self.results:
 
            if (
                result.objective.candidate_attribute
                == normalized_key
            ):
                return result.raw_value
 
        raise KeyError(
            f"No normalized objective named "
            f"'{objective_key}'."
        )