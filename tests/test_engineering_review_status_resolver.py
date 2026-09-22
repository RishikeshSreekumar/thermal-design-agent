"""
Focused regression checks for deterministic engineering
review-status resolution.
"""
 
from core.engineering_review_status_resolver import (
    EngineeringReviewStatusResolver,
)
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
def make_assessment(
    *,
    assessment_id: str,
    severity: EngineeringSeverity,
    passed: bool,
) -> EngineeringAssessment:
    """
    Create one minimal valid deterministic assessment for
    review-status regression testing.
    """
 
    return EngineeringAssessment(
        assessment_id=assessment_id,
        rule_id=f"rule.{assessment_id}",
        severity=severity,
        category=EngineeringCategory.THERMAL,
        title="Test assessment",
        summary="Deterministic test assessment.",
        passed=passed,
    )
 
 
success_assessment = make_assessment(
    assessment_id="assessment.success",
    severity=EngineeringSeverity.SUCCESS,
    passed=True,
)
 
warning_pass_assessment = make_assessment(
    assessment_id="assessment.warning.pass",
    severity=EngineeringSeverity.WARNING,
    passed=True,
)
 
warning_fail_assessment = make_assessment(
    assessment_id="assessment.warning.fail",
    severity=EngineeringSeverity.WARNING,
    passed=False,
)
 
critical_fail_assessment = make_assessment(
    assessment_id="assessment.critical.fail",
    severity=EngineeringSeverity.CRITICAL,
    passed=False,
)
 
info_fail_assessment = make_assessment(
    assessment_id="assessment.info.fail",
    severity=EngineeringSeverity.INFO,
    passed=False,
)
 
 
# --------------------------------------------------
# No deterministic assessment evidence
# --------------------------------------------------
 
assert (
    EngineeringReviewStatusResolver.resolve(
        ()
    )
    == EngineeringReviewStatus
    .INSUFFICIENT_EVIDENCE
)
 
 
# --------------------------------------------------
# Fully acceptable deterministic evidence
# --------------------------------------------------
 
assert (
    EngineeringReviewStatusResolver.resolve(
        (
            success_assessment,
        )
    )
    == EngineeringReviewStatus.ACCEPTABLE
)
 
 
# --------------------------------------------------
# Passing warning requires follow-up action
# --------------------------------------------------
 
assert (
    EngineeringReviewStatusResolver.resolve(
        (
            success_assessment,
            warning_pass_assessment,
        )
    )
    == EngineeringReviewStatus
    .ACCEPTABLE_WITH_ACTIONS
)
 
 
# --------------------------------------------------
# Failed warning requires engineering review
# --------------------------------------------------
 
assert (
    EngineeringReviewStatusResolver.resolve(
        (
            success_assessment,
            warning_fail_assessment,
        )
    )
    == EngineeringReviewStatus
    .REVIEW_REQUIRED
)
 
 
# --------------------------------------------------
# Missing evaluation evidence
# --------------------------------------------------
 
assert (
    EngineeringReviewStatusResolver.resolve(
        (
            success_assessment,
            info_fail_assessment,
        )
    )
    == EngineeringReviewStatus
    .INSUFFICIENT_EVIDENCE
)
 
 
# --------------------------------------------------
# Critical failure dominates every lesser status
# --------------------------------------------------
 
assert (
    EngineeringReviewStatusResolver.resolve(
        (
            success_assessment,
            warning_pass_assessment,
            warning_fail_assessment,
            critical_fail_assessment,
        )
    )
    == EngineeringReviewStatus
    .NOT_RECOMMENDED
)
 
 
# --------------------------------------------------
# Input validation
# --------------------------------------------------
 
try:
    EngineeringReviewStatusResolver.resolve(
        []
    )
 
except ValueError as error:
    assert (
        "'assessments' must be a tuple"
        in str(error)
    )
 
else:
    raise AssertionError(
        "Non-tuple assessment collection was accepted."
    )
 
 
try:
    EngineeringReviewStatusResolver.resolve(
        (
            "invalid",
        )
    )
 
except ValueError as error:
    assert (
        "Every assessment must be an "
        "EngineeringAssessment object"
        in str(error)
    )
 
else:
    raise AssertionError(
        "Invalid assessment object was accepted."
    )
 
 
print(
    "ALL ENGINEERING REVIEW STATUS RESOLVER CHECKS PASSED"
)