"""
engineering_recommendation.py
 
Immutable structured engineering recommendation.
 
A recommendation must originate from existing engineering
review evidence. The model does not perform calculations,
evaluate engineering rules, or determine recommendation
priority.
 
Every recommendation remains traceable to the Step 34
Engineering Review and ultimately to deterministic
engineering assessments and/or insights.
"""
 
from dataclasses import dataclass
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_recommendation_priority import (
    EngineeringRecommendationPriority,
)
from models.engineering_recommendation_type import (
    EngineeringRecommendationType,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
@dataclass(frozen=True)
class EngineeringRecommendation:
    """
    One prioritised and traceable engineering
    recommendation.
 
    Parameters
    ----------
    recommendation_id:
        Stable identifier unique within the recommendation
        result.
 
    recommendation_type:
        Functional recommendation classification.
 
    priority:
        Deterministically assigned action priority.
 
    category:
        Primary engineering category associated with the
        recommendation.
 
    severity:
        Severity inherited from the engineering evidence
        supporting the recommendation.
 
    title:
        Short recommendation title.
 
    recommendation:
        Specific engineering action being recommended.
 
    rationale:
        Deterministic explanation of why the recommendation
        exists.
 
    expected_effect:
        Optional supported description of the engineering
        outcome expected from addressing the recommendation.
 
    verification:
        Optional method for confirming completion or
        effectiveness.
 
    source_review_item_ids:
        Step 34 review-item IDs from which this
        recommendation originated.
 
    source_tradeoff_ids:
        Step 34 trade-off IDs supporting the recommendation.
 
    source_assessment_ids:
        Deterministic assessment IDs supporting the
        recommendation.
 
    source_insight_ids:
        Deterministic insight IDs supporting the
        recommendation.
    """
 
    recommendation_id: str
 
    recommendation_type: (
        EngineeringRecommendationType
    )
 
    priority: EngineeringRecommendationPriority
 
    category: EngineeringCategory
 
    severity: EngineeringSeverity
 
    title: str
 
    recommendation: str
 
    rationale: str
 
    expected_effect: str = ""
 
    verification: str = ""
 
    source_review_item_ids: tuple[
        str,
        ...,
    ] = ()
 
    source_tradeoff_ids: tuple[
        str,
        ...,
    ] = ()
 
    source_assessment_ids: tuple[
        str,
        ...,
    ] = ()
 
    source_insight_ids: tuple[
        str,
        ...,
    ] = ()
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate one recommendation.
        """
 
        normalized_id = (
            self._normalize_required_text(
                self.recommendation_id,
                "recommendation_id",
            )
        )
 
        object.__setattr__(
            self,
            "recommendation_id",
            normalized_id,
        )
 
        if not isinstance(
            self.recommendation_type,
            EngineeringRecommendationType,
        ):
            raise ValueError(
                "'recommendation_type' must be an "
                "EngineeringRecommendationType value."
            )
 
        if not isinstance(
            self.priority,
            EngineeringRecommendationPriority,
        ):
            raise ValueError(
                "'priority' must be an "
                "EngineeringRecommendationPriority value."
            )
 
        if not isinstance(
            self.category,
            EngineeringCategory,
        ):
            raise ValueError(
                "'category' must be an "
                "EngineeringCategory value."
            )
 
        if not isinstance(
            self.severity,
            EngineeringSeverity,
        ):
            raise ValueError(
                "'severity' must be an "
                "EngineeringSeverity value."
            )
 
        for field_name in (
            "title",
            "recommendation",
            "rationale",
        ):
            normalized_value = (
                self._normalize_required_text(
                    getattr(
                        self,
                        field_name,
                    ),
                    field_name,
                )
            )
 
            object.__setattr__(
                self,
                field_name,
                normalized_value,
            )
 
        for field_name in (
            "expected_effect",
            "verification",
        ):
            value = getattr(
                self,
                field_name,
            )
 
            if not isinstance(
                value,
                str,
            ):
                raise ValueError(
                    f"'{field_name}' must be a string."
                )
 
            object.__setattr__(
                self,
                field_name,
                value.strip(),
            )
 
        for field_name in (
            "source_review_item_ids",
            "source_tradeoff_ids",
            "source_assessment_ids",
            "source_insight_ids",
        ):
            normalized_ids = (
                self._validate_source_ids(
                    getattr(
                        self,
                        field_name,
                    ),
                    field_name,
                )
            )
 
            object.__setattr__(
                self,
                field_name,
                normalized_ids,
            )
 
        if not self.is_traceable:
            raise ValueError(
                "Engineering recommendation must reference "
                "at least one review item, trade-off, "
                "assessment, or insight."
            )
 
    @staticmethod
    def _normalize_required_text(
        value,
        field_name: str,
    ) -> str:
        """
        Validate and normalize one required text field.
        """
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"'{field_name}' must be a string."
            )
 
        normalized_value = value.strip()
 
        if not normalized_value:
            raise ValueError(
                f"'{field_name}' cannot be empty."
            )
 
        return normalized_value
 
    @staticmethod
    def _validate_source_ids(
        source_ids,
        field_name: str,
    ) -> tuple[str, ...]:
        """
        Validate one traceability-ID collection.
        """
 
        if not isinstance(
            source_ids,
            tuple,
        ):
            raise ValueError(
                f"'{field_name}' must be a tuple."
            )
 
        normalized_ids: list[str] = []
 
        for source_id in source_ids:
            if not isinstance(
                source_id,
                str,
            ):
                raise ValueError(
                    f"Every ID in '{field_name}' must "
                    "be a string."
                )
 
            normalized_id = (
                source_id.strip()
            )
 
            if not normalized_id:
                raise ValueError(
                    f"Every ID in '{field_name}' must "
                    "be non-empty."
                )
 
            normalized_ids.append(
                normalized_id
            )
 
        if (
            len(normalized_ids)
            != len(set(normalized_ids))
        ):
            raise ValueError(
                f"IDs in '{field_name}' must be unique."
            )
 
        return tuple(
            normalized_ids
        )
 
    @property
    def is_traceable(
        self,
    ) -> bool:
        """
        Return True when the recommendation references
        existing review or deterministic engineering
        evidence.
        """
 
        return bool(
            self.source_review_item_ids
            or self.source_tradeoff_ids
            or self.source_assessment_ids
            or self.source_insight_ids
        )
 
    @property
    def requires_immediate_attention(
        self,
    ) -> bool:
        """
        Return True for the highest recommendation
        priority.
        """
 
        return (
            self.priority
            == EngineeringRecommendationPriority.CRITICAL
        )
 
    @property
    def has_expected_effect(
        self,
    ) -> bool:
        """
        Return True when an expected engineering effect is
        recorded.
        """
 
        return bool(
            self.expected_effect
        )
 
    @property
    def has_verification(
        self,
    ) -> bool:
        """
        Return True when a verification method is recorded.
        """
 
        return bool(
            self.verification
        )