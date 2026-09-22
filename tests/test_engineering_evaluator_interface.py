"""
Focused checks for the rule-based engineering evaluator
interface and EngineeringAssessment model.
"""
 
from abc import ABC
from dataclasses import FrozenInstanceError
 
from intelligence.evaluators.base_evaluator import (
    EngineeringEvaluator,
)
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_evidence import (
    EngineeringEvidence,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
# --------------------------------------------------
# Evaluator interface
# --------------------------------------------------
 
assert issubclass(
    EngineeringEvaluator,
    ABC,
)
 
assert (
    "evaluate"
    in EngineeringEvaluator.__abstractmethods__
)
 
 
try:
    EngineeringEvaluator()
 
except TypeError:
    pass
 
else:
    raise AssertionError(
        "EngineeringEvaluator must remain abstract."
    )
 
 
# --------------------------------------------------
# Minimal concrete evaluator
# --------------------------------------------------
 
class ExampleEvaluator(
    EngineeringEvaluator,
):
    """
    Test-only evaluator proving the common interface.
 
    This evaluator introduces no engineering threshold.
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
            EngineeringAssessment(
                assessment_id=(
                    "test.rule_interface"
                ),
                rule_id=(
                    "test.interface_rule"
                ),
                severity=(
                    EngineeringSeverity.INFO
                ),
                category=(
                    EngineeringCategory.GENERAL
                ),
                title=(
                    "Evaluator interface check"
                ),
                summary=(
                    "The test evaluator returned a "
                    "structured deterministic assessment."
                ),
                evidence=(
                    EngineeringEvidence(
                        key="insight_count",
                        value=len(insights),
                    ),
                ),
                source_insight_ids=tuple(
                    insight.insight_id
                    for insight in insights
                ),
                recommendation="",
                passed=True,
            ),
        )
 
 
example_evaluator = ExampleEvaluator()
 
example_assessments = (
    example_evaluator.evaluate(
        context=None,
        insights=(),
    )
)
 
assert isinstance(
    example_assessments,
    tuple,
)
 
assert len(
    example_assessments
) == 1
 
 
# --------------------------------------------------
# Valid assessment
# --------------------------------------------------
 
assessment = example_assessments[0]
 
assert isinstance(
    assessment,
    EngineeringAssessment,
)
 
assert (
    assessment.assessment_id
    == "test.rule_interface"
)
 
assert (
    assessment.rule_id
    == "test.interface_rule"
)
 
assert (
    assessment.severity
    == EngineeringSeverity.INFO
)
 
assert (
    assessment.category
    == EngineeringCategory.GENERAL
)
 
assert assessment.passed
 
assert assessment.has_evidence
 
assert not assessment.has_source_insights
 
assert not assessment.has_recommendation
 
assert (
    assessment.evidence[0].key
    == "insight_count"
)
 
assert (
    assessment.evidence[0].value
    == 0
)
 
 
# --------------------------------------------------
# Normalization
# --------------------------------------------------
 
normalized_assessment = (
    EngineeringAssessment(
        assessment_id="  thermal.margin  ",
        rule_id="  thermal.maximum_temperature  ",
        severity=(
            EngineeringSeverity.WARNING
        ),
        category=(
            EngineeringCategory.THERMAL
        ),
        title="  Thermal margin  ",
        summary=(
            "  The rule identified a thermal-margin "
            "concern.  "
        ),
        evidence=(
            EngineeringEvidence(
                key=(
                    "estimated_base_temperature"
                ),
                value=99.3,
                unit="degC",
            ),
        ),
        source_insight_ids=(
            "  thermal.selected_design_performance  ",
        ),
        recommendation=(
            "  Review the permitted operating "
            "temperature.  "
        ),
        passed=False,
    )
)
 
assert (
    normalized_assessment.assessment_id
    == "thermal.margin"
)
 
assert (
    normalized_assessment.rule_id
    == "thermal.maximum_temperature"
)
 
assert (
    normalized_assessment.title
    == "Thermal margin"
)
 
assert (
    normalized_assessment.summary
    == (
        "The rule identified a thermal-margin "
        "concern."
    )
)
 
assert (
    normalized_assessment.source_insight_ids
    == (
        "thermal.selected_design_performance",
    )
)
 
assert (
    normalized_assessment.recommendation
    == (
        "Review the permitted operating "
        "temperature."
    )
)
 
assert (
    normalized_assessment.has_source_insights
)
 
assert (
    normalized_assessment.has_recommendation
)
 
assert not normalized_assessment.passed
 
 
# --------------------------------------------------
# Immutability
# --------------------------------------------------
 
try:
    assessment.title = "Changed"
 
except FrozenInstanceError:
    pass
 
else:
    raise AssertionError(
        "EngineeringAssessment must remain immutable."
    )
 
 
# --------------------------------------------------
# Invalid assessment helpers
# --------------------------------------------------
 
def assert_value_error(
    expected_message: str,
    **arguments,
) -> None:
    """
    Verify that an invalid assessment definition is
    rejected.
    """
 
    try:
        EngineeringAssessment(
            **arguments
        )
 
    except ValueError as exc:
        assert (
            expected_message
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid EngineeringAssessment was accepted."
        )
 
 
def valid_arguments() -> dict:
    """
    Return a fresh valid assessment definition.
    """
 
    return {
        "assessment_id": (
            "test.valid_assessment"
        ),
        "rule_id": (
            "test.valid_rule"
        ),
        "severity": (
            EngineeringSeverity.INFO
        ),
        "category": (
            EngineeringCategory.GENERAL
        ),
        "title": (
            "Valid assessment"
        ),
        "summary": (
            "The assessment definition is valid."
        ),
        "evidence": (),
        "source_insight_ids": (),
        "recommendation": "",
        "passed": True,
    }
 
 
# --------------------------------------------------
# Invalid identifiers and text
# --------------------------------------------------
 
arguments = valid_arguments()
arguments["assessment_id"] = "   "
 
assert_value_error(
    "assessment ID cannot be empty",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["rule_id"] = "   "
 
assert_value_error(
    "rule ID cannot be empty",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["title"] = "   "
 
assert_value_error(
    "assessment title cannot be empty",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["summary"] = "   "
 
assert_value_error(
    "assessment summary cannot be empty",
    **arguments,
)
 
 
# --------------------------------------------------
# Invalid enum values
# --------------------------------------------------
 
arguments = valid_arguments()
arguments["severity"] = "warning"
 
assert_value_error(
    "'severity' must be an "
    "EngineeringSeverity value",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["category"] = "thermal"
 
assert_value_error(
    "'category' must be an "
    "EngineeringCategory value",
    **arguments,
)
 
 
# --------------------------------------------------
# Invalid evidence
# --------------------------------------------------
 
arguments = valid_arguments()
arguments["evidence"] = []
 
assert_value_error(
    "'evidence' must be a tuple",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["evidence"] = (
    "invalid evidence",
)
 
assert_value_error(
    "Every assessment evidence item",
    **arguments,
)
 
 
# --------------------------------------------------
# Invalid source-insight references
# --------------------------------------------------
 
arguments = valid_arguments()
arguments["source_insight_ids"] = []
 
assert_value_error(
    "'source_insight_ids' must be a tuple",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["source_insight_ids"] = (
    "",
)
 
assert_value_error(
    "Source insight IDs cannot be empty",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["source_insight_ids"] = (
    "thermal.performance",
    "thermal.performance",
)
 
assert_value_error(
    "Source insight IDs must be unique",
    **arguments,
)
 
 
# --------------------------------------------------
# Invalid recommendation and pass state
# --------------------------------------------------
 
arguments = valid_arguments()
arguments["recommendation"] = None
 
assert_value_error(
    "'recommendation' must be a string",
    **arguments,
)
 
 
arguments = valid_arguments()
arguments["passed"] = 1
 
assert_value_error(
    "'passed' must be a bool",
    **arguments,
)
 
 
print(
    "ALL ENGINEERING EVALUATOR INTERFACE "
    "CHECKS PASSED"
)