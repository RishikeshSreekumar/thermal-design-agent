"""
Focused checks for the deterministic thermal-margin
evaluator.
"""
 
from intelligence.context_builder import (
    EngineeringContextBuilder,
)
from intelligence.evaluators.thermal_margin_evaluator import (
    ThermalMarginEvaluator,
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
from core.pareto_optimization_pipeline import (
    optimize_candidates_by_pareto_front,
)
 
 
# --------------------------------------------------
# Test helpers
# --------------------------------------------------
 
def create_candidate(
    *,
    estimated_base_temperature: float,
    thermal_resistance: float = 0.42,
    pressure_drop: float = 18.0,
    pumping_power: float = 0.0756,
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
        thermal_resistance=thermal_resistance,
        estimated_base_temperature=(
            estimated_base_temperature
        ),
    )
 
 
def create_context(
    candidate: DesignCandidate,
    *,
    maximum_base_temperature,
):
    """
    Build a valid context containing one selected design.
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
 
    engineering_requirements = (
        EngineeringRequirements(
            component_type="heat_sink",
            convection_mode="forced",
            requirements=Requirements(
                heat_load=165.0,
                ambient_temperature=30.0,
                maximum_base_temperature=(
                    maximum_base_temperature
                ),
                air_velocity=5.0,
            ),
            constraints=Constraints(
                base_length=50.0,
                base_width=50.0,
                max_height=30.0,
            ),
        )
    )
 
    return EngineeringContextBuilder.build(
        requirements=engineering_requirements,
        optimization_result=optimization_result,
    )
 
 
def evidence_value(
    assessment,
    key: str,
):
    """
    Return the value of one evidence item.
    """
 
    for evidence_item in assessment.evidence:
        if evidence_item.key == key:
            return evidence_item.value
 
    raise AssertionError(
        f"Evidence key '{key}' was not found."
    )
 
 
# --------------------------------------------------
# Evaluator configuration
# --------------------------------------------------
 
evaluator = ThermalMarginEvaluator(
    warning_margin_temperature=10.0,
)
 
assert (
    evaluator.warning_margin_temperature
    == 10.0
)
 
 
# --------------------------------------------------
# Comfortable passing margin
# --------------------------------------------------
 
success_context = create_context(
    create_candidate(
        estimated_base_temperature=85.0,
    ),
    maximum_base_temperature=100.0,
)
 
success_assessments = evaluator.evaluate(
    context=success_context,
    insights=(),
)
 
assert isinstance(
    success_assessments,
    tuple,
)
 
assert len(
    success_assessments
) == 1
 
success_assessment = (
    success_assessments[0]
)
 
assert (
    success_assessment.assessment_id
    == "thermal.selected_candidate_1"
)
 
assert (
    success_assessment.rule_id
    == (
        "thermal."
        "maximum_base_temperature_margin"
    )
)
 
assert (
    success_assessment.category
    == EngineeringCategory.THERMAL
)
 
assert (
    success_assessment.severity
    == EngineeringSeverity.SUCCESS
)
 
assert success_assessment.passed
 
assert (
    success_assessment.source_insight_ids
    == (
        "thermal."
        "selected_design_performance",
    )
)
 
assert (
    evidence_value(
        success_assessment,
        "estimated_base_temperature",
    )
    == 85.0
)
 
assert (
    evidence_value(
        success_assessment,
        "maximum_base_temperature",
    )
    == 100.0
)
 
assert (
    evidence_value(
        success_assessment,
        "temperature_margin",
    )
    == 15.0
)
 
assert (
    evidence_value(
        success_assessment,
        "thermal_resistance",
    )
    == 0.42
)
 
assert (
    evidence_value(
        success_assessment,
        "heat_load",
    )
    == 165.0
)
 
 
# --------------------------------------------------
# Warning at configured threshold
# --------------------------------------------------
 
warning_context = create_context(
    create_candidate(
        estimated_base_temperature=90.0,
    ),
    maximum_base_temperature=100.0,
)
 
warning_assessment = evaluator.evaluate(
    context=warning_context,
    insights=(),
)[0]
 
assert warning_assessment.passed
 
assert (
    warning_assessment.severity
    == EngineeringSeverity.WARNING
)
 
assert (
    evidence_value(
        warning_assessment,
        "temperature_margin",
    )
    == 10.0
)
 
 
# --------------------------------------------------
# Warning below configured threshold
# --------------------------------------------------
 
limited_margin_context = create_context(
    create_candidate(
        estimated_base_temperature=96.0,
    ),
    maximum_base_temperature=100.0,
)
 
limited_margin_assessment = evaluator.evaluate(
    context=limited_margin_context,
    insights=(),
)[0]
 
assert limited_margin_assessment.passed
 
assert (
    limited_margin_assessment.severity
    == EngineeringSeverity.WARNING
)
 
assert (
    evidence_value(
        limited_margin_assessment,
        "temperature_margin",
    )
    == 4.0
)
 
 
# --------------------------------------------------
# Exact allowable temperature
# --------------------------------------------------
 
zero_margin_context = create_context(
    create_candidate(
        estimated_base_temperature=100.0,
    ),
    maximum_base_temperature=100.0,
)
 
zero_margin_assessment = evaluator.evaluate(
    context=zero_margin_context,
    insights=(),
)[0]
 
assert zero_margin_assessment.passed
 
assert (
    zero_margin_assessment.severity
    == EngineeringSeverity.WARNING
)
 
assert (
    evidence_value(
        zero_margin_assessment,
        "temperature_margin",
    )
    == 0.0
)
 
 
# --------------------------------------------------
# Exceeded allowable temperature
# --------------------------------------------------
 
critical_context = create_context(
    create_candidate(
        estimated_base_temperature=106.0,
    ),
    maximum_base_temperature=100.0,
)
 
critical_assessment = evaluator.evaluate(
    context=critical_context,
    insights=(),
)[0]
 
assert not critical_assessment.passed
 
assert (
    critical_assessment.severity
    == EngineeringSeverity.CRITICAL
)
 
assert (
    evidence_value(
        critical_assessment,
        "temperature_margin",
    )
    == -6.0
)
 
 
# --------------------------------------------------
# Missing allowable temperature
# --------------------------------------------------
 
missing_limit_context = create_context(
    create_candidate(
        estimated_base_temperature=85.0,
    ),
    maximum_base_temperature=None,
)
 
missing_limit_assessment = evaluator.evaluate(
    context=missing_limit_context,
    insights=(),
)[0]
 
assert not missing_limit_assessment.passed
 
assert (
    missing_limit_assessment.severity
    == EngineeringSeverity.INFO
)
 
assert (
    "maximum allowable base temperature"
    in missing_limit_assessment.summary
)
 
assert not any(
    evidence_item.key
    == "temperature_margin"
    for evidence_item
    in missing_limit_assessment.evidence
)
 
 
# --------------------------------------------------
# Multiple Pareto-selected candidates
# --------------------------------------------------
 
candidate_one = create_candidate(
    estimated_base_temperature=85.0,
    thermal_resistance=0.35,
    pressure_drop=24.0,
    pumping_power=0.10,
)
 
candidate_two = create_candidate(
    estimated_base_temperature=105.0,
    thermal_resistance=0.50,
    pressure_drop=10.0,
    pumping_power=0.04,
)
 
pareto_optimization_result = (
    optimize_candidates_by_pareto_front(
        (
            candidate_one,
            candidate_two,
        )
    )
)
 
pareto_selected_candidates = tuple(
    analysis.candidate
    for analysis
    in (
        pareto_optimization_result
        .pareto_candidates
    )
)
 
assert (
    pareto_selected_candidates
    == (
        candidate_one,
        candidate_two,
    )
)
 
selection_configuration = (
    OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .PARETO_FRONT
        )
    )
)
 
selection_result = CandidateSelectionResult(
    configuration=selection_configuration,
    selected_candidates=(
        pareto_selected_candidates
    ),
    pareto_result=(
        pareto_optimization_result
    ),
)
 
multiple_optimization_result = OptimizationResult(
    best_result=None,
    candidates=[
        candidate_one,
        candidate_two,
    ],
    feasible_candidate_count=2,
    rejected_candidate_count=0,
    selected_material="Al6063",
    selected_process="extrusion",
    selection_result=selection_result,
)
 
multiple_requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
    requirements=Requirements(
        heat_load=165.0,
        ambient_temperature=30.0,
        maximum_base_temperature=100.0,
        air_velocity=5.0,
    ),
    constraints=Constraints(
        base_length=50.0,
        base_width=50.0,
        max_height=30.0,
    ),
)
 
multiple_context = (
    EngineeringContextBuilder.build(
        requirements=multiple_requirements,
        optimization_result=(
            multiple_optimization_result
        ),
    )
)
 
multiple_assessments = evaluator.evaluate(
    context=multiple_context,
    insights=(),
)
 
assert len(
    multiple_assessments
) == 2
 
assert tuple(
    assessment.assessment_id
    for assessment in multiple_assessments
) == (
    "thermal.selected_candidate_1",
    "thermal.selected_candidate_2",
)
 
assert (
    multiple_assessments[0].severity
    == EngineeringSeverity.SUCCESS
)
 
assert (
    multiple_assessments[1].severity
    == EngineeringSeverity.CRITICAL
)
 
# --------------------------------------------------
# Invalid evaluate inputs
# --------------------------------------------------
 
try:
    evaluator.evaluate(
        context=None,
        insights=(),
    )
 
except ValueError as exc:
    assert (
        "'context' must be an "
        "EngineeringContext object"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An invalid engineering context was accepted."
    )
 
 
try:
    evaluator.evaluate(
        context=success_context,
        insights=[],
    )
 
except ValueError as exc:
    assert (
        "'insights' must be a tuple"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An insight list was accepted."
    )
 
 
print(
    "ALL THERMAL MARGIN EVALUATOR "
    "CHECKS PASSED"
)