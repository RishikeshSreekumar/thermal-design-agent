"""
Focused checks for the modular engineering analyzer
pipeline.
"""
 
from intelligence.analyzers.model_limitation_analyzer import (
    ModelLimitationAnalyzer,
)
from intelligence.analyzers.optimization_analyzer import (
    OptimizationAnalyzer,
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
 
 
candidate = DesignCandidate(
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
 
selection_configuration = (
    OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE
        )
    )
)
 
selection_result = CandidateSelectionResult(
    configuration=selection_configuration,
    selected_candidates=(candidate,),
)
 
optimization_result = OptimizationResult(
    best_result=None,
    candidates=[candidate],
    feasible_candidate_count=1,
    rejected_candidate_count=3,
    selected_material="Al6063",
    selected_process="extrusion",
    selection_result=selection_result,
)
 
requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
)
 
context = EngineeringContextBuilder.build(
    requirements=requirements,
    optimization_result=optimization_result,
    known_limitations=(
        "Radiation heat transfer is not yet included.",
        "Fan accuracy depends on the supplied fan curve.",
    ),
)
 
# --------------------------------------------------
# Optimization analyzer
# --------------------------------------------------
 
optimization_analyzer = OptimizationAnalyzer()
 
optimization_insights = (
    optimization_analyzer.analyze(
        context
    )
)
 
assert isinstance(
    optimization_insights,
    tuple,
)
 
assert len(
    optimization_insights
) == 5
 
assert tuple(
    insight.insight_id
    for insight in optimization_insights
) == (
    "optimization.completed",
    "optimization.candidate_feasibility",
    "optimization.selection_strategy",
    "material.selected",
    "manufacturing.process_recorded",
)
 
# --------------------------------------------------
# Model-limitation analyzer
# --------------------------------------------------
 
limitation_analyzer = (
    ModelLimitationAnalyzer()
)
 
limitation_insights = (
    limitation_analyzer.analyze(
        context
    )
)
 
assert isinstance(
    limitation_insights,
    tuple,
)
 
assert len(
    limitation_insights
) == 2
 
assert tuple(
    insight.insight_id
    for insight in limitation_insights
) == (
    "model_limitation.1",
    "model_limitation.2",
)
 
assert all(
    insight.severity
    == EngineeringSeverity.WARNING
    for insight in limitation_insights
)
 
assert all(
    insight.category
    == EngineeringCategory.MODEL_LIMITATION
    for insight in limitation_insights
)
 
# --------------------------------------------------
# Integrated analyzer pipeline
# --------------------------------------------------
 
pipeline_insights = (
    EngineeringInsightEngine.generate(
        context
    )
)
 
assert isinstance(
    pipeline_insights,
    tuple,
)
 
assert tuple(
    insight.insight_id
    for insight in pipeline_insights
) == (
    "optimization.completed",
    "optimization.candidate_feasibility",
    "optimization.selection_strategy",
    "material.selected",
    "manufacturing.process_recorded",
    "geometry.selected_design_dimensions",
    "thermal.selected_design_performance",
    "airflow.selected_design_performance",
    "model_limitation.1",
    "model_limitation.2",
)
 
assert len(
    pipeline_insights
) == 10
 
assert len(
    {
        insight.insight_id
        for insight in pipeline_insights
    }
) == len(
    pipeline_insights
)
 
assert all(
    insight.has_evidence
    for insight in pipeline_insights
)
 
# --------------------------------------------------
# Context without limitations
# --------------------------------------------------
 
context_without_limitations = (
    EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=optimization_result,
    )
)
 
assert (
    ModelLimitationAnalyzer()
    .analyze(
        context_without_limitations
    )
    == ()
)
 
pipeline_without_limitations = (
    EngineeringInsightEngine.generate(
        context_without_limitations
    )
)
 
assert tuple(
    insight.insight_id
    for insight in pipeline_without_limitations
) == (
    "optimization.completed",
    "optimization.candidate_feasibility",
    "optimization.selection_strategy",
    "material.selected",
    "manufacturing.process_recorded",
    "geometry.selected_design_dimensions",
    "thermal.selected_design_performance",
    "airflow.selected_design_performance",
)
 
assert len(
    pipeline_without_limitations
) == 8
 
print(
    "ALL ENGINEERING ANALYZER PIPELINE CHECKS PASSED"
)