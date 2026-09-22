"""
pareto_metadata.py
 
Calculates candidate-level Pareto dominance metadata for
a complete collection of normalized objective analyses.
"""
 
import math
 
from core.pareto_dominance import (
    ParetoDominanceError,
    compare_pareto_dominance,
)
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.pareto_result import (
    ParetoCandidateMetadata,
    ParetoMetadataResult,
)
 
 
class ParetoMetadataError(ValueError):
    """
    Raised when Pareto metadata cannot be calculated.
    """
 
 
def analyze_pareto_metadata(
    analyses: tuple[
        CandidateObjectiveAnalysis,
        ...
    ],
    *,
    objective_tolerance: float = 1e-12,
) -> ParetoMetadataResult:
    """
    Calculate dominance counts and Pareto membership for
    every candidate analysis.
 
    Candidate order is preserved in the returned result.
    """
 
    if not analyses:
        raise ParetoMetadataError(
            "At least one candidate analysis is required."
        )
 
    if (
        not math.isfinite(objective_tolerance)
        or objective_tolerance < 0.0
    ):
        raise ParetoMetadataError(
            "Objective tolerance must be finite and "
            "non-negative."
        )
 
    dominates_counts = [
        0
        for _ in analyses
    ]
 
    dominated_by_counts = [
        0
        for _ in analyses
    ]
 
    for first_index in range(
        len(analyses) - 1
    ):
        first_analysis = analyses[
            first_index
        ]
 
        for second_index in range(
            first_index + 1,
            len(analyses),
        ):
            second_analysis = analyses[
                second_index
            ]
 
            try:
                comparison = (
                    compare_pareto_dominance(
                        first_analysis,
                        second_analysis,
                        objective_tolerance=(
                            objective_tolerance
                        ),
                    )
                )
 
            except ParetoDominanceError as exc:
                raise ParetoMetadataError(
                    (
                        "Unable to compare candidate "
                        f"analyses at indexes {first_index} "
                        f"and {second_index}."
                    )
                ) from exc
 
            if comparison.candidate_dominates:
                dominates_counts[
                    first_index
                ] += 1
 
                dominated_by_counts[
                    second_index
                ] += 1
 
            elif (
                comparison
                .compared_candidate_dominates
            ):
                dominates_counts[
                    second_index
                ] += 1
 
                dominated_by_counts[
                    first_index
                ] += 1
 
    metadata = tuple(
        ParetoCandidateMetadata(
            analysis=analysis,
            dominates_count=(
                dominates_counts[index]
            ),
            dominated_by_count=(
                dominated_by_counts[index]
            ),
        )
        for index, analysis in enumerate(
            analyses
        )
    )
 
    return ParetoMetadataResult(
        candidates=metadata
    )