"""
engineering_review_ai_merger.py
 
Merges validated AI synthesis into an authoritative
deterministic EngineeringReview.
 
The AI may replace communication fields only:
 
- executive summary;
- category section summaries;
- grounded trade-offs.
 
The following remain unchanged:
 
- overall deterministic status;
- strengths;
- concerns;
- findings;
- actions;
- validation requirements;
- assessment traceability;
- insight traceability.
"""
 
from dataclasses import replace
 
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_ai_synthesis import (
    EngineeringReviewAISynthesis,
)
from models.engineering_tradeoff import (
    EngineeringTradeoff,
)
 
 
class EngineeringReviewAIMerger:
    """
    Merge non-authoritative AI synthesis into the locked
    deterministic engineering review.
    """
 
    @staticmethod
    def merge(
        *,
        deterministic_review: EngineeringReview,
        ai_synthesis: EngineeringReviewAISynthesis,
    ) -> EngineeringReview:
        """
        Return an AI-enriched but deterministically
        authoritative EngineeringReview.
        """
 
        if not isinstance(
            deterministic_review,
            EngineeringReview,
        ):
            raise ValueError(
                "'deterministic_review' must be an "
                "EngineeringReview object."
            )
 
        if not isinstance(
            ai_synthesis,
            EngineeringReviewAISynthesis,
        ):
            raise ValueError(
                "'ai_synthesis' must be an "
                "EngineeringReviewAISynthesis object."
            )
 
        summary_by_category = {
            section.category: section.summary
            for section
            in ai_synthesis.section_summaries
        }
 
        enriched_sections = tuple(
            replace(
                section,
                summary=summary_by_category.get(
                    section.category,
                    section.summary,
                ),
            )
            for section
            in deterministic_review.sections
        )
 
        tradeoffs = tuple(
            EngineeringTradeoff(
                tradeoff_id=(
                    tradeoff.tradeoff_id
                ),
                title=tradeoff.title,
                severity=tradeoff.severity,
                categories=tradeoff.categories,
                benefit=tradeoff.benefit,
                penalty=tradeoff.penalty,
                guidance=tradeoff.guidance,
                source_assessment_ids=(
                    tradeoff
                    .source_assessment_ids
                ),
                source_insight_ids=(
                    tradeoff
                    .source_insight_ids
                ),
            )
            for tradeoff
            in ai_synthesis.tradeoffs
        )
 
        return EngineeringReview(
            status=deterministic_review.status,
            executive_summary=(
                ai_synthesis.executive_summary
            ),
            strengths=(
                deterministic_review.strengths
            ),
            concerns=(
                deterministic_review.concerns
            ),
            sections=enriched_sections,
            tradeoffs=tradeoffs,
            required_actions=(
                deterministic_review
                .required_actions
            ),
            validation_requirements=(
                deterministic_review
                .validation_requirements
            ),
            source_assessment_ids=(
                deterministic_review
                .source_assessment_ids
            ),
            source_insight_ids=(
                deterministic_review
                .source_insight_ids
            ),
        )