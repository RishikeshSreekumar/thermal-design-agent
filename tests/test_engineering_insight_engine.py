"""
Focused checks for EngineeringInsightEngine.
"""
 
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
 
 
def expect_value_error(
    action,
    expected_message: str,
) -> None:
    """
    Confirm that an action raises the expected validation
    error.
    """
 
    try:
        action()
 
    except ValueError as error:
        assert expected_message in str(error)
 
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
 
 
def find_insight(
    insights,
    insight_id: str,
):
    """
    Return one generated insight by its stable ID.
    """
 
    for insight in insights:
        if insight.insight_id == insight_id:
            return insight
 
    raise AssertionError(
        f"Insight not found: {insight_id}"
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
 
insights = EngineeringInsightEngine.generate(
    context
)
 
assert isinstance(
    insights,
    tuple,
)
 
assert len(insights) == 10

assert tuple(
    insight.insight_id
    for insight in insights
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
    {
        insight.insight_id
        for insight in insights
    }
) == len(insights)
 
completion_insight = find_insight(
    insights,
    "optimization.completed",
)
 
assert (
    completion_insight.severity
    == EngineeringSeverity.SUCCESS
)
 
assert (
    completion_insight.category
    == EngineeringCategory.OPTIMIZATION
)
 
assert completion_insight.has_evidence
 
feasibility_insight = find_insight(
    insights,
    "optimization.candidate_feasibility",
)
 
evidence_by_key = {
    evidence.key: evidence
    for evidence in feasibility_insight.evidence
}
 
assert (
    evidence_by_key[
        "feasible_candidate_count"
    ].value
    == 1
)
 
assert (
    evidence_by_key[
        "rejected_candidate_count"
    ].value
    == 3
)
 
assert (
    evidence_by_key[
        "feasibility_rate"
    ].value
    == 25.0
)
 
assert (
    evidence_by_key[
        "feasibility_rate"
    ].unit
    == "percent"
)
 
selection_insight = find_insight(
    insights,
    "optimization.selection_strategy",
)
 
assert (
    selection_insight.title
    == "Minimum thermal resistance selection used"
)
 
selection_evidence = {
    evidence.key: evidence.value
    for evidence in selection_insight.evidence
}
 
assert (
    selection_evidence["selection_mode"]
    == (
        OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
        .value
    )
)
 
assert (
    selection_evidence[
        "selected_candidate_count"
    ]
    == 1
)
 
assert not (
    selection_evidence[
        "contains_tradeoff_set"
    ]
)
 
material_insight = find_insight(
    insights,
    "material.selected",
)
 
assert (
    material_insight.evidence[0].value
    == "Al6063"
)
 
process_insight = find_insight(
    insights,
    "manufacturing.process_recorded",
)
 
assert (
    process_insight.evidence[0].value
    == "extrusion"
)

geometry_insight = find_insight(
    insights,
    "geometry.selected_design_dimensions",
)
 
assert (
    geometry_insight.category
    == EngineeringCategory.GEOMETRY
)
 
geometry_evidence = {
    evidence.key: evidence.value
    for evidence in geometry_insight.evidence
}
 
assert (
    geometry_evidence["base_thickness"]
    == 3.0
)
 
assert (
    geometry_evidence["fin_thickness"]
    == 1.0
)
 
assert (
    geometry_evidence["fin_height"]
    == 25.0
)
 
assert (
    geometry_evidence["fin_spacing"]
    == 3.0
)
 
assert (
    geometry_evidence["fin_count"]
    == 12
)

thermal_insight = find_insight(
    insights,
    "thermal.selected_design_performance",
)
 
assert (
    thermal_insight.category
    == EngineeringCategory.THERMAL
)
 
thermal_evidence = {
    evidence.key: evidence.value
    for evidence in thermal_insight.evidence
}
 
assert (
    thermal_evidence["thermal_resistance"]
    == 0.42
)
 
assert (
    thermal_evidence[
        "estimated_base_temperature"
    ]
    == 99.3
)
 
assert (
    thermal_evidence[
        "heat_transfer_coefficient"
    ]
    == 45.0
)

airflow_insight = find_insight(
    insights,
    "airflow.selected_design_performance",
)
 
assert (
    airflow_insight.category
    == EngineeringCategory.AIRFLOW
)
 
airflow_evidence = {
    evidence.key: evidence.value
    for evidence in airflow_insight.evidence
}
 
assert (
    airflow_evidence["approach_velocity"]
    == 3.0
)
 
assert (
    airflow_evidence["channel_velocity"]
    == 4.2
)
 
assert (
    airflow_evidence["reynolds_number"]
    == 2500.0
)
 
assert (
    airflow_evidence["pressure_drop"]
    == 18.0
)
 
assert (
    airflow_evidence["pumping_power"]
    == 0.0756
)

 
first_limitation = find_insight(
    insights,
    "model_limitation.1",
)
 
second_limitation = find_insight(
    insights,
    "model_limitation.2",
)
 
assert (
    first_limitation.severity
    == EngineeringSeverity.WARNING
)
 
assert (
    first_limitation.category
    == EngineeringCategory.MODEL_LIMITATION
)
 
assert (
    first_limitation.summary
    == "Radiation heat transfer is not yet included."
)
 
assert (
    second_limitation.summary
    == "Fan accuracy depends on the supplied fan curve."
)
 
assert all(
    insight.has_evidence
    for insight in insights
)
 
expect_value_error(
    lambda: EngineeringInsightEngine.generate(
        "invalid context"
    ),
    "'context' must be an EngineeringContext object",
)
 
print(
    "ALL ENGINEERING INSIGHT ENGINE CHECKS PASSED"
)