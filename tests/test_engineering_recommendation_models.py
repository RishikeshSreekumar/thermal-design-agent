"""
Focused regression checks for Step 35 recommendation
models.
"""
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_recommendation import (
    EngineeringRecommendation,
)
from models.engineering_recommendation_priority import (
    EngineeringRecommendationPriority,
)
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from models.engineering_recommendation_type import (
    EngineeringRecommendationType,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
def expect_value_error(
    callable_object,
    expected_message: str,
) -> None:
    """
    Verify that invalid model construction is rejected.
    """
 
    try:
        callable_object()
 
    except ValueError as error:
        assert (
            expected_message
            in str(error)
        )
 
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
 
 
# --------------------------------------------------
# Recommendation model
# --------------------------------------------------
 
thermal_recommendation = (
    EngineeringRecommendation(
        recommendation_id=(
            "recommendation.thermal.margin"
        ),
        recommendation_type=(
            EngineeringRecommendationType
            .DESIGN_IMPROVEMENT
        ),
        priority=(
            EngineeringRecommendationPriority.HIGH
        ),
        category=EngineeringCategory.THERMAL,
        severity=EngineeringSeverity.WARNING,
        title="Improve thermal margin",
        recommendation=(
            "Increase available thermal margin before "
            "design release."
        ),
        rationale=(
            "The deterministic thermal assessment "
            "identified limited remaining margin."
        ),
        expected_effect=(
            "Improve robustness against thermal variation."
        ),
        verification=(
            "Re-run the deterministic thermal assessment."
        ),
        source_review_item_ids=(
            "concern.thermal.margin",
        ),
        source_assessment_ids=(
            "assessment.thermal.margin",
        ),
        source_insight_ids=(
            "thermal.margin",
        ),
    )
)
 
assert thermal_recommendation.is_traceable
assert thermal_recommendation.has_expected_effect
assert thermal_recommendation.has_verification
 
assert (
    thermal_recommendation.priority
    == EngineeringRecommendationPriority.HIGH
)
 
 
validation_recommendation = (
    EngineeringRecommendation(
        recommendation_id=(
            "recommendation.validation.radiation"
        ),
        recommendation_type=(
            EngineeringRecommendationType
            .VALIDATION
        ),
        priority=(
            EngineeringRecommendationPriority.MEDIUM
        ),
        category=(
            EngineeringCategory.MODEL_LIMITATION
        ),
        severity=EngineeringSeverity.WARNING,
        title="Validate radiation assumption",
        recommendation=(
            "Review the effect of omitted radiation "
            "heat transfer before release."
        ),
        rationale=(
            "Radiation is declared as a current model "
            "limitation."
        ),
        source_review_item_ids=(
            "validation.model.radiation",
        ),
        source_insight_ids=(
            "model.radiation",
        ),
    )
)
 
 
# --------------------------------------------------
# Invalid recommendation contracts
# --------------------------------------------------
 
expect_value_error(
    lambda: EngineeringRecommendation(
        recommendation_id="",
        recommendation_type=(
            EngineeringRecommendationType
            .VALIDATION
        ),
        priority=(
            EngineeringRecommendationPriority.LOW
        ),
        category=EngineeringCategory.THERMAL,
        severity=EngineeringSeverity.INFO,
        title="Valid title",
        recommendation="Valid action.",
        rationale="Valid rationale.",
        source_insight_ids=(
            "thermal.valid",
        ),
    ),
    "'recommendation_id' cannot be empty",
)
 
expect_value_error(
    lambda: EngineeringRecommendation(
        recommendation_id=(
            "recommendation.untraceable"
        ),
        recommendation_type=(
            EngineeringRecommendationType
            .DESIGN_IMPROVEMENT
        ),
        priority=(
            EngineeringRecommendationPriority.LOW
        ),
        category=EngineeringCategory.THERMAL,
        severity=EngineeringSeverity.INFO,
        title="Untraceable",
        recommendation="Valid action.",
        rationale="Valid rationale.",
    ),
    "must reference at least one review item",
)
 
 
# --------------------------------------------------
# Result-model validation without duplicating the
# complete EngineeringReviewResult fixture here.
#
# Full integration with EngineeringReviewResult will be
# regression-tested in Step 35.2 using the existing
# Step 34 fixture.
# --------------------------------------------------
 
expect_value_error(
    lambda: EngineeringRecommendationResult(
        review_result="invalid",
        recommendations=(),
    ),
    "'review_result' must be an "
    "EngineeringReviewResult object",
)
 
 
print(
    "ALL ENGINEERING RECOMMENDATION MODEL CHECKS PASSED"
)