"""
engineering_application_result.py
 
Canonical end-to-end application result for the
Thermal Design Agent.
 
This aggregate preserves the outputs produced by the
existing engineering workflow without recalculating,
rewriting, or flattening them.
"""
 
from dataclasses import dataclass
from pathlib import Path
 
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from models.engineering_report import (
    EngineeringReport,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
from models.geometry import (
    GeometryParameters,
)
from models.optimization_result import (
    OptimizationResult,
)
from models.requirements import (
    EngineeringRequirements,
)
 
 
@dataclass(frozen=True)
class EngineeringApplicationResult:
    """
    Complete output of one engineering design run.
    """
 
    requirements: EngineeringRequirements
 
    optimization_result: OptimizationResult
 
    intelligence_result: EngineeringIntelligenceResult
 
    review_result: EngineeringReviewResult
 
    recommendation_result: EngineeringRecommendationResult
 
    report: EngineeringReport
 
    geometry: GeometryParameters
 
    step_file: Path
 
    def __post_init__(
        self,
    ) -> None:
 
        if not isinstance(
            self.requirements,
            EngineeringRequirements,
        ):
            raise ValueError(
                "'requirements' must be an "
                "EngineeringRequirements object."
            )
 
        if not isinstance(
            self.optimization_result,
            OptimizationResult,
        ):
            raise ValueError(
                "'optimization_result' must be an "
                "OptimizationResult object."
            )
 
        if not isinstance(
            self.intelligence_result,
            EngineeringIntelligenceResult,
        ):
            raise ValueError(
                "'intelligence_result' must be an "
                "EngineeringIntelligenceResult object."
            )
 
        if not isinstance(
            self.review_result,
            EngineeringReviewResult,
        ):
            raise ValueError(
                "'review_result' must be an "
                "EngineeringReviewResult object."
            )
 
        if not isinstance(
            self.recommendation_result,
            EngineeringRecommendationResult,
        ):
            raise ValueError(
                "'recommendation_result' must be an "
                "EngineeringRecommendationResult object."
            )
 
        if not isinstance(
            self.report,
            EngineeringReport,
        ):
            raise ValueError(
                "'report' must be an "
                "EngineeringReport object."
            )
 
        if not isinstance(
            self.geometry,
            GeometryParameters,
        ):
            raise ValueError(
                "'geometry' must be a "
                "GeometryParameters object."
            )
 
        if not isinstance(
            self.step_file,
            Path,
        ):
            raise ValueError(
                "'step_file' must be a pathlib.Path."
            )
 
        # --------------------------------------------------
        # Traceability / object-identity checks
        # --------------------------------------------------
 
        if (
            self.intelligence_result.context.requirements
            is not self.requirements
        ):
            raise ValueError(
                "Application-result requirements must match "
                "the intelligence context."
            )
 
        if (
            self.intelligence_result
            .context
            .optimization_result
            is not self.optimization_result
        ):
            raise ValueError(
                "Application-result optimization result must "
                "match the intelligence context."
            )
 
        if (
            self.review_result.source.intelligence_result
            is not self.intelligence_result
        ):
            raise ValueError(
                "Application-result review must preserve "
                "the intelligence result."
            )
 
        if (
            self.recommendation_result.review_result
            is not self.review_result
        ):
            raise ValueError(
                "Application-result recommendations must "
                "preserve the review result."
            )
 
        if (
            self.report.source
            is not self.recommendation_result
        ):
            raise ValueError(
                "Application-result report must preserve "
                "the recommendation result."
            )
 
    @property
    def selected_candidate(
        self,
    ):
        """
        Return the uniquely selected candidate, if one exists.
        """
 
        return (
            self.optimization_result
            .selected_candidate
        )
 
    @property
    def engineering_status(
        self,
    ):
        """
        Return the authoritative engineering-review status.
        """
 
        return self.review_result.review.status
 
    @property
    def has_ai_review(
        self,
    ) -> bool:
        """
        Return whether the engineering review was AI enriched.
        """
 
        return self.review_result.ai_enriched
 
    @property
    def has_recommendations(
        self,
    ) -> bool:
        """
        Return whether grounded recommendations exist.
        """
 
        return (
            self.recommendation_result
            .has_recommendations
        )