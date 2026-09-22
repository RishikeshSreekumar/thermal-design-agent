"""
engineering_review_parser.py
 
Parses and grounds structured LLM engineering-review output.
 
The parser validates:
 
- response structure;
- category values;
- severity values;
- section-category availability;
- source assessment IDs;
- source insight IDs.
 
It performs no engineering calculation.
"""
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_review_ai_synthesis import (
    EngineeringReviewAISynthesis,
    EngineeringReviewAISectionSummary,
    EngineeringReviewAITradeoff,
)
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
class EngineeringReviewAIParser:
    """
    Convert raw provider output into validated grounded AI
    engineering-review synthesis.
    """
 
    @classmethod
    def parse(
        cls,
        *,
        data: dict,
        source: EngineeringReviewSource,
        deterministic_review: EngineeringReview,
    ) -> EngineeringReviewAISynthesis:
        """
        Parse and validate one provider response.
        """
 
        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "Engineering-review AI response must be a "
                "dictionary."
            )
 
        if not isinstance(
            source,
            EngineeringReviewSource,
        ):
            raise ValueError(
                "'source' must be an "
                "EngineeringReviewSource object."
            )
 
        if not isinstance(
            deterministic_review,
            EngineeringReview,
        ):
            raise ValueError(
                "'deterministic_review' must be an "
                "EngineeringReview object."
            )
 
        executive_summary = data.get(
            "executive_summary"
        )
 
        raw_sections = data.get(
            "section_summaries",
            [],
        )
 
        raw_tradeoffs = data.get(
            "tradeoffs",
            [],
        )
 
        if not isinstance(
            raw_sections,
            list,
        ):
            raise ValueError(
                "'section_summaries' must be a list."
            )
 
        if not isinstance(
            raw_tradeoffs,
            list,
        ):
            raise ValueError(
                "'tradeoffs' must be a list."
            )
 
        available_categories = {
            section.category
            for section
            in deterministic_review.sections
        }
 
        section_summaries = tuple(
            cls._parse_section(
                raw_section=raw_section,
                available_categories=(
                    available_categories
                ),
            )
            for raw_section in raw_sections
        )
 
        tradeoffs = tuple(
            cls._parse_tradeoff(
                raw_tradeoff=raw_tradeoff,
                source=source,
                available_categories=(
                    available_categories
                ),
            )
            for raw_tradeoff in raw_tradeoffs
        )
 
        return EngineeringReviewAISynthesis(
            executive_summary=(
                executive_summary
            ),
            section_summaries=(
                section_summaries
            ),
            tradeoffs=tradeoffs,
        )
 
    @classmethod
    def _parse_section(
        cls,
        *,
        raw_section,
        available_categories: set[
            EngineeringCategory
        ],
    ) -> EngineeringReviewAISectionSummary:
        """
        Parse one AI-generated section summary.
        """
 
        if not isinstance(
            raw_section,
            dict,
        ):
            raise ValueError(
                "Every AI section summary must be a "
                "dictionary."
            )
 
        category = cls._parse_category(
            raw_section.get(
                "category"
            )
        )
 
        if (
            category
            not in available_categories
        ):
            raise ValueError(
                "AI section summary references category "
                "not present in deterministic review: "
                f"'{category.value}'."
            )
 
        return EngineeringReviewAISectionSummary(
            category=category,
            summary=raw_section.get(
                "summary"
            ),
        )
 
    @classmethod
    def _parse_tradeoff(
        cls,
        *,
        raw_tradeoff,
        source: EngineeringReviewSource,
        available_categories: set[
            EngineeringCategory
        ],
    ) -> EngineeringReviewAITradeoff:
        """
        Parse one grounded AI-generated trade-off.
        """
 
        if not isinstance(
            raw_tradeoff,
            dict,
        ):
            raise ValueError(
                "Every AI trade-off must be a dictionary."
            )
 
        raw_categories = raw_tradeoff.get(
            "categories",
            [],
        )
 
        if not isinstance(
            raw_categories,
            list,
        ):
            raise ValueError(
                "AI trade-off 'categories' must be a list."
            )
 
        categories = tuple(
            cls._parse_category(
                category
            )
            for category
            in raw_categories
        )
 
        for category in categories:
            if (
                category
                not in available_categories
            ):
                raise ValueError(
                    "AI trade-off references category not "
                    "present in deterministic review: "
                    f"'{category.value}'."
                )
 
        assessment_ids = (
            cls._parse_id_list(
                raw_tradeoff.get(
                    "source_assessment_ids",
                    [],
                ),
                field_name=(
                    "source_assessment_ids"
                ),
            )
        )
 
        insight_ids = (
            cls._parse_id_list(
                raw_tradeoff.get(
                    "source_insight_ids",
                    [],
                ),
                field_name=(
                    "source_insight_ids"
                ),
            )
        )
 
        for assessment_id in assessment_ids:
            if (
                assessment_id
                not in source.assessment_index
            ):
                raise ValueError(
                    "AI trade-off references unknown "
                    "assessment ID: "
                    f"'{assessment_id}'."
                )
 
        for insight_id in insight_ids:
            if (
                insight_id
                not in source.insight_index
            ):
                raise ValueError(
                    "AI trade-off references unknown "
                    "insight ID: "
                    f"'{insight_id}'."
                )
 
        return EngineeringReviewAITradeoff(
            tradeoff_id=raw_tradeoff.get(
                "tradeoff_id"
            ),
            title=raw_tradeoff.get(
                "title"
            ),
            severity=cls._parse_severity(
                raw_tradeoff.get(
                    "severity"
                )
            ),
            categories=categories,
            benefit=raw_tradeoff.get(
                "benefit"
            ),
            penalty=raw_tradeoff.get(
                "penalty"
            ),
            guidance=raw_tradeoff.get(
                "guidance",
                "",
            ),
            source_assessment_ids=(
                assessment_ids
            ),
            source_insight_ids=(
                insight_ids
            ),
        )
 
    @staticmethod
    def _parse_category(
        value,
    ) -> EngineeringCategory:
        """
        Parse one engineering-category value.
        """
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "Engineering category must be a string."
            )
 
        try:
            return EngineeringCategory(
                value.strip()
            )
 
        except ValueError as exc:
            raise ValueError(
                "Unknown engineering category: "
                f"'{value}'."
            ) from exc
 
    @staticmethod
    def _parse_severity(
        value,
    ) -> EngineeringSeverity:
        """
        Parse one engineering-severity value.
        """
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "Engineering severity must be a string."
            )
 
        try:
            return EngineeringSeverity(
                value.strip()
            )
 
        except ValueError as exc:
            raise ValueError(
                "Unknown engineering severity: "
                f"'{value}'."
            ) from exc
 
    @staticmethod
    def _parse_id_list(
        value,
        *,
        field_name: str,
    ) -> tuple[str, ...]:
        """
        Parse one provider ID list.
        """
 
        if not isinstance(
            value,
            list,
        ):
            raise ValueError(
                f"'{field_name}' must be a list."
            )
 
        normalized_ids: list[str] = []
 
        for source_id in value:
            if (
                not isinstance(
                    source_id,
                    str,
                )
                or not source_id.strip()
            ):
                raise ValueError(
                    f"Every ID in '{field_name}' must be "
                    "a non-empty string."
                )
 
            normalized_ids.append(
                source_id.strip()
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