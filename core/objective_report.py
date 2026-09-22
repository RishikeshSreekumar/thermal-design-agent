"""
Builds objective-evaluation reports for
design candidates.
"""
 
from core.objective_evaluator import (
    evaluate_objective,
)
from models.design_candidate import DesignCandidate
from models.objective_result import (
    ObjectiveEvaluationResult,
    ObjectiveResult,
)
from models.optimization_objective import (
    OptimizationObjective,
)
 
 
def evaluate_objectives(
    candidate: DesignCandidate,
    objectives: tuple[
        OptimizationObjective,
        ...
    ],
) -> ObjectiveEvaluationResult:
    """
    Evaluate every requested optimization objective.
    """
 
    results: list[ObjectiveResult] = []
 
    for objective in objectives:
 
        value = evaluate_objective(
            candidate,
            objective,
        )
 
        results.append(
            ObjectiveResult(
                objective=objective,
                value=value,
            )
        )
 
    return ObjectiveEvaluationResult(
        results=tuple(results)
    )