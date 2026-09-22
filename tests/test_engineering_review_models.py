"""
Focused checks for structured engineering-review models.
"""
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_item import (
    EngineeringReviewItem,
)
from models.engineering_review_section import (
    EngineeringReviewSection,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
from models.engineering_tradeoff import (
    EngineeringTradeoff,
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
 
 
thermal_strength = EngineeringReviewItem(
    item_id="strength.thermal.requirement_met",
    category=EngineeringCategory.THERMAL,
    severity=EngineeringSeverity.SUCCESS,
    title="Thermal requirement satisfied",
    summary=(
        "The selected design satisfies the configured "
        "thermal-performance requirement."
    ),
    source_assessment_ids=(
        "assessment.thermal.margin",
    ),
    source_insight_ids=(
        "thermal.selected_candidate_performance",
    ),
)
 
airflow_concern = EngineeringReviewItem(
    item_id="concern.airflow.pressure_margin",
    category=EngineeringCategory.AIRFLOW,
    severity=EngineeringSeverity.WARNING,
    title="Limited airflow pressure margin",
    summary=(
        "The predicted pressure loss consumes a substantial "
        "portion of the available fan pressure."
    ),
    consequence=(
        "The achieved operating airflow may be sensitive "
        "to fan and system-model uncertainty."
    ),
    verification=(
        "Confirm the operating point using the approved "
        "fan curve or a system-level airflow test."
    ),
    source_assessment_ids=(
        "assessment.airflow.performance",
    ),
    source_insight_ids=(
        "airflow.pressure_drop_margin",
    ),
)
 
validation_action = EngineeringReviewItem(
    item_id="validation.airflow.operating_point",
    category=EngineeringCategory.AIRFLOW,
    severity=EngineeringSeverity.WARNING,
    title="Validate the airflow operating point",
    summary=(
        "The fan-coupled operating point requires "
        "confirmation before design release."
    ),
    verification=(
        "Use an approved fan curve, CFD, or physical "
        "airflow testing."
    ),
    source_assessment_ids=(
        "assessment.airflow.performance",
    ),
)
 
thermal_section = EngineeringReviewSection(
    category=EngineeringCategory.THERMAL,
    status=EngineeringReviewStatus.ACCEPTABLE,
    summary=(
        "The selected candidate satisfies the configured "
        "thermal requirement under the current model."
    ),
    findings=(
        thermal_strength,
    ),
    source_assessment_ids=(
        "assessment.thermal.margin",
    ),
    source_insight_ids=(
        "thermal.selected_candidate_performance",
    ),
)
 
airflow_section = EngineeringReviewSection(
    category=EngineeringCategory.AIRFLOW,
    status=(
        EngineeringReviewStatus
        .ACCEPTABLE_WITH_ACTIONS
    ),
    summary=(
        "Airflow performance is feasible, but the "
        "available pressure margin requires validation."
    ),
    findings=(
        airflow_concern,
    ),
    source_assessment_ids=(
        "assessment.airflow.performance",
    ),
    source_insight_ids=(
        "airflow.pressure_drop_margin",
    ),
)
 
thermal_airflow_tradeoff = EngineeringTradeoff(
    tradeoff_id=(
        "tradeoff.thermal_airflow.fin_spacing"
    ),
    title=(
        "Heat-transfer area versus airflow restriction"
    ),
    severity=EngineeringSeverity.WARNING,
    categories=(
        EngineeringCategory.THERMAL,
        EngineeringCategory.AIRFLOW,
    ),
    benefit=(
        "Closer fin spacing may increase the available "
        "heat-transfer surface area."
    ),
    penalty=(
        "Closer fin spacing may increase flow restriction "
        "and pressure loss."
    ),
    guidance=(
        "Evaluate thermal improvement together with the "
        "resulting fan operating point."
    ),
    source_assessment_ids=(
        "assessment.thermal.margin",
        "assessment.airflow.performance",
    ),
    source_insight_ids=(
        "thermal.selected_candidate_performance",
        "airflow.pressure_drop_margin",
    ),
)
 
review = EngineeringReview(
    status=(
        EngineeringReviewStatus
        .ACCEPTABLE_WITH_ACTIONS
    ),
    executive_summary=(
        "The selected design satisfies the configured "
        "thermal requirement. Airflow operating-point "
        "validation remains necessary before release."
    ),
    strengths=(
        thermal_strength,
    ),
    sections=(
        thermal_section,
        airflow_section,
    ),
    tradeoffs=(
        thermal_airflow_tradeoff,
    ),
    validation_requirements=(
        validation_action,
    ),
    source_assessment_ids=(
        "assessment.thermal.margin",
        "assessment.airflow.performance",
    ),
    source_insight_ids=(
        "thermal.selected_candidate_performance",
        "airflow.pressure_drop_margin",
    ),
)
 
assert (
    review.status
    == EngineeringReviewStatus
    .ACCEPTABLE_WITH_ACTIONS
)
 
assert review.has_strengths
 
assert not review.has_concerns
 
assert review.has_tradeoffs
 
assert not review.has_required_actions
 
assert review.requires_validation
 
assert thermal_strength.is_traceable
 
assert not thermal_strength.has_consequence
 
assert airflow_concern.has_consequence
 
assert airflow_concern.has_verification
 
assert thermal_section.has_findings
 
expect_value_error(
    lambda: EngineeringReviewItem(
        item_id="",
        category=EngineeringCategory.THERMAL,
        severity=EngineeringSeverity.INFO,
        title="Valid title",
        summary="Valid summary.",
        source_insight_ids=(
            "thermal.valid",
        ),
    ),
    "review item ID cannot be empty",
)
 
expect_value_error(
    lambda: EngineeringReviewItem(
        item_id="review.untraceable",
        category=EngineeringCategory.GENERAL,
        severity=EngineeringSeverity.INFO,
        title="Untraceable item",
        summary=(
            "This item has no deterministic source."
        ),
    ),
    "must reference at least one assessment or insight",
)
 
expect_value_error(
    lambda: EngineeringReviewSection(
        category=EngineeringCategory.THERMAL,
        status=EngineeringReviewStatus.ACCEPTABLE,
        summary="Invalid mixed-category section.",
        findings=(
            airflow_concern,
        ),
    ),
    "same engineering category as its section",
)
 
expect_value_error(
    lambda: EngineeringTradeoff(
        tradeoff_id="tradeoff.invalid",
        title="Invalid trade-off",
        severity=EngineeringSeverity.INFO,
        categories=(
            EngineeringCategory.THERMAL,
        ),
        benefit="Valid benefit.",
        penalty="Valid penalty.",
        source_insight_ids=(
            "thermal.valid",
        ),
    ),
    "at least two engineering categories",
)
 
expect_value_error(
    lambda: EngineeringReview(
        status=EngineeringReviewStatus.ACCEPTABLE,
        executive_summary="Duplicate-section test.",
        sections=(
            thermal_section,
            EngineeringReviewSection(
                category=EngineeringCategory.THERMAL,
                status=(
                    EngineeringReviewStatus
                    .REVIEW_REQUIRED
                ),
                summary="Second thermal section.",
            ),
        ),
    ),
    "Duplicate engineering review section category",
)
 
expect_value_error(
    lambda: EngineeringReview(
        status=EngineeringReviewStatus.ACCEPTABLE,
        executive_summary="Duplicate-item test.",
        strengths=(
            thermal_strength,
            thermal_strength,
        ),
    ),
    (
        "Duplicate engineering review item ID in "
        "'strengths'"
    ),
)
 
print(
    "ALL ENGINEERING REVIEW MODEL CHECKS PASSED"
)