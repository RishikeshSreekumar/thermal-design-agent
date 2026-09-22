"""
engineering_recommendation_service.py
 
High-level API for Step 35 — Engineering Recommendation
Generation.
 
Workflow:
 
EngineeringReviewResult
        ↓
Grounded AI Recommendation Synthesis
        ↓
EngineeringRecommendationResult
 
The service preserves the complete authoritative Step 34
engineering review and packages the validated recommendation
population generated from it.
 
This layer performs no engineering calculation and does not
modify the deterministic engineering review.
"""

import logging 
from core.engineering_recommendation_ai_synthesizer import (
    EngineeringRecommendationAISynthesizer,
)
from llm.base import (
    LLMProvider,
)
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
 
logger = logging.getLogger(
    __name__
) 
class EngineeringRecommendationService:
    """
    Public orchestration boundary for complete engineering
    recommendation generation.
    """
 
    @classmethod
    def build(
        cls,
        review_result: EngineeringReviewResult,
        *,
        provider: LLMProvider | None = None,
        fallback_to_empty: bool = True,
    ) -> EngineeringRecommendationResult:
        """
        Build one complete structured engineering
        recommendation result.
 
        Parameters
        ----------
        review_result:
            Complete Step 34 EngineeringReviewResult.
 
        provider:
            Optional explicit LLM provider. When omitted,
            the configured provider is resolved by the
            recommendation AI synthesizer.

        fallback_to_empty:
            When True, an AI/provider/parsing failure
            returns a valid recommendation result with no
            AI recommendations. The authoritative
            engineering review remains unchanged.
        """
        
 
        if not isinstance(
            review_result,
            EngineeringReviewResult,
        ):
            raise ValueError(
                "'review_result' must be an "
                "EngineeringReviewResult object."
            )
 
        if (
            provider is not None
            and not isinstance(
                provider,
                LLMProvider,
            )
        ):
            raise ValueError(
                "'provider' must be an LLMProvider object "
                "or None."
            )
        
        if not isinstance(
            fallback_to_empty,
            bool,
        ):
            raise ValueError(
                "'fallback_to_empty' must be a boolean."
            )
 
        try:
            recommendations = (
                EngineeringRecommendationAISynthesizer
                .synthesize(
                    review_result=review_result,
                    provider=provider,
                )
            )
        except Exception as exc:
            if not fallback_to_empty:
                raise
            logger.warning(
                "Engineering-recommendation AI synthesis "
                "failed. Continuing without AI "
                "recommendations. Reason: %s: %s",
                type(exc).__name__,
                exc,
            )
            recommendations = ()
 
        return EngineeringRecommendationResult(
            review_result=review_result,
            recommendations=recommendations,
        )