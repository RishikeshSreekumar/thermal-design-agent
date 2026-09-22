"""
engineering_recommendation_result.py
 
Canonical structured output of the Recommendation Engine.
 
The result preserves the complete Step 34
EngineeringReviewResult together with the ordered
recommendation population generated from it.
 
Recommendation generation does not replace or modify the
authoritative engineering review.
"""
 
from dataclasses import dataclass
 
from models.engineering_recommendation import (
    EngineeringRecommendation,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
 
 
@dataclass(frozen=True)
class EngineeringRecommendationResult:
    """
    Complete structured recommendation result.
    """
 
    review_result: EngineeringReviewResult
 
    recommendations: tuple[
        EngineeringRecommendation,
        ...,
    ] = ()
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the recommendation result.
        """
 
        if not isinstance(
            self.review_result,
            EngineeringReviewResult,
        ):
            raise ValueError(
                "'review_result' must be an "
                "EngineeringReviewResult object."
            )
 
        if not isinstance(
            self.recommendations,
            tuple,
        ):
            raise ValueError(
                "'recommendations' must be a tuple."
            )
 
        seen_ids: set[str] = set()
 
        for recommendation in (
            self.recommendations
        ):
            if not isinstance(
                recommendation,
                EngineeringRecommendation,
            ):
                raise ValueError(
                    "Every recommendation must be an "
                    "EngineeringRecommendation object."
                )
 
            if (
                recommendation.recommendation_id
                in seen_ids
            ):
                raise ValueError(
                    "Duplicate engineering "
                    "recommendation ID: "
                    f"'{recommendation.recommendation_id}'."
                )
 
            seen_ids.add(
                recommendation.recommendation_id
            )
 
    @property
    def has_recommendations(
        self,
    ) -> bool:
        """
        Return True when at least one recommendation exists.
        """
 
        return bool(
            self.recommendations
        )
 
    @property
    def recommendation_count(
        self,
    ) -> int:
        """
        Return the number of generated recommendations.
        """
 
        return len(
            self.recommendations
        )
 
    @property
    def highest_priority(
        self,
    ):
        """
        Return the highest priority represented in the
        recommendation population, or None when empty.
 
        Ordering is explicit here rather than relying on
        Enum declaration order.
        """
 
        if not self.recommendations:
            return None
 
        from models.engineering_recommendation_priority import (
            EngineeringRecommendationPriority,
        )
 
        priority_rank = {
            EngineeringRecommendationPriority.CRITICAL: 0,
            EngineeringRecommendationPriority.HIGH: 1,
            EngineeringRecommendationPriority.MEDIUM: 2,
            EngineeringRecommendationPriority.LOW: 3,
        }
 
        return min(
            (
                recommendation.priority
                for recommendation
                in self.recommendations
            ),
            key=priority_rank.__getitem__,
        )
 
    def recommendations_for_priority(
        self,
        priority,
    ) -> tuple[
        EngineeringRecommendation,
        ...,
    ]:
        """
        Return recommendations matching one priority.
        """
 
        from models.engineering_recommendation_priority import (
            EngineeringRecommendationPriority,
        )
 
        if not isinstance(
            priority,
            EngineeringRecommendationPriority,
        ):
            raise ValueError(
                "'priority' must be an "
                "EngineeringRecommendationPriority value."
            )
 
        return tuple(
            recommendation
            for recommendation
            in self.recommendations
            if recommendation.priority
            == priority
        )
 
    def recommendations_for_category(
        self,
        category,
    ) -> tuple[
        EngineeringRecommendation,
        ...,
    ]:
        """
        Return recommendations matching one engineering
        category.
        """
 
        from models.engineering_category import (
            EngineeringCategory,
        )
 
        if not isinstance(
            category,
            EngineeringCategory,
        ):
            raise ValueError(
                "'category' must be an "
                "EngineeringCategory value."
            )
 
        return tuple(
            recommendation
            for recommendation
            in self.recommendations
            if recommendation.category
            == category
        )