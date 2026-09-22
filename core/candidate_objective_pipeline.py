"""
candidate_objective_pipeline.py
 
Coordinates raw objective evaluation and normalization
for a collection of evaluated design candidates.
"""
 
from core.objective_normalizer import (
    normalize_objective_reports,
)
from core.objective_registry import (
    DEFAULT_OPTIMIZATION_OBJECTIVES,
)
from core.objective_report import (
    evaluate_objectives,
)
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.design_candidate import DesignCandidate
from models.optimization_objective import (
    OptimizationObjective,
)
 
 
class CandidateObjectivePipelineError(ValueError):
    """
    Raised when candidate objective analysis cannot be
    performed.
    """
 
 
def analyze_candidate_objectives(
    candidates: tuple[DesignCandidate, ...],
    objectives: tuple[
        OptimizationObjective,
        ...,
    ] = DEFAULT_OPTIMIZATION_OBJECTIVES,
) -> tuple[CandidateObjectiveAnalysis, ...]:
    """
    Evaluate and normalize the requested objectives for
    all supplied design candidates.
    """
 
    if not candidates:
        raise CandidateObjectivePipelineError(
            "At least one design candidate is required."
        )
 
    if not objectives:
        raise CandidateObjectivePipelineError(
            "At least one optimization objective is required."
        )
 
    raw_reports = tuple(
        evaluate_objectives(
            candidate,
            objectives,
        )
        for candidate in candidates
    )
 
    normalized_reports = (
        normalize_objective_reports(
            raw_reports
        )
    )
 
    return tuple(
        CandidateObjectiveAnalysis(
            candidate=candidate,
            raw_report=raw_report,
            normalized_report=normalized_report,
        )
        for (
            candidate,
            raw_report,
            normalized_report,
        ) in zip(
            candidates,
            raw_reports,
            normalized_reports,
            strict=True,
        )
    )