"""
engineering_review_result.py
 
Canonical output of the complete Engineering Review
workflow.
 
The result preserves:
 
- the complete deterministic engineering source;
- the deterministic review baseline;
- the final review presented to downstream systems;
- whether AI enrichment was successfully applied;
- whether deterministic fallback was required.
 
The deterministic engineering verdict always remains
authoritative.
"""
 
from dataclasses import dataclass
 
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
 
 
@dataclass(frozen=True)
class EngineeringReviewResult:
    """
    Complete output of Step 34 — Engineering Review
    Synthesis.
    """
 
    source: EngineeringReviewSource
 
    deterministic_review: EngineeringReview
 
    review: EngineeringReview
 
    ai_requested: bool
 
    ai_enriched: bool
 
    fallback_reason: str = ""
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the complete review result and enforce the
        deterministic-authority boundary.
        """
 
        if not isinstance(
            self.source,
            EngineeringReviewSource,
        ):
            raise ValueError(
                "'source' must be an "
                "EngineeringReviewSource object."
            )
 
        if not isinstance(
            self.deterministic_review,
            EngineeringReview,
        ):
            raise ValueError(
                "'deterministic_review' must be an "
                "EngineeringReview object."
            )
 
        if not isinstance(
            self.review,
            EngineeringReview,
        ):
            raise ValueError(
                "'review' must be an EngineeringReview "
                "object."
            )
 
        if not isinstance(
            self.ai_requested,
            bool,
        ):
            raise ValueError(
                "'ai_requested' must be a boolean."
            )
 
        if not isinstance(
            self.ai_enriched,
            bool,
        ):
            raise ValueError(
                "'ai_enriched' must be a boolean."
            )
 
        if (
            self.ai_enriched
            and not self.ai_requested
        ):
            raise ValueError(
                "AI enrichment cannot be true when AI "
                "synthesis was not requested."
            )
 
        if not isinstance(
            self.fallback_reason,
            str,
        ):
            raise ValueError(
                "'fallback_reason' must be a string."
            )
 
        normalized_reason = (
            self.fallback_reason.strip()
        )
 
        object.__setattr__(
            self,
            "fallback_reason",
            normalized_reason,
        )
 
        if (
            self.ai_enriched
            and normalized_reason
        ):
            raise ValueError(
                "Successful AI enrichment cannot also "
                "contain a fallback reason."
            )
 
        self._validate_source_population()
 
        self._validate_locked_authority()
 
    def _validate_source_population(
        self,
    ) -> None:
        """
        Confirm both reviews refer to the complete original
        engineering-intelligence population.
        """
 
        expected_assessment_ids = tuple(
            assessment.assessment_id
            for assessment
            in self.source.assessments
        )
 
        expected_insight_ids = tuple(
            insight.insight_id
            for insight
            in self.source.insights
        )
 
        for review in (
            self.deterministic_review,
            self.review,
        ):
            if (
                review.source_assessment_ids
                != expected_assessment_ids
            ):
                raise ValueError(
                    "Engineering review assessment sources "
                    "do not match the source package."
                )
 
            if (
                review.source_insight_ids
                != expected_insight_ids
            ):
                raise ValueError(
                    "Engineering review insight sources do "
                    "not match the source package."
                )
 
    def _validate_locked_authority(
        self,
    ) -> None:
        """
        Confirm AI enrichment has not modified any
        authoritative deterministic review fields.
        """
 
        deterministic = (
            self.deterministic_review
        )
 
        final = self.review
 
        if final.status != deterministic.status:
            raise ValueError(
                "AI synthesis cannot modify deterministic "
                "engineering review status."
            )
 
        if final.strengths != deterministic.strengths:
            raise ValueError(
                "AI synthesis cannot modify deterministic "
                "review strengths."
            )
 
        if final.concerns != deterministic.concerns:
            raise ValueError(
                "AI synthesis cannot modify deterministic "
                "review concerns."
            )
 
        if (
            final.required_actions
            != deterministic.required_actions
        ):
            raise ValueError(
                "AI synthesis cannot modify deterministic "
                "required actions."
            )
 
        if (
            final.validation_requirements
            != deterministic.validation_requirements
        ):
            raise ValueError(
                "AI synthesis cannot modify deterministic "
                "validation requirements."
            )
 
    @property
    def used_ai(
        self,
    ) -> bool:
        """
        Return True when AI enrichment was successfully
        applied.
        """
 
        return self.ai_enriched
 
    @property
    def used_fallback(
        self,
    ) -> bool:
        """
        Return True when requested AI synthesis failed and
        the deterministic review was returned instead.
        """
 
        return (
            self.ai_requested
            and not self.ai_enriched
            and bool(self.fallback_reason)
        )