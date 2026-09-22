"""
objective_normalizer.py
 
Normalizes objective values across a collection of
evaluated design candidates.
"""
 
import math
 
from models.objective_result import (
    NormalizedObjectiveEvaluationResult,
    NormalizedObjectiveResult,
    ObjectiveEvaluationResult,
)
from models.optimization_objective import (
    ObjectiveDirection,
)
 
 
class ObjectiveNormalizationError(ValueError):
    """
    Raised when objective reports cannot be normalized.
    """
 
 
def normalize_objective_reports(
    reports: tuple[
        ObjectiveEvaluationResult,
        ...
    ],
) -> tuple[
    NormalizedObjectiveEvaluationResult,
    ...
]:
    """
    Normalize matching objectives across candidate reports.
 
    A normalized value of zero represents the best value
    and one represents the worst value.
    """
 
    if not reports:
        raise ObjectiveNormalizationError(
            "At least one objective report is required."
        )
 
    _validate_report_structure(reports)
 
    normalized_report_results: list[
        list[NormalizedObjectiveResult]
    ] = [
        []
        for _ in reports
    ]
 
    objective_count = len(
        reports[0].results
    )
 
    for objective_index in range(
        objective_count
    ):
        objective = (
            reports[0]
            .results[objective_index]
            .objective
        )
 
        raw_values = tuple(
            report.results[
                objective_index
            ].value
            for report in reports
        )
 
        normalized_values = _normalize_values(
            raw_values,
            objective.direction,
        )
 
        for report_index, normalized_value in enumerate(
            normalized_values
        ):
            normalized_report_results[
                report_index
            ].append(
                NormalizedObjectiveResult(
                    objective=objective,
                    raw_value=raw_values[
                        report_index
                    ],
                    normalized_value=(
                        normalized_value
                    ),
                )
            )
 
    return tuple(
        NormalizedObjectiveEvaluationResult(
            results=tuple(results)
        )
        for results in normalized_report_results
    )
 
 
def _normalize_values(
    values: tuple[float, ...],
    direction: ObjectiveDirection,
) -> tuple[float, ...]:
    """
    Normalize one objective across all candidates.
    """
 
    minimum_value = min(values)
    maximum_value = max(values)
 
    value_range = (
        maximum_value - minimum_value
    )
 
    if math.isclose(
        value_range,
        0.0,
        rel_tol=0.0,
        abs_tol=1e-15,
    ):
        return tuple(
            0.0
            for _ in values
        )
 
    if direction is ObjectiveDirection.MINIMIZE:
        return tuple(
            (value - minimum_value)
            / value_range
            for value in values
        )
 
    if direction is ObjectiveDirection.MAXIMIZE:
        return tuple(
            (maximum_value - value)
            / value_range
            for value in values
        )
 
    raise ObjectiveNormalizationError(
        f"Unsupported objective direction: "
        f"{direction!r}."
    )
 
 
def _validate_report_structure(
    reports: tuple[
        ObjectiveEvaluationResult,
        ...
    ],
) -> None:
    """
    Verify that every report contains the same objectives
    in the same order.
    """
 
    reference_results = reports[0].results
 
    if not reference_results:
        raise ObjectiveNormalizationError(
            "Objective reports cannot be empty."
        )
 
    reference_attributes = tuple(
        result.objective.candidate_attribute
        for result in reference_results
    )
 
    for report_index, report in enumerate(
        reports[1:],
        start=1,
    ):
        report_attributes = tuple(
            result.objective.candidate_attribute
            for result in report.results
        )
 
        if (
            report_attributes
            != reference_attributes
        ):
            raise ObjectiveNormalizationError(
                (
                    "Objective report at index "
                    f"{report_index} does not match "
                    "the reference report structure."
                )
            )