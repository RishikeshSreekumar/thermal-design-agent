"""
pareto_optimization_pipeline.py
 
Coordinates objective analysis, Pareto metadata
calculation, and Pareto-front extraction through one
public function.
"""
 
import math
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.pareto_front import (
    ParetoFrontError,
    extract_pareto_front,
)
from core.pareto_metadata import (
    ParetoMetadataError,
    analyze_pareto_metadata,
)
from models.design_candidate import DesignCandidate
from models.optimization_objective import (
    OptimizationObjective,
)
from models.pareto_optimization_result import (
    ParetoOptimizationResult,
)
 
 
class ParetoOptimizationPipelineError(
    ValueError
):
    """
    Raised when the complete Pareto optimization workflow
    cannot be performed.
    """
 
 
def optimize_candidates_by_pareto_front(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    *,
    objectives: tuple[
        OptimizationObjective,
        ...,
    ] | None = None,
    objective_tolerance: float = 1e-12,
) -> ParetoOptimizationResult:
    """
    Analyze design candidates and extract the
    non-dominated Pareto front.
    """
 
    if not candidates:
        raise ParetoOptimizationPipelineError(
            "At least one design candidate is required."
        )
 
    if (
        not math.isfinite(objective_tolerance)
        or objective_tolerance < 0.0
    ):
        raise ParetoOptimizationPipelineError(
            "Objective tolerance must be finite and "
            "non-negative."
        )
 
    if objectives is None:
        analyses = analyze_candidate_objectives(
            candidates
        )
 
    else:
        if not objectives:
            raise ParetoOptimizationPipelineError(
                "Custom optimization objectives cannot "
                "be empty."
            )
 
        analyses = analyze_candidate_objectives(
            candidates,
            objectives,
        )
 
    try:
        metadata = analyze_pareto_metadata(
            analyses,
            objective_tolerance=(
                objective_tolerance
            ),
        )
 
        front = extract_pareto_front(
            analyses,
            objective_tolerance=(
                objective_tolerance
            ),
        )
 
    except (
        ParetoMetadataError,
        ParetoFrontError,
    ) as exc:
        raise ParetoOptimizationPipelineError(
            "Pareto optimization could not be completed."
        ) from exc
 
    _validate_pipeline_consistency(
        analyses=analyses,
        metadata=metadata,
        front=front,
    )
 
    return ParetoOptimizationResult(
        analyses=analyses,
        metadata=metadata,
        front=front,
    )
 
 
def _validate_pipeline_consistency(
    analyses,
    metadata,
    front,
) -> None:
    """
    Verify that metadata classification and front
    extraction produced matching candidate groups.
    """
 
    if (
        metadata.total_candidate_count
        != len(analyses)
    ):
        raise ParetoOptimizationPipelineError(
            "Pareto metadata candidate count does not "
            "match the analyzed candidate count."
        )
 
    if (
        front.total_candidate_count
        != len(analyses)
    ):
        raise ParetoOptimizationPipelineError(
            "Pareto-front candidate count does not match "
            "the analyzed candidate count."
        )
 
    metadata_pareto_analyses = tuple(
        candidate_metadata.analysis
        for candidate_metadata
        in metadata.pareto_candidates
    )
 
    if (
        metadata_pareto_analyses
        != front.pareto_candidates
    ):
        raise ParetoOptimizationPipelineError(
            "Pareto metadata and Pareto-front extraction "
            "produced inconsistent non-dominated sets."
        )
 
    metadata_dominated_analyses = tuple(
        candidate_metadata.analysis
        for candidate_metadata
        in metadata.dominated_candidates
    )
 
    if (
        metadata_dominated_analyses
        != front.dominated_candidates
    ):
        raise ParetoOptimizationPipelineError(
            "Pareto metadata and Pareto-front extraction "
            "produced inconsistent dominated sets."
        )