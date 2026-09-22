"""
pareto_dominance.py
 
Determines Pareto-dominance relationships between
normalized candidate objective analyses.
"""
 
import math
 
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.pareto_result import (
    ParetoDominanceResult,
)
 
 
class ParetoDominanceError(ValueError):
    """
    Raised when two candidate analyses cannot be compared.
    """
 
 
def compare_pareto_dominance(
    candidate: CandidateObjectiveAnalysis,
    compared_candidate: CandidateObjectiveAnalysis,
    *,
    objective_tolerance: float = 1e-12,
) -> ParetoDominanceResult:
    """
    Compare two normalized candidate objective analyses.
 
    Lower normalized objective values are always preferred.
    """
 
    if (
        not math.isfinite(objective_tolerance)
        or objective_tolerance < 0.0
    ):
        raise ParetoDominanceError(
            "Objective tolerance must be finite and "
            "non-negative."
        )
 
    candidate_values = _get_objective_values(
        candidate
    )
 
    compared_values = _get_objective_values(
        compared_candidate
    )
 
    if (
        candidate_values.keys()
        != compared_values.keys()
    ):
        raise ParetoDominanceError(
            "Candidate analyses do not contain matching "
            "optimization objectives."
        )
 
    candidate_dominates = _dominates(
        candidate_values,
        compared_values,
        objective_tolerance,
    )
 
    compared_candidate_dominates = _dominates(
        compared_values,
        candidate_values,
        objective_tolerance,
    )
 
    return ParetoDominanceResult(
        candidate=candidate,
        compared_candidate=compared_candidate,
        candidate_dominates=candidate_dominates,
        compared_candidate_dominates=(
            compared_candidate_dominates
        ),
    )
 
 
def candidate_dominates(
    candidate: CandidateObjectiveAnalysis,
    compared_candidate: CandidateObjectiveAnalysis,
    *,
    objective_tolerance: float = 1e-12,
) -> bool:
    """
    Return True when the first candidate Pareto-dominates
    the second candidate.
    """
 
    comparison = compare_pareto_dominance(
        candidate,
        compared_candidate,
        objective_tolerance=objective_tolerance,
    )
 
    return comparison.candidate_dominates
 
 
def _get_objective_values(
    analysis: CandidateObjectiveAnalysis,
) -> dict[str, float]:
    """
    Return normalized objective values keyed by candidate
    attribute.
    """
 
    if not analysis.normalized_report.results:
        raise ParetoDominanceError(
            "Candidate analysis contains no normalized "
            "objectives."
        )
 
    objective_values: dict[str, float] = {}
 
    for result in (
        analysis.normalized_report.results
    ):
        objective_key = (
            result.objective.candidate_attribute
        )
 
        if objective_key in objective_values:
            raise ParetoDominanceError(
                (
                    "Candidate analysis contains duplicate "
                    f"objective '{objective_key}'."
                )
            )
 
        normalized_value = (
            result.normalized_value
        )
 
        if not math.isfinite(normalized_value):
            raise ParetoDominanceError(
                (
                    f"Objective '{objective_key}' has a "
                    "non-finite normalized value."
                )
            )
 
        if not (
            0.0
            <= normalized_value
            <= 1.0
        ):
            raise ParetoDominanceError(
                (
                    f"Objective '{objective_key}' has a "
                    "normalized value outside the range "
                    "0.0 to 1.0."
                )
            )
 
        objective_values[
            objective_key
        ] = normalized_value
 
    return objective_values
 
 
def _dominates(
    candidate_values: dict[str, float],
    compared_values: dict[str, float],
    tolerance: float,
) -> bool:
    """
    Return True when the first value set is no worse in
    every objective and strictly better in at least one.
    """
 
    strictly_better = False
 
    for objective_key in candidate_values:
        candidate_value = candidate_values[
            objective_key
        ]
 
        compared_value = compared_values[
            objective_key
        ]
 
        if (
            candidate_value
            > compared_value + tolerance
        ):
            return False
 
        if (
            candidate_value
            < compared_value - tolerance
        ):
            strictly_better = True
 
    return strictly_better