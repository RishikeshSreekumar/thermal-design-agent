"""
engineering_recommendation_payload.py
 
Builds the grounded evidence package supplied to the
Step 35 AI Recommendation Engine.
 
The Recommendation Engine does not receive raw engineering
data in isolation. It receives the complete authoritative
Step 34 engineering evidence together with the final
structured Engineering Review.
 
This module performs no engineering calculation and creates
no recommendation.
"""
 
from llm.engineering_review_payload import (
    EngineeringReviewPayloadBuilder,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
 
 
class EngineeringRecommendationPayloadBuilder:
    """
    Build the grounded input package used for AI
    recommendation synthesis.
    """
 
    @classmethod
    def build(
        cls,
        review_result: EngineeringReviewResult,
    ) -> dict:
        """
        Build one JSON-serializable recommendation payload.
        """
 
        if not isinstance(
            review_result,
            EngineeringReviewResult,
        ):
            raise ValueError(
                "'review_result' must be an "
                "EngineeringReviewResult object."
            )
 
        source = review_result.source
 
        deterministic_review = (
            review_result.deterministic_review
        )
 
        final_review = review_result.review
 
        # Reuse the complete Step 34 grounded engineering
        # package instead of duplicating requirements,
        # candidate, optimization, insight, assessment,
        # and evidence serialization here.
        engineering_evidence = (
            EngineeringReviewPayloadBuilder.build(
                source=source,
                deterministic_review=(
                    deterministic_review
                ),
            )
        )
 
        return {
            "recommendation_contract": {
                "engineering_calculations_are_locked": True,
                "assessment_outcomes_are_locked": True,
                "engineering_review_status_is_locked": True,
 
                # AI is intentionally responsible for
                # recommendation reasoning and communication.
                "ai_may_propose": [
                    "recommendations",
                    "recommendation_priority",
                    "rationale",
                    "expected_effect",
                    "verification",
                ],
 
                # These boundaries will be enforced again by
                # the Step 35 grounding parser.
                "ai_must_not": [
                    "change_engineering_values",
                    "change_assessment_outcomes",
                    "change_review_status",
                    "invent_engineering_evidence",
                    "invent_source_ids",
                    "introduce_new_acceptance_thresholds",
                    "claim_unvalidated_performance",
                ],
            },
 
            "engineering_evidence": (
                engineering_evidence
            ),
 
            "final_engineering_review": {
                "status": (
                    final_review.status.value
                ),
 
                "executive_summary": (
                    final_review.executive_summary
                ),
 
                "strengths": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in final_review.strengths
                ],
 
                "concerns": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in final_review.concerns
                ],
 
                "required_actions": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in final_review.required_actions
                ],
 
                "validation_requirements": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in (
                        final_review
                        .validation_requirements
                    )
                ],
 
                "tradeoffs": [
                    cls._tradeoff_to_dict(
                        tradeoff
                    )
                    for tradeoff
                    in final_review.tradeoffs
                ],
            },
 
            # Explicit ID registries make later grounding
            # validation simple and unambiguous.
            "valid_source_ids": {
                "review_item_ids": (
                    cls._collect_review_item_ids(
                        final_review
                    )
                ),
 
                "tradeoff_ids": [
                    tradeoff.tradeoff_id
                    for tradeoff
                    in final_review.tradeoffs
                ],
 
                "assessment_ids": [
                    assessment.assessment_id
                    for assessment
                    in source.assessments
                ],
 
                "insight_ids": [
                    insight.insight_id
                    for insight
                    in source.insights
                ],
            },
        }
 
    @staticmethod
    def _review_item_to_dict(
        item,
    ) -> dict:
        """
        Convert one Step 34 review item into a compact
        JSON-safe representation.
        """
 
        return {
            "item_id": item.item_id,
            "category": item.category.value,
            "severity": item.severity.value,
            "title": item.title,
            "summary": item.summary,
            "consequence": item.consequence,
            "verification": item.verification,
            "source_assessment_ids": list(
                item.source_assessment_ids
            ),
            "source_insight_ids": list(
                item.source_insight_ids
            ),
        }
 
    @staticmethod
    def _tradeoff_to_dict(
        tradeoff,
    ) -> dict:
        """
        Convert one grounded Step 34 trade-off into a
        compact JSON-safe representation.
        """
 
        return {
            "tradeoff_id": tradeoff.tradeoff_id,
            "title": tradeoff.title,
            "severity": tradeoff.severity.value,
            "categories": [
                category.value
                for category
                in tradeoff.categories
            ],
            "benefit": tradeoff.benefit,
            "penalty": tradeoff.penalty,
            "guidance": tradeoff.guidance,
            "source_assessment_ids": list(
                tradeoff.source_assessment_ids
            ),
            "source_insight_ids": list(
                tradeoff.source_insight_ids
            ),
        }
 
    @staticmethod
    def _collect_review_item_ids(
        review,
    ) -> list[str]:
        """
        Return every top-level Step 34 review-item ID that
        may legitimately support a recommendation.
        """
 
        item_ids: list[str] = []
 
        for collection in (
            review.strengths,
            review.concerns,
            review.required_actions,
            review.validation_requirements,
        ):
            for item in collection:
                if item.item_id not in item_ids:
                    item_ids.append(
                        item.item_id
                    )
 
        return item_ids