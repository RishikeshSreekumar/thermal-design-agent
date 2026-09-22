"""
engineering_review_source_builder.py
 
Builds the validated deterministic source package used by
engineering-review synthesis.
 
The builder performs no engineering calculation, rule
evaluation, summarization, or LLM operation.
"""
 
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
 
 
class EngineeringReviewSourceBuilder:
    """
    Build a traceable and lossless review source from the
    complete engineering-intelligence result.
    """
 
    @staticmethod
    def build(
        intelligence_result: (
            EngineeringIntelligenceResult
        ),
    ) -> EngineeringReviewSource:
        """
        Build the review source package.
 
        The original context, insights, and assessments are
        preserved by object identity. No source content is
        copied, rewritten, summarized, or discarded.
        """
 
        if not isinstance(
            intelligence_result,
            EngineeringIntelligenceResult,
        ):
            raise ValueError(
                "'intelligence_result' must be an "
                "EngineeringIntelligenceResult object."
            )
 
        insight_index = (
            EngineeringReviewSourceBuilder
            ._build_insight_index(
                intelligence_result
            )
        )
 
        assessment_index = (
            EngineeringReviewSourceBuilder
            ._build_assessment_index(
                intelligence_result
            )
        )
 
        assessed_id_set = {
            source_insight_id
            for assessment
            in intelligence_result.assessments
            for source_insight_id
            in assessment.source_insight_ids
        }
 
        assessed_insight_ids = tuple(
            insight.insight_id
            for insight
            in intelligence_result.insights
            if insight.insight_id
            in assessed_id_set
        )
 
        unassessed_insight_ids = tuple(
            insight.insight_id
            for insight
            in intelligence_result.insights
            if insight.insight_id
            not in assessed_id_set
        )
 
        return EngineeringReviewSource(
            intelligence_result=(
                intelligence_result
            ),
            insight_index=insight_index,
            assessment_index=assessment_index,
            assessed_insight_ids=(
                assessed_insight_ids
            ),
            unassessed_insight_ids=(
                unassessed_insight_ids
            ),
        )
 
    @staticmethod
    def _build_insight_index(
        intelligence_result: (
            EngineeringIntelligenceResult
        ),
    ) -> dict:
        """
        Build the stable insight-ID lookup and reject
        duplicate source insight IDs.
        """
 
        insight_index = {}
 
        for insight in intelligence_result.insights:
            if (
                insight.insight_id
                in insight_index
            ):
                raise ValueError(
                    "Duplicate engineering insight ID in "
                    "review source: "
                    f"'{insight.insight_id}'."
                )
 
            insight_index[
                insight.insight_id
            ] = insight
 
        return insight_index
 
    @staticmethod
    def _build_assessment_index(
        intelligence_result: (
            EngineeringIntelligenceResult
        ),
    ) -> dict:
        """
        Build the stable assessment-ID lookup and reject
        duplicate source assessment IDs.
        """
 
        assessment_index = {}
 
        for assessment in (
            intelligence_result.assessments
        ):
            if (
                assessment.assessment_id
                in assessment_index
            ):
                raise ValueError(
                    "Duplicate engineering assessment ID "
                    "in review source: "
                    f"'{assessment.assessment_id}'."
                )
 
            assessment_index[
                assessment.assessment_id
            ] = assessment
 
        return assessment_index