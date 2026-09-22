"""
Focused integration checks for the complete deterministic
engineering-intelligence pipeline.
"""
 
from dataclasses import FrozenInstanceError
 
from intelligence.engineering_assessment_engine import (
    EngineeringAssessmentEngine,
)
from intelligence.engineering_intelligence_pipeline import (
    EngineeringIntelligencePipeline,
)
from intelligence.evaluators.manufacturability_evaluator import (
    ManufacturabilityEvaluator,
)
from intelligence.evaluators.thermal_margin_evaluator import (
    ThermalMarginEvaluator,
)
from intelligence.evaluators.airflow_performance_evaluator import (
    AirflowPerformanceEvaluator,
)
from manufacturing.extrusion_capability import (
    AL6063_EXTRUSION,
)
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.optimization_result import (
    OptimizationResult,
)
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
# --------------------------------------------------
# Deterministic test fixture
# --------------------------------------------------
 
candidate = DesignCandidate(
    base_thickness=3.0,
    fin_thickness=1.0,
    fin_height=8.0,
    fin_spacing=3.0,
    fin_count=12,
    total_height=11.0,
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
    selected_candidates=(
        candidate,
    ),
)
 
optimization_result = OptimizationResult(
    best_result=None,
    candidates=[
        candidate,
    ],
    feasible_candidate_count=1,
    rejected_candidate_count=3,
    selected_material="Al6063",
    selected_process="extrusion",
    selection_result=selection_result,
)
 
requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
    requirements=Requirements(
        heat_load=165.0,
        ambient_temperature=30.0,
        maximum_base_temperature=105.0,
        maximum_pressure_drop=25.0,
        maximum_pumping_power=0.10,
        air_velocity=5.0,
    ),
    constraints=Constraints(
        base_length=50.0,
        base_width=50.0,
        max_height=30.0,
    ),
)
 
known_limitations = (
    "Radiation heat transfer is not yet included.",
    "Fan accuracy depends on the supplied fan curve.",
)
 
 
# --------------------------------------------------
# Pipeline configuration
# --------------------------------------------------
 
manufacturability_evaluator = (
    ManufacturabilityEvaluator(
        capability=AL6063_EXTRUSION,
    )
)

thermal_margin_evaluator = (
    ThermalMarginEvaluator(
        warning_margin_temperature=10.0,
    )
)

airflow_performance_evaluator = (
    AirflowPerformanceEvaluator()
)
 
assessment_engine = (
    EngineeringAssessmentEngine(
        evaluators=(
            manufacturability_evaluator,
            thermal_margin_evaluator,
            airflow_performance_evaluator,
        )
    )
)
 
pipeline = EngineeringIntelligencePipeline(
    assessment_engine=assessment_engine,
)
 
assert (
    pipeline.assessment_engine
    is assessment_engine
)
 
assert (
    assessment_engine.evaluators
    == (
        manufacturability_evaluator,
        thermal_margin_evaluator,
        airflow_performance_evaluator,
    )
) 
 
# --------------------------------------------------
# Complete pipeline run
# --------------------------------------------------
 
result = pipeline.run(
    requirements=requirements,
    optimization_result=optimization_result,
    known_limitations=known_limitations,
)
 
assert isinstance(
    result,
    EngineeringIntelligenceResult,
)
 
assert (
    result.context.requirements
    is requirements
)
 
assert (
    result.context.optimization_result
    is optimization_result
)
 
assert (
    result.context.selected_candidates
    == (
        candidate,
    )
)
 
assert (
    result.context.known_limitations
    == known_limitations
)
 
 
# --------------------------------------------------
# Insight integration
# --------------------------------------------------
 
assert result.has_insights
 
assert len(
    result.insights
) == 10
 
assert tuple(
    insight.insight_id
    for insight in result.insights
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
 
 
# --------------------------------------------------
# Assessment integration
# --------------------------------------------------
 
assert result.has_assessments
 
assert len(
    result.assessments
) == 4
 
assert tuple(
    assessment.assessment_id
    for assessment in result.assessments
) == (
    "manufacturing.selected_candidate_1",
    "thermal.selected_candidate_1",
    (
        "airflow.pressure_drop."
        "selected_candidate_1"
    ),
    (
        "airflow.pumping_power."
        "selected_candidate_1"
    ),
)
 
 
# --------------------------------------------------
# Manufacturing assessment
# --------------------------------------------------
 
manufacturing_assessment = (
    result.assessments[0]
)
 
assert (
    manufacturing_assessment.assessment_id
    == "manufacturing.selected_candidate_1"
)
 
assert (
    manufacturing_assessment.source_insight_ids
    == (
        "manufacturing.process_recorded",
        "geometry.selected_design_dimensions",
    )
)
 
assert manufacturing_assessment.passed
 
 
# --------------------------------------------------
# Thermal assessment
# --------------------------------------------------
 
thermal_assessment = (
    result.assessments[1]
)
 
assert (
    thermal_assessment.assessment_id
    == "thermal.selected_candidate_1"
)
 
assert (
    thermal_assessment.rule_id
    == (
        "thermal."
        "maximum_base_temperature_margin"
    )
)
 
assert (
    thermal_assessment.source_insight_ids
    == (
        "thermal."
        "selected_design_performance",
    )
)
 
assert thermal_assessment.passed
 
assert (
    thermal_assessment.severity
    == EngineeringSeverity.WARNING
)
 
 
def evidence_value(
    assessment,
    key: str,
):
    """
    Return one assessment evidence value by key.
    """
 
    for evidence_item in assessment.evidence:
        if evidence_item.key == key:
            return evidence_item.value
 
    raise AssertionError(
        f"Evidence key '{key}' was not found."
    )
 
 
assert (
    evidence_value(
        thermal_assessment,
        "estimated_base_temperature",
    )
    == 99.3
)
 
assert (
    evidence_value(
        thermal_assessment,
        "maximum_base_temperature",
    )
    == 105.0
)
 
assert abs(
    evidence_value(
        thermal_assessment,
        "temperature_margin",
    )
    - 5.7
) < 1e-12

# --------------------------------------------------
# Pressure drop assessment
# --------------------------------------------------

pressure_drop_assessment = (
    result.assessments[2]
)

assert (
    pressure_drop_assessment.rule_id
    == "airflow.maximum_pressure_drop"
)
 
assert (
    pressure_drop_assessment.source_insight_ids
    == (
        "airflow."
        "selected_design_performance",
    )
)
 
assert pressure_drop_assessment.passed
 
assert (
    pressure_drop_assessment.severity
    == EngineeringSeverity.SUCCESS
)
 
assert (
    evidence_value(
        pressure_drop_assessment,
        "pressure_drop",
    )
    == 18.0
)
 
assert (
    evidence_value(
        pressure_drop_assessment,
        "maximum_pressure_drop",
    )
    == 25.0
)
 
assert (
    evidence_value(
        pressure_drop_assessment,
        "pressure_drop_margin",
    )
    == 7.0
)

# --------------------------------------------------
# Pumping power assessment
# --------------------------------------------------
 
pumping_power_assessment = (
    result.assessments[3]
)
 
assert (
    pumping_power_assessment.rule_id
    == "airflow.maximum_pumping_power"
)
 
assert (
    pumping_power_assessment.source_insight_ids
    == (
        "airflow."
        "selected_design_performance",
    )
)
 
assert pumping_power_assessment.passed
 
assert (
    pumping_power_assessment.severity
    == EngineeringSeverity.SUCCESS
)
 
assert (
    evidence_value(
        pumping_power_assessment,
        "pumping_power",
    )
    == 0.0756
)
 
assert (
    evidence_value(
        pumping_power_assessment,
        "maximum_pumping_power",
    )
    == 0.10
)
 
assert abs(
    evidence_value(
        pumping_power_assessment,
        "pumping_power_margin",
    )
    - 0.0244
) < 1e-12 
 
# --------------------------------------------------
# Aggregate assessment classification
# --------------------------------------------------
 
assert len(
    result.passed_assessments
) == 4
 
assert (
    result.passed_assessments
    == result.assessments
)
 
assert (
    result.failed_assessments
    == ()
)
 
# --------------------------------------------------
# Empty assessment-engine configuration
# --------------------------------------------------
 
empty_pipeline = (
    EngineeringIntelligencePipeline(
        assessment_engine=(
            EngineeringAssessmentEngine()
        )
    )
)
 
empty_result = empty_pipeline.run(
    requirements=requirements,
    optimization_result=optimization_result,
    known_limitations=known_limitations,
)
 
assert empty_result.has_insights
 
assert not empty_result.has_assessments
 
assert (
    empty_result.assessments
    == ()
)
 
assert (
    empty_result.passed_assessments
    == ()
)
 
assert (
    empty_result.failed_assessments
    == ()
)
 
 
# --------------------------------------------------
# Aggregate immutability
# --------------------------------------------------
 
try:
    result.insights = ()
 
except FrozenInstanceError:
    pass
 
else:
    raise AssertionError(
        "EngineeringIntelligenceResult must remain "
        "immutable."
    )
 
 
# --------------------------------------------------
# Invalid pipeline configuration
# --------------------------------------------------
 
try:
    EngineeringIntelligencePipeline(
        assessment_engine=None,
    )
 
except ValueError as exc:
    assert (
        "'assessment_engine' must be an "
        "EngineeringAssessmentEngine object"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An invalid assessment engine was accepted."
    )
 
 
# --------------------------------------------------
# Invalid pipeline inputs
# --------------------------------------------------
 
try:
    pipeline.run(
        requirements=None,
        optimization_result=optimization_result,
    )
 
except ValueError as exc:
    assert (
        "'requirements' must be an "
        "EngineeringRequirements object"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "Invalid engineering requirements were accepted."
    )
 
 
try:
    pipeline.run(
        requirements=requirements,
        optimization_result=None,
    )
 
except ValueError as exc:
    assert (
        "'optimization_result' must be an "
        "OptimizationResult object"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An invalid optimization result was accepted."
    )
 
 
try:
    pipeline.run(
        requirements=requirements,
        optimization_result=optimization_result,
        known_limitations=[],
    )
 
except ValueError as exc:
    assert (
        "'known_limitations' must be a tuple"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "A limitation list was accepted."
    )
 
 
try:
    pipeline.run(
        requirements=requirements,
        optimization_result=optimization_result,
        known_limitations=(
            "Valid limitation",
            42,
        ),
    )
 
except ValueError as exc:
    assert (
        "Every known limitation must be a string"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "A non-string known limitation was accepted."
    )
 
 
print(
    "ALL ENGINEERING INTELLIGENCE PIPELINE "
    "CHECKS PASSED"
)