"""
Focused checks for the manufacturability assessment
adapter.
"""
 
from intelligence.context_builder import (
    EngineeringContextBuilder,
)
from intelligence.evaluators.manufacturability_evaluator import (
    ManufacturabilityEvaluator,
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
)
 
 
# --------------------------------------------------
# Test helpers
# --------------------------------------------------
 
def create_candidate(
    *,
    fin_thickness: float = 1.0,
    fin_spacing: float = 3.0,
    fin_height: float = 8.0,
    base_thickness: float = 3.0,
) -> DesignCandidate:
    """
    Create one deterministic candidate.
    """
 
    return DesignCandidate(
        base_thickness=base_thickness,
        fin_thickness=fin_thickness,
        fin_height=fin_height,
        fin_spacing=fin_spacing,
        fin_count=12,
        total_height=(
            base_thickness
            + fin_height
        ),
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
 
 
def create_context(
    candidate: DesignCandidate,
    *,
    maximum_height: float = 30.0,
):
    """
    Build a valid engineering context containing one
    selected candidate.
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
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=maximum_height,
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
    Return one evidence value by key.
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
 
evaluator = ManufacturabilityEvaluator(
    capability=AL6063_EXTRUSION,
)
 
assert (
    evaluator.capability
    is AL6063_EXTRUSION
)
 
 
# --------------------------------------------------
# Feasible candidate with supplier warning
# --------------------------------------------------
 
feasible_candidate = create_candidate()
 
feasible_context = create_context(
    feasible_candidate
)
 
feasible_assessments = evaluator.evaluate(
    context=feasible_context,
    insights=(),
)
 
assert isinstance(
    feasible_assessments,
    tuple,
)
 
assert len(
    feasible_assessments
) == 1
 
feasible_assessment = (
    feasible_assessments[0]
)
 
assert (
    feasible_assessment.assessment_id
    == "manufacturing.selected_candidate_1"
)
 
assert (
    feasible_assessment.rule_id
    == (
        "manufacturing."
        "configured_process_capability"
    )
)
 
assert (
    feasible_assessment.category
    == EngineeringCategory.MANUFACTURING
)
 
assert (
    feasible_assessment.severity
    == EngineeringSeverity.WARNING
)
 
assert feasible_assessment.passed
 
assert feasible_assessment.has_evidence
 
assert (
    feasible_assessment.source_insight_ids
    == (
        "manufacturing.process_recorded",
        "geometry.selected_design_dimensions",
    )
)
 
assert (
    evidence_value(
        feasible_assessment,
        "is_feasible",
    )
    is True
)
 
assert (
    evidence_value(
        feasible_assessment,
        "manufacturing_status",
    )
    == "Feasible with review"
)
 
assert (
    evidence_value(
        feasible_assessment,
        "violation_count",
    )
    == 0
)
 
assert (
    evidence_value(
        feasible_assessment,
        "warning_count",
    )
    == 1
)
 
assert (
    evidence_value(
        feasible_assessment,
        "checked_rule_count",
    )
    == 7
)
 
 
# --------------------------------------------------
# Non-manufacturable candidate
# --------------------------------------------------
 
invalid_candidate = create_candidate(
    fin_thickness=0.5,
)
 
invalid_context = create_context(
    invalid_candidate
)
 
invalid_assessments = evaluator.evaluate(
    context=invalid_context,
    insights=(),
)
 
assert len(
    invalid_assessments
) == 1
 
invalid_assessment = (
    invalid_assessments[0]
)
 
assert not invalid_assessment.passed
 
assert (
    invalid_assessment.severity
    == EngineeringSeverity.CRITICAL
)
 
assert (
    evidence_value(
        invalid_assessment,
        "is_feasible",
    )
    is False
)
 
assert (
    evidence_value(
        invalid_assessment,
        "manufacturing_status",
    )
    == "Rejected"
)
 
assert (
    evidence_value(
        invalid_assessment,
        "violation_count",
    )
    >= 1
)
 
assert any(
    evidence_item.key.startswith(
        "violation_"
    )
    for evidence_item
    in invalid_assessment.evidence
)
 
 
# --------------------------------------------------
# Height constraint violation
# --------------------------------------------------
 
height_candidate = create_candidate(
    fin_height=28.0,
)
 
height_context = create_context(
    height_candidate,
    maximum_height=30.0,
)
 
height_assessment = evaluator.evaluate(
    context=height_context,
    insights=(),
)[0]
 
assert not height_assessment.passed
 
assert (
    evidence_value(
        height_assessment,
        "violation_count",
    )
    >= 1
)
 
assert any(
    (
        evidence_item.key.startswith(
            "violation_"
        )
        and (
            "maximum permitted height"
            in str(evidence_item.value)
        )
    )
    for evidence_item
    in height_assessment.evidence
)
 
 
# --------------------------------------------------
# Invalid evaluator configuration
# --------------------------------------------------
 
try:
    ManufacturabilityEvaluator(
        capability=None,
    )
 
except ValueError as exc:
    assert (
        "'capability' must be a "
        "ProcessCapability object"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An invalid process capability was accepted."
    )
 
 
# --------------------------------------------------
# Missing engineering constraints
# --------------------------------------------------
 
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
        feasible_candidate,
    ),
)
 
optimization_result = OptimizationResult(
    best_result=None,
    candidates=[
        feasible_candidate,
    ],
    feasible_candidate_count=1,
    rejected_candidate_count=0,
    selected_material="Al6063",
    selected_process="extrusion",
    selection_result=selection_result,
)
 
missing_constraints_context = (
    EngineeringContextBuilder.build(
        requirements=EngineeringRequirements(
            component_type="heat_sink",
            convection_mode="forced",
        ),
        optimization_result=optimization_result,
    )
)
 
try:
    evaluator.evaluate(
        context=missing_constraints_context,
        insights=(),
    )
 
except ValueError as exc:
    assert (
        "requires engineering constraints"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "A context without constraints was accepted."
    )
 
 
# --------------------------------------------------
# Missing maximum height
# --------------------------------------------------
 
missing_height_context = (
    EngineeringContextBuilder.build(
        requirements=EngineeringRequirements(
            component_type="heat_sink",
            convection_mode="forced",
            constraints=Constraints(
                base_length=50.0,
                base_width=50.0,
                max_height=None,
            ),
        ),
        optimization_result=optimization_result,
    )
)
 
try:
    evaluator.evaluate(
        context=missing_height_context,
        insights=(),
    )
 
except ValueError as exc:
    assert (
        "requires 'constraints.max_height'"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "A context without maximum height was accepted."
    )
 
 
print(
    "ALL MANUFACTURABILITY EVALUATOR "
    "CHECKS PASSED"
)