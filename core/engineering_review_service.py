"""
engineering_review_service.py
 
High-level API for Step 34 — Engineering Review Synthesis.
 
Workflow:
 
EngineeringIntelligenceResult
        ↓
EngineeringReviewSourceBuilder
        ↓
Deterministic EngineeringReview
        ↓
Optional grounded AI synthesis
        ↓
EngineeringReviewResult
 
If AI synthesis is unavailable or invalid, the deterministic
review remains fully usable and may be returned as a safe
fallback.
 
Only AI-layer failures are eligible for fallback.
Deterministic source or review failures continue to raise.
"""
 
import logging
 
from core.engineering_review_ai_synthesizer import (
    EngineeringReviewAISynthesizer,
)
from core.engineering_review_source_builder import (
    EngineeringReviewSourceBuilder,
)
from core.engineering_review_synthesizer import (
    EngineeringReviewSynthesizer,
)
from llm.base import (
    LLMProvider,
)
from llm.factory import (
    get_llm_provider,
)
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
 
 
logger = logging.getLogger(
    __name__
)
 
 
class EngineeringReviewService:
    """
    Public orchestration boundary for complete engineering
    review generation.
    """
 
    @classmethod
    def build(
        cls,
        intelligence_result: EngineeringIntelligenceResult,
        *,
        use_ai: bool = True,
        provider: LLMProvider | None = None,
        fallback_to_deterministic: bool = True,
    ) -> EngineeringReviewResult:
        """
        Build one complete structured engineering review.
 
        Parameters
        ----------
        intelligence_result:
            Complete deterministic engineering-intelligence
            result.
 
        use_ai:
            Whether grounded AI communication synthesis
            should be attempted.
 
        provider:
            Optional explicit provider. When omitted and
            AI is requested, the configured LLM provider
            is obtained through the existing factory.
 
        fallback_to_deterministic:
            When True, an AI/provider/parsing failure returns
            the valid deterministic review instead of making
            Engineering Review unavailable.
        """
 
        if not isinstance(
            intelligence_result,
            EngineeringIntelligenceResult,
        ):
            raise ValueError(
                "'intelligence_result' must be an "
                "EngineeringIntelligenceResult object."
            )
 
        if not isinstance(
            use_ai,
            bool,
        ):
            raise ValueError(
                "'use_ai' must be a boolean."
            )
 
        if not isinstance(
            fallback_to_deterministic,
            bool,
        ):
            raise ValueError(
                "'fallback_to_deterministic' must be a "
                "boolean."
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
 
        source = (
            EngineeringReviewSourceBuilder.build(
                intelligence_result
            )
        )
 
        deterministic_review = (
            EngineeringReviewSynthesizer.synthesize(
                source
            )
        )
 
        if not use_ai:
            return EngineeringReviewResult(
                source=source,
                deterministic_review=(
                    deterministic_review
                ),
                review=deterministic_review,
                ai_requested=False,
                ai_enriched=False,
            )
 
        try:
            resolved_provider = (
                provider
                if provider is not None
                else get_llm_provider()
            )
 
            enriched_review = (
                EngineeringReviewAISynthesizer
                .synthesize(
                    source=source,
                    deterministic_review=(
                        deterministic_review
                    ),
                    provider=resolved_provider,
                )
            )
 
        except Exception as exc:
            if not fallback_to_deterministic:
                raise
 
            fallback_reason = (
                f"{type(exc).__name__}: {exc}"
            )
 
            logger.warning(
                "Engineering-review AI synthesis failed. "
                "Returning deterministic review. Reason: %s",
                fallback_reason,
            )
 
            return EngineeringReviewResult(
                source=source,
                deterministic_review=(
                    deterministic_review
                ),
                review=deterministic_review,
                ai_requested=True,
                ai_enriched=False,
                fallback_reason=fallback_reason,
            )
 
        return EngineeringReviewResult(
            source=source,
            deterministic_review=(
                deterministic_review
            ),
            review=enriched_review,
            ai_requested=True,
            ai_enriched=True,
        )