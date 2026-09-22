"""
engineering_review_ai_synthesizer.py
 
Provider-neutral grounded AI engineering-review synthesis.
 
Workflow:
 
EngineeringReviewSource
        +
Deterministic EngineeringReview
        ↓
Grounded payload
        ↓
LLM provider
        ↓
Grounded response parser
        ↓
AI synthesis
        ↓
Protected deterministic merge
        ↓
Enriched EngineeringReview
"""
 
from llm.base import LLMProvider
from llm.engineering_review_parser import (
    EngineeringReviewAIParser,
)
from llm.engineering_review_payload import (
    EngineeringReviewPayloadBuilder,
)
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
 
from core.engineering_review_ai_merger import (
    EngineeringReviewAIMerger,
)
 
 
class EngineeringReviewAISynthesizer:
    """
    Execute grounded provider-independent engineering
    review synthesis.
    """
 
    @staticmethod
    def synthesize(
        *,
        source: EngineeringReviewSource,
        deterministic_review: EngineeringReview,
        provider: LLMProvider,
    ) -> EngineeringReview:
        """
        Return the AI-enriched authoritative review.
        """
 
        if not isinstance(
            provider,
            LLMProvider,
        ):
            raise ValueError(
                "'provider' must be an LLMProvider object."
            )
 
        payload = (
            EngineeringReviewPayloadBuilder.build(
                source=source,
                deterministic_review=(
                    deterministic_review
                ),
            )
        )
 
        raw_synthesis = (
            provider.synthesize_engineering_review(
                payload
            )
        )
 
        ai_synthesis = (
            EngineeringReviewAIParser.parse(
                data=raw_synthesis,
                source=source,
                deterministic_review=(
                    deterministic_review
                ),
            )
        )
 
        return EngineeringReviewAIMerger.merge(
            deterministic_review=(
                deterministic_review
            ),
            ai_synthesis=ai_synthesis,
        )