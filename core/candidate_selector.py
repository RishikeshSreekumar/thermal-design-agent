"""
candidate_selector.py
 
Coordinates selection from an already evaluated
collection of thermal-design candidates.
 
Supported selection modes:
 
- Minimum thermal resistance
- Weighted multi-objective score
- Pareto front
"""
from core.candidate_state_validator import (
    CandidateStateValidationError,
    validate_completed_candidates,
) 
from core.objective_registry import (
    DEFAULT_OPTIMIZATION_OBJECTIVES,
)
from core.pareto_optimization_pipeline import (
    ParetoOptimizationPipelineError,
    optimize_candidates_by_pareto_front,
)
from core.weighted_optimization_pipeline import (
    WeightedOptimizationPipelineError,
    optimize_candidates_by_weighted_score,
)
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.design_candidate import DesignCandidate
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
 
 
class CandidateSelectionError(ValueError):
    """
    Raised when evaluated candidates cannot be selected
    using the requested selection configuration.
    """
 
 
def select_candidates(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    configuration: (
        OptimizationSelectionConfiguration | None
    ) = None,
) -> CandidateSelectionResult:
    """
    Select from evaluated design candidates using the
    configured selection mode.
 
    When no configuration is supplied, legacy
    minimum-thermal-resistance selection is used.
    """
 
    if not candidates:
        raise CandidateSelectionError(
            "At least one evaluated design candidate is "
            "required."
        )
 
    resolved_configuration = (
        configuration
        if configuration is not None
        else OptimizationSelectionConfiguration()
    )
 
    if not isinstance(
        resolved_configuration,
        OptimizationSelectionConfiguration,
    ):
        raise CandidateSelectionError(
            "Configuration must be an "
            "OptimizationSelectionConfiguration or None."
        )
 
    require_physical_properties = (
        _configuration_requires_physical_properties(
            resolved_configuration
        )
    )
 
    try:
        validate_completed_candidates(
            candidates,
            require_physical_properties=(
                require_physical_properties
            ),
        )
 
    except CandidateStateValidationError as exc:
        raise CandidateSelectionError(
            "Candidate selection requires complete and "
            "physically valid evaluated candidates."
        ) from exc
 
    if not isinstance(
        resolved_configuration,
        OptimizationSelectionConfiguration,
    ):
        raise CandidateSelectionError(
            "Configuration must be an "
            "OptimizationSelectionConfiguration or None."
        )
 
    mode = resolved_configuration.mode
 
    if (
        mode
        == OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    ):
        return _select_minimum_thermal_resistance(
            candidates,
            resolved_configuration,
        )
 
    if (
        mode
        == OptimizationSelectionMode
        .WEIGHTED_SCORE
    ):
        return _select_by_weighted_score(
            candidates,
            resolved_configuration,
        )
 
    if (
        mode
        == OptimizationSelectionMode
        .PARETO_FRONT
    ):
        return _select_by_pareto_front(
            candidates,
            resolved_configuration,
        )
 
    raise CandidateSelectionError(
        "Unsupported optimization selection mode."
    )
 
def _configuration_requires_physical_properties(
    configuration: (
        OptimizationSelectionConfiguration
    ),
) -> bool:
    """
    Return True when the configured selection depends on
    physical material properties.
 
    Mass currently requires resolved solid volume and
    mass state. The helper is intentionally based on the
    objective's candidate attribute rather than its
    display name.
    """
 
    if (
        configuration.mode
        == OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    ):
        return False
 
    objectives = (
        configuration.objectives
        if configuration.objectives is not None
        else DEFAULT_OPTIMIZATION_OBJECTIVES
    )
 
    return any(
        objective.candidate_attribute
        == "mass"
        for objective in objectives
    )

def _select_minimum_thermal_resistance(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    configuration: (
        OptimizationSelectionConfiguration
    ),
) -> CandidateSelectionResult:
    """
    Preserve the existing minimum-thermal-resistance
    candidate-selection behaviour.
    """
 
    selected_candidate = min(
        candidates,
        key=lambda candidate: (
            candidate.thermal_resistance
        ),
    )
 
    return CandidateSelectionResult(
        configuration=configuration,
        selected_candidates=(
            selected_candidate,
        ),
    )
 
 
def _select_by_weighted_score(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    configuration: (
        OptimizationSelectionConfiguration
    ),
) -> CandidateSelectionResult:
    """
    Run weighted multi-objective optimization and return
    the best-ranked candidate.
    """
 
    scoring_configuration = (
        configuration.scoring_configuration
    )
 
    if scoring_configuration is None:
        raise CandidateSelectionError(
            "Weighted-score selection requires a "
            "scoring configuration."
        )
 
    try:
        weighted_result = (
            optimize_candidates_by_weighted_score(
                candidates,
                scoring_configuration,
                objectives=configuration.objectives,
                score_tolerance=(
                    configuration.score_tolerance
                ),
            )
        )
 
    except WeightedOptimizationPipelineError as exc:
        raise CandidateSelectionError(
            "Weighted candidate selection could not be "
            "completed."
        ) from exc
 
    selected_candidate = (
        weighted_result
        .best_candidate
        .scored_candidate
        .analysis
        .candidate
    )
 
    return CandidateSelectionResult(
        configuration=configuration,
        selected_candidates=(
            selected_candidate,
        ),
        weighted_result=weighted_result,
    )
 
 
def _select_by_pareto_front(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    configuration: (
        OptimizationSelectionConfiguration
    ),
) -> CandidateSelectionResult:
    """
    Run Pareto optimization and return every
    non-dominated candidate.
    """
 
    try:
        pareto_result = (
            optimize_candidates_by_pareto_front(
                candidates,
                objectives=configuration.objectives,
                objective_tolerance=(
                    configuration.objective_tolerance
                ),
            )
        )
 
    except ParetoOptimizationPipelineError as exc:
        raise CandidateSelectionError(
            "Pareto candidate selection could not be "
            "completed."
        ) from exc
 
    selected_candidates = tuple(
        analysis.candidate
        for analysis
        in pareto_result.pareto_candidates
    )
 
    return CandidateSelectionResult(
        configuration=configuration,
        selected_candidates=selected_candidates,
        pareto_result=pareto_result,
    )