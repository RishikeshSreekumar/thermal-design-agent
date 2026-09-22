"""
objective_evaluator.py
 
Extracts validated raw optimization-objective values
from evaluated design candidates.
"""
 
import math
 
from models.design_candidate import DesignCandidate
from models.optimization_objective import (
    OptimizationObjective,
)
 
 
class ObjectiveEvaluationError(ValueError):
    """
    Raised when an optimization objective cannot be
    evaluated from a design candidate.
    """
 
 
def evaluate_objective(
    candidate: DesignCandidate,
    objective: OptimizationObjective,
) -> float:
    """
    Return the validated raw value of one optimization
    objective for a design candidate.
    """
 
    attribute_name = objective.candidate_attribute
 
    if not hasattr(candidate, attribute_name):
        raise ObjectiveEvaluationError(
            (
                f"DesignCandidate has no attribute "
                f"'{attribute_name}' for objective "
                f"'{objective.name}'."
            )
        )
 
    raw_value = getattr(
        candidate,
        attribute_name,
    )
 
    if isinstance(raw_value, bool) or not isinstance(
        raw_value,
        (int, float),
    ):
        raise ObjectiveEvaluationError(
            (
                f"Objective '{objective.name}' must resolve "
                f"to a numerical value. "
                f"Attribute '{attribute_name}' returned "
                f"{type(raw_value).__name__}."
            )
        )
 
    value = float(raw_value)
 
    if not math.isfinite(value):
        raise ObjectiveEvaluationError(
            (
                f"Objective '{objective.name}' returned a "
                f"non-finite value: {value}."
            )
        )
 
    return value