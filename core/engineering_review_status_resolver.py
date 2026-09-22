"""
engineering_review_status_resolver.py
 
Deterministically resolves consolidated engineering-review
status from existing engineering assessments.
 
This module performs no engineering calculation and
introduces no new engineering thresholds.
 
It only interprets assessment outcomes already produced by
the deterministic EngineeringAssessment layer.
"""
 
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
class EngineeringReviewStatusResolver:
    """
    Resolve deterministic engineering assessments into the
    controlled EngineeringReviewStatus model.
    """
 
    @staticmethod
    def resolve(
        assessments: tuple[
            EngineeringAssessment,
            ...,
        ],
    ) -> EngineeringReviewStatus:
        """
        Resolve one assessment collection into a single
        review status.
 
        Status precedence is intentionally conservative:
 
        1. Failed CRITICAL
        2. Failed WARNING
        3. Failed INFO
        4. Any other failed assessment
        5. Passing WARNING
        6. Fully acceptable
        """
 
        EngineeringReviewStatusResolver._validate(
            assessments
        )
 
        if not assessments:
            return (
                EngineeringReviewStatus
                .INSUFFICIENT_EVIDENCE
            )
 
        if any(
            (
                not assessment.passed
                and assessment.severity
                == EngineeringSeverity.CRITICAL
            )
            for assessment in assessments
        ):
            return (
                EngineeringReviewStatus
                .NOT_RECOMMENDED
            )
 
        if any(
            (
                not assessment.passed
                and assessment.severity
                == EngineeringSeverity.WARNING
            )
            for assessment in assessments
        ):
            return (
                EngineeringReviewStatus
                .REVIEW_REQUIRED
            )
 
        if any(
            (
                not assessment.passed
                and assessment.severity
                == EngineeringSeverity.INFO
            )
            for assessment in assessments
        ):
            return (
                EngineeringReviewStatus
                .INSUFFICIENT_EVIDENCE
            )
 
        if any(
            not assessment.passed
            for assessment in assessments
        ):
            return (
                EngineeringReviewStatus
                .REVIEW_REQUIRED
            )
 
        if any(
            assessment.severity
            == EngineeringSeverity.WARNING
            for assessment in assessments
        ):
            return (
                EngineeringReviewStatus
                .ACCEPTABLE_WITH_ACTIONS
            )
 
        return (
            EngineeringReviewStatus.ACCEPTABLE
        )
 
    @staticmethod
    def _validate(
        assessments,
    ) -> None:
        """
        Validate the assessment collection before status
        resolution.
        """
 
        if not isinstance(
            assessments,
            tuple,
        ):
            raise ValueError(
                "'assessments' must be a tuple."
            )
 
        for assessment in assessments:
            if not isinstance(
                assessment,
                EngineeringAssessment,
            ):
                raise ValueError(
                    "Every assessment must be an "
                    "EngineeringAssessment object."
                )