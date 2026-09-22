"""
engineering_recommendation_ai_synthesizer.py
 
Grounded AI synthesis for Step 35 engineering
recommendations.
 
This layer coordinates:
 
EngineeringReviewResult
    -> grounded recommendation payload
    -> configured LLM provider
    -> strict recommendation parser
    -> EngineeringRecommendation objects
 
The synthesizer performs no deterministic engineering
calculation and does not modify Step 34 engineering
evidence.
"""
 
from llm.base import (
    LLMProvider,
)
from llm.engineering_recommendation_parser import (
    EngineeringRecommendationParser,
)
from llm.engineering_recommendation_payload import (
    EngineeringRecommendationPayloadBuilder,
)
from llm.factory import (
    get_llm_provider,
)
from models.engineering_recommendation import (
    EngineeringRecommendation,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
 
 
class EngineeringRecommendationAISynthesizer:
    """
    Generate grounded engineering recommendations using
    the configured LLM provider.
    """
 
    @classmethod
    def synthesize(
        cls,
        review_result: EngineeringReviewResult,
        provider: LLMProvider | None = None,
    ) -> tuple[
        EngineeringRecommendation,
        ...,
    ]:
        """
        Generate and validate grounded AI recommendations.
 
        Parameters
        ----------
        review_result:
            Complete Step 34 Engineering Review result.
 
        provider:
            Optional explicit LLM provider. When omitted,
            the configured provider factory is used.
 
        Returns
        -------
        tuple[EngineeringRecommendation, ...]
            Strictly validated and source-grounded
            engineering recommendations.
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
                "'provider' must be an LLMProvider "
                "object or None."
            )
 
        payload = (
            EngineeringRecommendationPayloadBuilder
            .build(
                review_result
            )
        )
 
        active_provider = (
            provider
            if provider is not None
            else get_llm_provider()
        )
 
        response = (
            active_provider
            .synthesize_engineering_recommendations(
                payload
            )
        )
 
        return (
            EngineeringRecommendationParser
            .parse(
                response=response,
                payload=payload,
            )
        )