"""
Focused checks for the deterministic GeometryAnalyzer.
"""
 
from dataclasses import replace
 
from core.pareto_optimization_pipeline import (
    optimize_candidates_by_pareto_front,
)
from intelligence.analyzers.geometry_analyzer import (
    GeometryAnalyzer,
)
from intelligence.context_builder import (
    EngineeringContextBuilder,
)
from intelligence.insight_engine import (
    EngineeringInsightEngine,
)
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_severity import (
    EngineeringSeverity,
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
 
 
def evidence_values(
    insight,
) -> dict[
    str,
    object,
]:
    """
    Return evidence values indexed by evidence key.
    """
 
    return {
        evidence.key: evidence.value
        for evidence in insight.evidence
    }
 
 
base_candidate = DesignCandidate(
    base_thickness=3.0,
    fin_thickness=1.0,
    fin_height=25.0,
    fin_spacing=3.0,
    fin_count=12,
    total_height=28.0,
    gross_frontal_area=0.0014,
    open_flow_area=0.0010,
    blockage_ratio=0.2857,
    approach_velocity=3.0,
    channel_velocity=4.2,
    reynolds_number=2500.0,
    nusselt_number=8.5,
    heat_transfer_coefficient=45.0,
    friction_factor=0.04,
    pressure_drop=18.0,
    pumping_power=0.0756,
    thermal_resistance=0.42,
    estimated_base_temperature=99.3,
)
 
requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
)
 
# --------------------------------------------------
# Single selected design
# --------------------------------------------------
 
legacy_configuration = (
    OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE
        )
    )
)
 
legacy_selection_result = (
    CandidateSelectionResult(
        configuration=legacy_configuration,
        selected_candidates=(
            base_candidate,
        ),
    )
)
 
legacy_optimization_result = (
    OptimizationResult(
        best_result=None,
        candidates=[base_candidate],
        feasible_candidate_count=1,
        rejected_candidate_count=2,
        selected_material="Al6063",
        selected_process="extrusion",
        selection_result=(
            legacy_selection_result
        ),
    )
)
 
single_context = (
    EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=(
            legacy_optimization_result
        ),
    )
)
 
single_insights = GeometryAnalyzer().analyze(
    single_context
)
 
assert len(single_insights) == 1
 
single_insight = single_insights[0]
 
assert (
    single_insight.insight_id
    == "geometry.selected_design_dimensions"
)
 
assert (
    single_insight.category
    == EngineeringCategory.GEOMETRY
)
 
assert (
    single_insight.severity
    == EngineeringSeverity.INFO
)
 
single_values = evidence_values(
    single_insight
)
 
assert (
    single_values["base_thickness"]
    == 3.0
)
 
assert (
    single_values["fin_thickness"]
    == 1.0
)
 
assert (
    single_values["fin_height"]
    == 25.0
)
 
assert (
    single_values["fin_spacing"]
    == 3.0
)
 
assert (
    single_values["fin_count"]
    == 12
)
 
assert (
    single_values["total_height"]
    == 28.0
)
 
assert (
    single_values["gross_frontal_area"]
    == 0.0014
)
 
assert (
    single_values["open_flow_area"]
    == 0.0010
)
 
# --------------------------------------------------
# Pareto trade-off set
# --------------------------------------------------
 
second_candidate = replace(
    base_candidate,
    base_thickness=4.0,
    fin_thickness=1.2,
    fin_height=20.0,
    fin_spacing=4.0,
    fin_count=10,
    total_height=24.0,
    gross_frontal_area=0.0015,
    open_flow_area=0.0012,
    blockage_ratio=0.20,
    channel_velocity=3.5,
    reynolds_number=2100.0,
    pressure_drop=9.0,
    pumping_power=0.035,
    thermal_resistance=0.58,
    estimated_base_temperature=107.0,
    heat_transfer_coefficient=38.0,
)
 
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
        (
            base_candidate,
            second_candidate,
        )
    )
)
 
pareto_candidates = tuple(
    analysis.candidate
    for analysis
    in pareto_optimization.pareto_candidates
)
 
assert len(pareto_candidates) == 2
 
pareto_selection_result = (
    CandidateSelectionResult(
        configuration=pareto_configuration,
        selected_candidates=pareto_candidates,
        pareto_result=pareto_optimization,
    )
)
 
pareto_optimization_result = (
    OptimizationResult(
        best_result=None,
        candidates=[
            base_candidate,
            second_candidate,
        ],
        feasible_candidate_count=2,
        rejected_candidate_count=0,
        selected_material="Al6063",
        selected_process="extrusion",
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
 
tradeoff_insights = (
    GeometryAnalyzer().analyze(
        pareto_context
    )
)
 
assert len(tradeoff_insights) == 1
 
tradeoff_insight = tradeoff_insights[0]
 
assert (
    tradeoff_insight.insight_id
    == "geometry.tradeoff_set_dimensions"
)
 
tradeoff_values = evidence_values(
    tradeoff_insight
)
 
assert (
    tradeoff_values[
        "selected_candidate_count"
    ]
    == 2
)
 
assert (
    tradeoff_values[
        "minimum_base_thickness"
    ]
    == 3.0
)
 
assert (
    tradeoff_values[
        "maximum_base_thickness"
    ]
    == 4.0
)
 
assert (
    tradeoff_values[
        "minimum_fin_thickness"
    ]
    == 1.0
)
 
assert (
    tradeoff_values[
        "maximum_fin_thickness"
    ]
    == 1.2
)
 
assert (
    tradeoff_values[
        "minimum_fin_height"
    ]
    == 20.0
)
 
assert (
    tradeoff_values[
        "maximum_fin_height"
    ]
    == 25.0
)
 
assert (
    tradeoff_values[
        "minimum_fin_spacing"
    ]
    == 3.0
)
 
assert (
    tradeoff_values[
        "maximum_fin_spacing"
    ]
    == 4.0
)
 
assert (
    tradeoff_values[
        "minimum_fin_count"
    ]
    == 10
)
 
assert (
    tradeoff_values[
        "maximum_fin_count"
    ]
    == 12
)
 
assert (
    tradeoff_values[
        "minimum_total_height"
    ]
    == 24.0
)
 
assert (
    tradeoff_values[
        "maximum_total_height"
    ]
    == 28.0
)
 
assert (
    tradeoff_values[
        "minimum_gross_frontal_area"
    ]
    == 0.0014
)
 
assert (
    tradeoff_values[
        "maximum_gross_frontal_area"
    ]
    == 0.0015
)
 
assert (
    tradeoff_values[
        "minimum_open_flow_area"
    ]
    == 0.0010
)
 
assert (
    tradeoff_values[
        "maximum_open_flow_area"
    ]
    == 0.0012
)
 
# --------------------------------------------------
# Integrated analyzer pipeline
# --------------------------------------------------
 
pipeline_insight_ids = tuple(
    insight.insight_id
    for insight
    in EngineeringInsightEngine.generate(
        single_context
    )
)
 
assert (
    "geometry.selected_design_dimensions"
    in pipeline_insight_ids
)
 
try:
    GeometryAnalyzer().analyze(
        "invalid context"
    )
 
except ValueError as error:
    assert (
        "'context' must be an "
        "EngineeringContext object"
        in str(error)
    )
 
else:
    raise AssertionError(
        "Expected ValueError was not raised."
    )
 
print(
    "ALL GEOMETRY ANALYZER CHECKS PASSED"
)