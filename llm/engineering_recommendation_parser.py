"""
engineering_recommendation_parser.py
 
Parse and validate grounded AI recommendation synthesis.
 
The parser converts untrusted LLM output into strongly
validated EngineeringRecommendation objects.
 
No recommendation is accepted unless all referenced source
IDs exist in the grounded Step 35 payload.
"""
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_recommendation import (
    EngineeringRecommendation,
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
 
 
class EngineeringRecommendationParser:
    """
    Convert untrusted LLM recommendation output into
    validated engineering recommendation objects.
    """
 
    @classmethod
    def parse(
        cls,
        response: dict,
        payload: dict,
    ) -> tuple[
        EngineeringRecommendation,
        ...,
    ]:
        """
        Parse and ground one recommendation response.
        """
 
        if not isinstance(
            response,
            dict,
        ):
            raise ValueError(
                "Engineering recommendation response "
                "must be a dictionary."
            )
 
        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "'payload' must be a dictionary."
            )
 
        raw_recommendations = response.get(
            "recommendations"
        )
 
        if not isinstance(
            raw_recommendations,
            list,
        ):
            raise ValueError(
                "Engineering recommendation response must "
                "contain a 'recommendations' list."
            )
 
        valid_source_ids = payload.get(
            "valid_source_ids"
        )
 
        if not isinstance(
            valid_source_ids,
            dict,
        ):
            raise ValueError(
                "Recommendation payload is missing "
                "'valid_source_ids'."
            )
 
        valid_review_item_ids = cls._id_set(
            valid_source_ids,
            "review_item_ids",
        )
 
        valid_tradeoff_ids = cls._id_set(
            valid_source_ids,
            "tradeoff_ids",
        )
 
        valid_assessment_ids = cls._id_set(
            valid_source_ids,
            "assessment_ids",
        )
 
        valid_insight_ids = cls._id_set(
            valid_source_ids,
            "insight_ids",
        )
 
        recommendations: list[
            EngineeringRecommendation
        ] = []
 
        seen_recommendation_ids: set[str] = set()
 
        for raw_recommendation in raw_recommendations:
 
            if not isinstance(
                raw_recommendation,
                dict,
            ):
                raise ValueError(
                    "Every AI recommendation must be a "
                    "dictionary."
                )
 
            recommendation_id = cls._required_text(
                raw_recommendation,
                "recommendation_id",
            )
 
            if (
                recommendation_id
                in seen_recommendation_ids
            ):
                raise ValueError(
                    "Duplicate AI engineering "
                    "recommendation ID: "
                    f"'{recommendation_id}'."
                )
 
            seen_recommendation_ids.add(
                recommendation_id
            )
 
            source_review_item_ids = (
                cls._source_ids(
                    raw_recommendation,
                    "source_review_item_ids",
                    valid_review_item_ids,
                )
            )
 
            source_tradeoff_ids = (
                cls._source_ids(
                    raw_recommendation,
                    "source_tradeoff_ids",
                    valid_tradeoff_ids,
                )
            )
 
            source_assessment_ids = (
                cls._source_ids(
                    raw_recommendation,
                    "source_assessment_ids",
                    valid_assessment_ids,
                )
            )
 
            source_insight_ids = (
                cls._source_ids(
                    raw_recommendation,
                    "source_insight_ids",
                    valid_insight_ids,
                )
            )
 
            if not (
                source_review_item_ids
                or source_tradeoff_ids
                or source_assessment_ids
                or source_insight_ids
            ):
                raise ValueError(
                    "AI engineering recommendation "
                    f"'{recommendation_id}' has no valid "
                    "engineering source traceability."
                )
 
            recommendations.append(
                EngineeringRecommendation(
                    recommendation_id=(
                        recommendation_id
                    ),
 
                    recommendation_type=(
                        cls._enum_value(
                            raw_recommendation,
                            "recommendation_type",
                            EngineeringRecommendationType,
                        )
                    ),
 
                    priority=cls._enum_value(
                        raw_recommendation,
                        "priority",
                        EngineeringRecommendationPriority,
                    ),
 
                    category=cls._enum_value(
                        raw_recommendation,
                        "category",
                        EngineeringCategory,
                    ),
 
                    severity=cls._enum_value(
                        raw_recommendation,
                        "severity",
                        EngineeringSeverity,
                    ),
 
                    title=cls._required_text(
                        raw_recommendation,
                        "title",
                    ),
 
                    recommendation=(
                        cls._required_text(
                            raw_recommendation,
                            "recommendation",
                        )
                    ),
 
                    rationale=cls._required_text(
                        raw_recommendation,
                        "rationale",
                    ),
 
                    expected_effect=(
                        cls._optional_text(
                            raw_recommendation,
                            "expected_effect",
                        )
                    ),
 
                    verification=(
                        cls._optional_text(
                            raw_recommendation,
                            "verification",
                        )
                    ),
 
                    source_review_item_ids=(
                        source_review_item_ids
                    ),
 
                    source_tradeoff_ids=(
                        source_tradeoff_ids
                    ),
 
                    source_assessment_ids=(
                        source_assessment_ids
                    ),
 
                    source_insight_ids=(
                        source_insight_ids
                    ),
                )
            )
 
        return tuple(
            recommendations
        )
 
    @staticmethod
    def _id_set(
        registry: dict,
        field_name: str,
    ) -> set[str]:
        """
        Read one valid source-ID registry.
        """
 
        values = registry.get(
            field_name
        )
 
        if not isinstance(
            values,
            list,
        ):
            raise ValueError(
                "Recommendation payload source registry "
                f"'{field_name}' must be a list."
            )
 
        valid_ids: set[str] = set()
 
        for value in values:
            if not isinstance(
                value,
                str,
            ):
                raise ValueError(
                    "Recommendation payload source registry "
                    f"'{field_name}' contains a non-string "
                    "ID."
                )
 
            normalized = value.strip()
 
            if not normalized:
                raise ValueError(
                    "Recommendation payload source registry "
                    f"'{field_name}' contains an empty ID."
                )
 
            if normalized in valid_ids:
                raise ValueError(
                    "Recommendation payload source registry "
                    f"'{field_name}' contains duplicate ID "
                    f"'{normalized}'."
                )
 
            valid_ids.add(
                normalized
            )
 
        return valid_ids
 
    @staticmethod
    def _required_text(
        raw: dict,
        field_name: str,
    ) -> str:
        """
        Read one required non-empty text field.
        """
 
        value = raw.get(
            field_name
        )
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"Recommendation field '{field_name}' "
                "must be a string."
            )
 
        normalized = value.strip()
 
        if not normalized:
            raise ValueError(
                f"Recommendation field '{field_name}' "
                "cannot be empty."
            )
 
        return normalized
 
    @staticmethod
    def _optional_text(
        raw: dict,
        field_name: str,
    ) -> str:
        """
        Read one optional text field.
        """
 
        value = raw.get(
            field_name,
            "",
        )
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"Recommendation field '{field_name}' "
                "must be a string."
            )
 
        return value.strip()
 
    @staticmethod
    def _enum_value(
        raw: dict,
        field_name: str,
        enum_type,
    ):
        """
        Parse one controlled enum value.
        """
 
        value = raw.get(
            field_name
        )
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"Recommendation field '{field_name}' "
                "must be a string."
            )
 
        try:
            return enum_type(
                value.strip()
            )
 
        except ValueError as exc:
            raise ValueError(
                f"Invalid recommendation field "
                f"'{field_name}': '{value}'."
            ) from exc
 
    @staticmethod
    def _source_ids(
        raw: dict,
        field_name: str,
        valid_ids: set[str],
    ) -> tuple[str, ...]:
        """
        Parse one recommendation source-ID collection and
        reject invented IDs.
        """
 
        values = raw.get(
            field_name,
            [],
        )
 
        if not isinstance(
            values,
            list,
        ):
            raise ValueError(
                f"Recommendation field '{field_name}' "
                "must be a list."
            )
 
        normalized_ids: list[str] = []
 
        for value in values:
 
            if not isinstance(
                value,
                str,
            ):
                raise ValueError(
                    f"Recommendation field '{field_name}' "
                    "contains a non-string ID."
                )
 
            normalized = value.strip()
 
            if not normalized:
                raise ValueError(
                    f"Recommendation field '{field_name}' "
                    "contains an empty ID."
                )
 
            if normalized not in valid_ids:
                raise ValueError(
                    "AI recommendation referenced unknown "
                    f"{field_name}: '{normalized}'."
                )
 
            if normalized in normalized_ids:
                raise ValueError(
                    f"Recommendation field '{field_name}' "
                    f"contains duplicate ID '{normalized}'."
                )
 
            normalized_ids.append(
                normalized
            )
 
        return tuple(
            normalized_ids
        )