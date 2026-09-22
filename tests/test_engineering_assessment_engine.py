"""
Focused regression checks for
EngineeringAssessmentEngine.
"""
 
from intelligence.engineering_assessment_engine import (
    EngineeringAssessmentEngine,
)
from intelligence.evaluators.base_evaluator import (
    EngineeringEvaluator,
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
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_evidence import (
    EngineeringEvidence,
)
from models.engineering_insight import (
    EngineeringInsight,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
# --------------------------------------------------
# Test helpers
# --------------------------------------------------
 
def create_context(
) -> EngineeringContext:
    """
    Create a valid EngineeringContext for assessment-engine
    orchestration checks.
    """
 
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
    )
 
    return EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=optimization_result,
        known_limitations=(
            "Radiation heat transfer is not yet included.",
            "Fan accuracy depends on the supplied fan curve.",
        ),
    )
 
 
def create_insight(
    insight_id: str,
) -> EngineeringInsight:
    """
    Create one deterministic test insight.
    """
 
    return EngineeringInsight(
        insight_id=insight_id,
        severity=EngineeringSeverity.INFO,
        category=EngineeringCategory.GENERAL,
        title="Test insight",
        summary=(
            "A deterministic test insight was supplied."
        ),
        evidence=(
            EngineeringEvidence(
                key="test_value",
                value=1,
            ),
        ),
    )
 
 
def create_assessment(
    assessment_id: str,
    *,
    source_insight_id: str = "",
) -> EngineeringAssessment:
    """
    Create one deterministic test assessment.
    """
 
    source_insight_ids = ()
 
    if source_insight_id:
        source_insight_ids = (
            source_insight_id,
        )
 
    return EngineeringAssessment(
        assessment_id=assessment_id,
        rule_id=(
            f"{assessment_id}.rule"
        ),
        severity=EngineeringSeverity.INFO,
        category=EngineeringCategory.GENERAL,
        title="Test assessment",
        summary=(
            "A deterministic test assessment was "
            "generated."
        ),
        evidence=(
            EngineeringEvidence(
                key="assessment_value",
                value=1,
            ),
        ),
        source_insight_ids=(
            source_insight_ids
        ),
        recommendation="",
        passed=True,
    )
 
 
class FirstEvaluator(
    EngineeringEvaluator,
):
    """
    Test evaluator returning two assessments.
    """
 
    def evaluate(
        self,
        context,
        insights,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        return (
            create_assessment(
                "test.first",
                source_insight_id=(
                    insights[0].insight_id
                ),
            ),
            create_assessment(
                "test.second",
            ),
        )
 
 
class SecondEvaluator(
    EngineeringEvaluator,
):
    """
    Test evaluator returning one assessment.
    """
 
    def evaluate(
        self,
        context,
        insights,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        return (
            create_assessment(
                "test.third",
            ),
        )
 
 
class EmptyEvaluator(
    EngineeringEvaluator,
):
    """
    Test evaluator with no applicable rules.
    """
 
    def evaluate(
        self,
        context,
        insights,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        return ()
 
 
class DuplicateEvaluator(
    EngineeringEvaluator,
):
    """
    Test evaluator returning a duplicate assessment ID.
    """
 
    def evaluate(
        self,
        context,
        insights,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        return (
            create_assessment(
                "test.first",
            ),
        )
 
 
class InvalidCollectionEvaluator(
    EngineeringEvaluator,
):
    """
    Test evaluator returning a list instead of a tuple.
    """
 
    def evaluate(
        self,
        context,
        insights,
    ):
        return [
            create_assessment(
                "test.invalid_collection",
            ),
        ]
 
 
class InvalidItemEvaluator(
    EngineeringEvaluator,
):
    """
    Test evaluator returning an invalid output item.
    """
 
    def evaluate(
        self,
        context,
        insights,
    ):
        return (
            "not an assessment",
        )
 
 
# --------------------------------------------------
# Valid orchestration
# --------------------------------------------------
 
context = create_context()
 
insights = (
    create_insight(
        "test.source_insight"
    ),
)
 
engine = EngineeringAssessmentEngine(
    evaluators=(
        FirstEvaluator(),
        EmptyEvaluator(),
        SecondEvaluator(),
    )
)
 
assert isinstance(
    engine.evaluators,
    tuple,
)
 
assert len(
    engine.evaluators
) == 3
 
assessments = engine.evaluate(
    context=context,
    insights=insights,
)
 
assert isinstance(
    assessments,
    tuple,
)
 
assert len(
    assessments
) == 3
 
assert tuple(
    assessment.assessment_id
    for assessment in assessments
) == (
    "test.first",
    "test.second",
    "test.third",
)
 
assert (
    assessments[0].source_insight_ids
    == (
        "test.source_insight",
    )
)
 
 
# --------------------------------------------------
# Empty engine
# --------------------------------------------------
 
empty_engine = (
    EngineeringAssessmentEngine()
)
 
empty_assessments = (
    empty_engine.evaluate(
        context=context,
        insights=insights,
    )
)
 
assert (
    empty_assessments
    == ()
)
 
 
# --------------------------------------------------
# Invalid evaluator configuration
# --------------------------------------------------
 
try:
    EngineeringAssessmentEngine(
        evaluators=[],
    )
 
except ValueError as exc:
    assert (
        "'evaluators' must be a tuple"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "A list of evaluators was accepted."
    )
 
 
try:
    EngineeringAssessmentEngine(
        evaluators=(
            "invalid evaluator",
        ),
    )
 
except ValueError as exc:
    assert (
        "Every evaluator must implement "
        "EngineeringEvaluator"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An invalid evaluator was accepted."
    )
 
 
# --------------------------------------------------
# Invalid context
# --------------------------------------------------
 
try:
    engine.evaluate(
        context=None,
        insights=insights,
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
 
 
# --------------------------------------------------
# Invalid insight collection
# --------------------------------------------------
 
try:
    engine.evaluate(
        context=context,
        insights=[],
    )
 
except ValueError as exc:
    assert (
        "'insights' must be a tuple"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "A list of insights was accepted."
    )
 
 
try:
    engine.evaluate(
        context=context,
        insights=(
            "invalid insight",
        ),
    )
 
except ValueError as exc:
    assert (
        "Every insight must be an "
        "EngineeringInsight object"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An invalid insight item was accepted."
    )
 
 
# --------------------------------------------------
# Invalid evaluator outputs
# --------------------------------------------------
 
invalid_collection_engine = (
    EngineeringAssessmentEngine(
        evaluators=(
            InvalidCollectionEvaluator(),
        )
    )
)
 
try:
    invalid_collection_engine.evaluate(
        context=context,
        insights=insights,
    )
 
except ValueError as exc:
    assert (
        "InvalidCollectionEvaluator.evaluate() "
        "must return a tuple"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An evaluator list result was accepted."
    )
 
 
invalid_item_engine = (
    EngineeringAssessmentEngine(
        evaluators=(
            InvalidItemEvaluator(),
        )
    )
)
 
try:
    invalid_item_engine.evaluate(
        context=context,
        insights=insights,
    )
 
except ValueError as exc:
    assert (
        "returned an item that is not an "
        "EngineeringAssessment"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "An invalid assessment item was accepted."
    )
 
 
# --------------------------------------------------
# Duplicate assessment IDs
# --------------------------------------------------
 
duplicate_engine = (
    EngineeringAssessmentEngine(
        evaluators=(
            FirstEvaluator(),
            DuplicateEvaluator(),
        )
    )
)
 
try:
    duplicate_engine.evaluate(
        context=context,
        insights=insights,
    )
 
except ValueError as exc:
    assert (
        "Duplicate engineering assessment ID: "
        "'test.first'"
        in str(exc)
    )
 
else:
    raise AssertionError(
        "Duplicate engineering assessment IDs were "
        "accepted."
    )
 
 
print(
    "ALL ENGINEERING ASSESSMENT ENGINE "
    "CHECKS PASSED"
)