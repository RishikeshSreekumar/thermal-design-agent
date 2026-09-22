"""
weighted_scorer.py
 
Calculates weighted multi-objective scores from normalized
candidate objective analyses.
"""
 
import math
 
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.scoring_configuration import (
    ScoringConfiguration,
)
from models.weighted_score import (
    CandidateWeightedScore,
    WeightedObjectiveContribution,
)
 
 
class WeightedScoringError(ValueError):
    """
    Raised when a candidate cannot be scored using the
    supplied scoring configuration.
    """
 
 
def score_candidate_analyses(
    analyses: tuple[
        CandidateObjectiveAnalysis,
        ...
    ],
    configuration: ScoringConfiguration,
) -> tuple[CandidateWeightedScore, ...]:
    """
    Calculate weighted scores for candidate analyses.
 
    Candidate order is preserved in the returned tuple.
    """
 
    if not analyses:
        raise WeightedScoringError(
            "At least one candidate analysis is required."
        )
 
    normalized_weights = {
        objective_weight.objective_key: (
            objective_weight.weight
            / configuration.total_weight
        )
        for objective_weight
        in configuration.objective_weights
    }
 
    scored_candidates: list[
        CandidateWeightedScore
    ] = []
 
    for analysis in analyses:
        contributions: list[
            WeightedObjectiveContribution
        ] = []
 
        for (
            objective_key,
            normalized_weight,
        ) in normalized_weights.items():
            try:
                normalized_value = (
                    analysis
                    .normalized_report
                    .get_normalized_value(
                        objective_key
                    )
                )
 
            except KeyError as exc:
                raise WeightedScoringError(
                    (
                        f"Candidate analysis does not "
                        f"contain the configured objective "
                        f"'{objective_key}'."
                    )
                ) from exc
 
            if not math.isfinite(
                normalized_value
            ):
                raise WeightedScoringError(
                    (
                        f"Objective '{objective_key}' has "
                        "a non-finite normalized value."
                    )
                )
 
            if not (
                0.0
                <= normalized_value
                <= 1.0
            ):
                raise WeightedScoringError(
                    (
                        f"Objective '{objective_key}' has "
                        "a normalized value outside the "
                        "range 0.0 to 1.0."
                    )
                )
 
            objective_result = next(
                result
                for result
                in analysis.normalized_report.results
                if (
                    result
                    .objective
                    .candidate_attribute
                    == objective_key
                )
            )
 
            weighted_value = (
                normalized_value
                * normalized_weight
            )
 
            contributions.append(
                WeightedObjectiveContribution(
                    objective=(
                        objective_result.objective
                    ),
                    normalized_value=(
                        normalized_value
                    ),
                    normalized_weight=(
                        normalized_weight
                    ),
                    weighted_value=weighted_value,
                )
            )
 
        total_score = sum(
            contribution.weighted_value
            for contribution in contributions
        )
 
        scored_candidates.append(
            CandidateWeightedScore(
                analysis=analysis,
                contributions=tuple(
                    contributions
                ),
                total_score=total_score,
            )
        )
 
    return tuple(scored_candidates)