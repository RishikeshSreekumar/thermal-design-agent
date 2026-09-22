"""
engineering_review_synthesizer.py
 
High-level deterministic engineering-review synthesizer.
 
This module converts the complete EngineeringReviewSource
into a validated EngineeringReview.
 
It performs no new engineering calculation, introduces no
new evaluator threshold, and invokes no LLM.
 
Its purpose is to establish a complete deterministic review
baseline that later AI synthesis may enrich without changing
the underlying engineering verdict or traceability.
"""
 
from core.engineering_review_status_resolver import (
    EngineeringReviewStatusResolver,
)
from core.engineering_review_structure_synthesizer import (
    EngineeringReviewStructureSynthesizer,
)
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
 
 
class EngineeringReviewSynthesizer:
    """
    Assemble one complete deterministic EngineeringReview.
    """
 
    @classmethod
    def synthesize(
        cls,
        source: EngineeringReviewSource,
    ) -> EngineeringReview:
        """
        Generate the complete deterministic review.
        """
 
        if not isinstance(
            source,
            EngineeringReviewSource,
        ):
            raise ValueError(
                "'source' must be an "
                "EngineeringReviewSource object."
            )
 
        components = (
            EngineeringReviewStructureSynthesizer
            .synthesize(
                source
            )
        )
 
        status = (
            EngineeringReviewStatusResolver
            .resolve(
                source.assessments
            )
        )
 
        # A review cannot be called fully acceptable when
        # explicit validation requirements remain.
        #
        # This does not alter an engineering assessment.
        # It only keeps the consolidated review status
        # consistent with its own required-validation
        # section.
        if (
            status
            == EngineeringReviewStatus.ACCEPTABLE
            and components.validation_requirements
        ):
            status = (
                EngineeringReviewStatus
                .ACCEPTABLE_WITH_ACTIONS
            )
 
        executive_summary = (
            cls._build_executive_summary(
                source=source,
                status=status,
                strength_count=len(
                    components.strengths
                ),
                concern_count=len(
                    components.concerns
                ),
                action_count=len(
                    components.required_actions
                ),
                validation_count=len(
                    components
                    .validation_requirements
                ),
            )
        )
 
        return EngineeringReview(
            status=status,
            executive_summary=(
                executive_summary
            ),
            strengths=components.strengths,
            concerns=components.concerns,
            sections=components.sections,
 
            # Cross-category engineering trade-off
            # generation is intentionally deferred to the
            # grounded synthesis layer. No trade-off is
            # invented here.
            tradeoffs=(),
 
            required_actions=(
                components.required_actions
            ),
            validation_requirements=(
                components
                .validation_requirements
            ),
            source_assessment_ids=tuple(
                assessment.assessment_id
                for assessment
                in source.assessments
            ),
            source_insight_ids=tuple(
                insight.insight_id
                for insight
                in source.insights
            ),
        )
 
    @staticmethod
    def _build_executive_summary(
        *,
        source: EngineeringReviewSource,
        status: EngineeringReviewStatus,
        strength_count: int,
        concern_count: int,
        action_count: int,
        validation_count: int,
    ) -> str:
        """
        Build a factual deterministic executive summary.
 
        Rich engineering narrative is deliberately deferred
        to the later LLM synthesis layer.
        """
 
        selected_design_count = len(
            source.context.selected_candidates
        )
 
        assessment_count = len(
            source.assessments
        )
 
        insight_count = len(
            source.insights
        )
 
        return (
            "Engineering review completed for "
            f"{selected_design_count} selected design"
            f"{'' if selected_design_count == 1 else 's'}. "
            f"The deterministic intelligence layer produced "
            f"{insight_count} engineering insight(s) and "
            f"{assessment_count} engineering assessment(s). "
            f"The consolidated review status is "
            f"'{status.value}'. "
            f"The review contains {strength_count} "
            f"confirmed strength(s), {concern_count} "
            f"concern(s), {action_count} required "
            f"action(s), and {validation_count} validation "
            f"requirement(s)."
        )