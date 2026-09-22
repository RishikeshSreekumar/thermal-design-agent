"""
Focused checks for the deterministic airflow-performance
evaluator.
"""
 
from intelligence.context_builder import (
    EngineeringContextBuilder,
)
from intelligence.evaluators.airflow_performance_evaluator import (
    AirflowPerformanceEvaluator,
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
    Constraints,
    EngineeringRequirements,
    Requirements,
)
 
 
def create_candidate(
    *,
    pressure_drop: float,
    pumping_power: float,
) -> DesignCandidate:
    """
    Create one deterministic selected candidate.
    """
 
    return DesignCandidate(
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
        pressure_drop=pressure_drop,
        pumping_power=pumping_power,
        thermal_resistance=0.42,
        estimated_base_temperature=99.3,
    )
 
 
def create_context(
    candidate: DesignCandidate,
    *,
    maximum_pressure_drop,
    maximum_pumping_power,
):
    """
    Build a valid single-selected-candidate context.
    """
 
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
        rejected_candidate_count=0,
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
            maximum_pressure_drop=(
                maximum_pressure_drop
            ),
            maximum_pumping_power=(
                maximum_pumping_power
            ),
            air_velocity=5.0,
        ),
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=30.0,
        ),
    )
 
    return EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=optimization_result,
    )
 
 
def evidence_value(
    assessment,
    key: str,
):
    """
    Return one assessment evidence value.
    """
 
    for evidence_item in assessment.evidence:
        if evidence_item.key == key:
            return evidence_item.value
 
    raise AssertionError(
        f"Evidence key '{key}' was not found."
    )
 
 
evaluator = AirflowPerformanceEvaluator()
 
 
# --------------------------------------------------
# Both limits pass
# --------------------------------------------------
 
passing_context = create_context(
    create_candidate(
        pressure_drop=70.0,
        pumping_power=0.18,
    ),
    maximum_pressure_drop=80.0,
    maximum_pumping_power=0.25,
)
 
passing_assessments = evaluator.evaluate(
    context=passing_context,
    insights=(),
)
 
assert isinstance(
    passing_assessments,
    tuple,
)
 
assert len(
    passing_assessments
) == 2
 
pressure_assessment = passing_assessments[0]
power_assessment = passing_assessments[1]
 
assert (
    pressure_assessment.assessment_id
    == (
        "airflow.pressure_drop."
        "selected_candidate_1"
    )
)
 
assert (
    pressure_assessment.rule_id
    == "airflow.maximum_pressure_drop"
)
 
assert (
    pressure_assessment.category
    == EngineeringCategory.AIRFLOW
)
 
assert (
    pressure_assessment.severity
    == EngineeringSeverity.SUCCESS
)
 
assert pressure_assessment.passed
 
assert (
    pressure_assessment.source_insight_ids
    == (
        "airflow."
        "selected_design_performance",
    )
)
 
assert (
    evidence_value(
        pressure_assessment,
        "pressure_drop",
    )
    == 70.0
)
 
assert (
    evidence_value(
        pressure_assessment,
        "maximum_pressure_drop",
    )
    == 80.0
)
 
assert (
    evidence_value(
        pressure_assessment,
        "pressure_drop_margin",
    )
    == 10.0
)
 
assert (
    power_assessment.assessment_id
    == (
        "airflow.pumping_power."
        "selected_candidate_1"
    )
)
 
assert (
    power_assessment.rule_id
    == "airflow.maximum_pumping_power"
)
 
assert (
    power_assessment.severity
    == EngineeringSeverity.SUCCESS
)
 
assert power_assessment.passed
 
assert abs(
    evidence_value(
        power_assessment,
        "pumping_power_margin",
    )
    - 0.07
) < 1e-12
 
 
# --------------------------------------------------
# Exact limits pass
# --------------------------------------------------
 
exact_context = create_context(
    create_candidate(
        pressure_drop=80.0,
        pumping_power=0.25,
    ),
    maximum_pressure_drop=80.0,
    maximum_pumping_power=0.25,
)
 
exact_assessments = evaluator.evaluate(
    context=exact_context,
    insights=(),
)
 
assert exact_assessments[0].passed
assert exact_assessments[1].passed
 
assert (
    evidence_value(
        exact_assessments[0],
        "pressure_drop_margin",
    )
    == 0.0
)
 
assert (
    evidence_value(
        exact_assessments[1],
        "pumping_power_margin",
    )
    == 0.0
)
 
 
# --------------------------------------------------
# Both limits exceeded
# --------------------------------------------------
 
failing_context = create_context(
    create_candidate(
        pressure_drop=95.0,
        pumping_power=0.30,
    ),
    maximum_pressure_drop=80.0,
    maximum_pumping_power=0.25,
)
 
failing_assessments = evaluator.evaluate(
    context=failing_context,
    insights=(),
)
 
assert not failing_assessments[0].passed
assert not failing_assessments[1].passed
 
assert (
    failing_assessments[0].severity
    == EngineeringSeverity.CRITICAL
)
 
assert (
    failing_assessments[1].severity
    == EngineeringSeverity.CRITICAL
)
 
assert (
    evidence_value(
        failing_assessments[0],
        "pressure_drop_margin",
    )
    == -15.0
)
 
assert abs(
    evidence_value(
        failing_assessments[1],
        "pumping_power_margin",
    )
    - (-0.05)
) < 1e-12
 
 
# --------------------------------------------------
# Missing explicit limits
# --------------------------------------------------
 
missing_context = create_context(
    create_candidate(
        pressure_drop=70.0,
        pumping_power=0.18,
    ),
    maximum_pressure_drop=None,
    maximum_pumping_power=None,
)
 
missing_assessments = evaluator.evaluate(
    context=missing_context,
    insights=(),
)
 
assert len(
    missing_assessments
) == 2
 
assert not missing_assessments[0].passed
assert not missing_assessments[1].passed
 
assert (
    missing_assessments[0].severity
    == EngineeringSeverity.INFO
)
 
assert (
    missing_assessments[1].severity
    == EngineeringSeverity.INFO
)
 
assert not any(
    item.key == "pressure_drop_margin"
    for item in missing_assessments[0].evidence
)
 
assert not any(
    item.key == "pumping_power_margin"
    for item in missing_assessments[1].evidence
)
 
 
# --------------------------------------------------
# Independent rule outcomes
# --------------------------------------------------
 
mixed_context = create_context(
    create_candidate(
        pressure_drop=70.0,
        pumping_power=0.30,
    ),
    maximum_pressure_drop=80.0,
    maximum_pumping_power=0.25,
)
 
mixed_assessments = evaluator.evaluate(
    context=mixed_context,
    insights=(),
)
 
assert mixed_assessments[0].passed
assert not mixed_assessments[1].passed
 
assert (
    mixed_assessments[0].severity
    == EngineeringSeverity.SUCCESS
)
 
assert (
    mixed_assessments[1].severity
    == EngineeringSeverity.CRITICAL
)
 
 
print(
    "ALL AIRFLOW PERFORMANCE EVALUATOR "
    "CHECKS PASSED"
)