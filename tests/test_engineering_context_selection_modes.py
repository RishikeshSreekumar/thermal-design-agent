"""
Focused checks for optimization-selection information
exposed through EngineeringContext.
"""
 
from dataclasses import replace
 
from core.pareto_optimization_pipeline import (
    optimize_candidates_by_pareto_front,
)
from core.weighted_optimization_pipeline import (
    optimize_candidates_by_weighted_score,
)
from intelligence.context_builder import (
    EngineeringContextBuilder,
)
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.optimization_result import (
    OptimizationResult,
)
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.requirements import (
    EngineeringRequirements,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def create_base_candidate() -> DesignCandidate:
    """
    Create one valid deterministic design candidate.
    """
 
    return DesignCandidate(
        base_thickness=3.0,
        fin_thickness=0.8,
        fin_height=8.0,
        fin_spacing=1.6,
        fin_count=21,
        total_height=11.0,
        gross_frontal_area=0.0004,
        open_flow_area=0.000256,
        blockage_ratio=0.36,
        approach_velocity=5.0,
        channel_velocity=7.8125,
        reynolds_number=1295.405982905983,
        nusselt_number=7.54,
        heat_transfer_coefficient=74.36325,
        friction_factor=0.049405,
        pressure_drop=100.0,
        pumping_power=0.3,
        thermal_resistance=0.5,
        estimated_base_temperature=112.5,
    )
 
 
def create_optimization_result(
    candidates: tuple[
        DesignCandidate,
        ...,
    ],
    selection_result: CandidateSelectionResult,
) -> OptimizationResult:
    """
    Create an optimization result around an existing
    deterministic selection result.
    """
 
    return OptimizationResult(
        best_result=None,
        candidates=list(candidates),
        feasible_candidate_count=len(candidates),
        rejected_candidate_count=2,
        selected_material="Al6063",
        selected_process="extrusion",
        selection_result=selection_result,
    )
 
 
requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
)
 
thermal_focused_candidate = (
    create_base_candidate()
)
 
balanced_candidate = replace(
    thermal_focused_candidate,
    thermal_resistance=0.7,
    pressure_drop=60.0,
    pumping_power=0.2,
)
 
airflow_focused_candidate = replace(
    thermal_focused_candidate,
    thermal_resistance=0.9,
    pressure_drop=20.0,
    pumping_power=0.1,
)
 
dominated_candidate = replace(
    thermal_focused_candidate,
    thermal_resistance=0.8,
    pressure_drop=80.0,
    pumping_power=0.25,
)
 
candidates = (
    dominated_candidate,
    airflow_focused_candidate,
    balanced_candidate,
    thermal_focused_candidate,
)
 
# --------------------------------------------------
# Minimum thermal resistance
# --------------------------------------------------
 
legacy_configuration = (
    OptimizationSelectionConfiguration()
)
 
legacy_selection_result = (
    CandidateSelectionResult(
        configuration=legacy_configuration,
        selected_candidates=(
            thermal_focused_candidate,
        ),
    )
)
 
legacy_optimization_result = (
    create_optimization_result(
        candidates=candidates,
        selection_result=(
            legacy_selection_result
        ),
    )
)
 
legacy_context = (
    EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=(
            legacy_optimization_result
        ),
    )
)
 
assert (
    legacy_context.selection_result
    is legacy_selection_result
)
 
assert (
    legacy_context.selection_configuration
    is legacy_configuration
)
 
assert legacy_context.uses_legacy_selection
 
assert not legacy_context.uses_weighted_selection
 
assert not legacy_context.uses_pareto_selection
 
assert legacy_context.weighted_result is None
 
assert legacy_context.pareto_result is None
 
assert legacy_context.selected_candidate_count == 1
 
assert legacy_context.has_single_selected_design
 
assert not legacy_context.has_tradeoff_set
 
# --------------------------------------------------
# Weighted multi-objective selection
# --------------------------------------------------
 
scoring_configuration = ScoringConfiguration(
    objective_weights=(
        ObjectiveWeight(
            objective_key="thermal_resistance",
            weight=0.6,
        ),
        ObjectiveWeight(
            objective_key="pressure_drop",
            weight=0.3,
        ),
        ObjectiveWeight(
            objective_key="pumping_power",
            weight=0.1,
        ),
    )
)
 
weighted_configuration = (
    OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .WEIGHTED_SCORE
        ),
        scoring_configuration=(
            scoring_configuration
        ),
    )
)
 
weighted_optimization = (
    optimize_candidates_by_weighted_score(
        candidates,
        scoring_configuration,
    )
)
 
weighted_best_candidate = (
    weighted_optimization
    .best_candidate
    .scored_candidate
    .analysis
    .candidate
)
 
weighted_selection_result = (
    CandidateSelectionResult(
        configuration=weighted_configuration,
        selected_candidates=(
            weighted_best_candidate,
        ),
        weighted_result=weighted_optimization,
    )
)
 
weighted_optimization_result = (
    create_optimization_result(
        candidates=candidates,
        selection_result=(
            weighted_selection_result
        ),
    )
)
 
weighted_context = (
    EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=(
            weighted_optimization_result
        ),
    )
)
 
assert weighted_context.uses_weighted_selection
 
assert not weighted_context.uses_legacy_selection
 
assert not weighted_context.uses_pareto_selection
 
assert (
    weighted_context.weighted_result
    is weighted_optimization
)
 
assert weighted_context.pareto_result is None
 
assert (
    weighted_context
    .selection_configuration
    .scoring_configuration
    is scoring_configuration
)
 
assert weighted_context.selected_candidate_count == 1
 
assert weighted_context.has_single_selected_design
 
assert not weighted_context.has_tradeoff_set
 
# --------------------------------------------------
# Pareto-front selection
# --------------------------------------------------
 
pareto_configuration = (
    OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .PARETO_FRONT
        )
    )
)
 
pareto_optimization = (
    optimize_candidates_by_pareto_front(
        candidates
    )
)
 
pareto_candidates = tuple(
    analysis.candidate
    for analysis
    in pareto_optimization.pareto_candidates
)
 
pareto_selection_result = (
    CandidateSelectionResult(
        configuration=pareto_configuration,
        selected_candidates=pareto_candidates,
        pareto_result=pareto_optimization,
    )
)
 
pareto_optimization_result = (
    create_optimization_result(
        candidates=candidates,
        selection_result=(
            pareto_selection_result
        ),
    )
)
 
pareto_context = (
    EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=(
            pareto_optimization_result
        ),
    )
)
 
assert pareto_context.uses_pareto_selection
 
assert not pareto_context.uses_legacy_selection
 
assert not pareto_context.uses_weighted_selection
 
assert pareto_context.weighted_result is None
 
assert (
    pareto_context.pareto_result
    is pareto_optimization
)
 
assert (
    pareto_context.selected_candidates
    == pareto_candidates
)
 
assert (
    pareto_context.selected_candidate_count
    == len(pareto_candidates)
)
 
assert (
    pareto_context.has_tradeoff_set
    == (
        len(pareto_candidates) > 1
    )
)
 
if len(pareto_candidates) > 1:
    assert not (
        pareto_context
        .has_single_selected_design
    )
 
    assert (
        pareto_context.selected_candidate
        is None
    )
 
print(
    "ALL ENGINEERING CONTEXT SELECTION MODE "
    "CHECKS PASSED"
)