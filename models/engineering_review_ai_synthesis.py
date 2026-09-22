"""
engineering_review_ai_synthesis.py
 
Structured output returned by the LLM engineering-review
synthesis layer.
 
This model contains communication and synthesis only.
 
It contains no authoritative engineering status and cannot
replace deterministic assessments, evidence, actions, or
validation requirements.
"""
 
from dataclasses import dataclass
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
@dataclass(frozen=True)
class EngineeringReviewAISectionSummary:
    """
    AI-generated explanation for one deterministic review
    section.
    """
 
    category: EngineeringCategory
 
    summary: str
 
    def __post_init__(
        self,
    ) -> None:
 
        if not isinstance(
            self.category,
            EngineeringCategory,
        ):
            raise ValueError(
                "'category' must be an "
                "EngineeringCategory value."
            )
 
        if not isinstance(
            self.summary,
            str,
        ):
            raise ValueError(
                "'summary' must be a string."
            )
 
        normalized_summary = (
            self.summary.strip()
        )
 
        if not normalized_summary:
            raise ValueError(
                "AI section summary cannot be empty."
            )
 
        object.__setattr__(
            self,
            "summary",
            normalized_summary,
        )
 
 
@dataclass(frozen=True)
class EngineeringReviewAITradeoff:
    """
    AI-synthesized cross-domain engineering trade-off.
 
    Every trade-off must reference deterministic source
    assessments and/or insights.
    """
 
    tradeoff_id: str
 
    title: str
 
    severity: EngineeringSeverity
 
    categories: tuple[
        EngineeringCategory,
        ...,
    ]
 
    benefit: str
 
    penalty: str
 
    guidance: str = ""
 
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
 
        if not isinstance(
            self.tradeoff_id,
            str,
        ):
            raise ValueError(
                "'tradeoff_id' must be a string."
            )
 
        normalized_id = (
            self.tradeoff_id.strip()
        )
 
        if not normalized_id:
            raise ValueError(
                "AI trade-off ID cannot be empty."
            )
 
        object.__setattr__(
            self,
            "tradeoff_id",
            normalized_id,
        )
 
        if not isinstance(
            self.title,
            str,
        ):
            raise ValueError(
                "'title' must be a string."
            )
 
        normalized_title = (
            self.title.strip()
        )
 
        if not normalized_title:
            raise ValueError(
                "AI trade-off title cannot be empty."
            )
 
        object.__setattr__(
            self,
            "title",
            normalized_title,
        )
 
        if not isinstance(
            self.severity,
            EngineeringSeverity,
        ):
            raise ValueError(
                "'severity' must be an "
                "EngineeringSeverity value."
            )
 
        if not isinstance(
            self.categories,
            tuple,
        ):
            raise ValueError(
                "'categories' must be a tuple."
            )
 
        if len(
            self.categories
        ) < 2:
            raise ValueError(
                "AI engineering trade-offs must reference "
                "at least two engineering categories."
            )
 
        if (
            len(set(self.categories))
            != len(self.categories)
        ):
            raise ValueError(
                "AI engineering trade-off categories "
                "must be unique."
            )
 
        for category in self.categories:
            if not isinstance(
                category,
                EngineeringCategory,
            ):
                raise ValueError(
                    "Every AI trade-off category must be "
                    "an EngineeringCategory value."
                )
 
        for field_name in (
            "benefit",
            "penalty",
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
 
            normalized_value = (
                value.strip()
            )
 
            if not normalized_value:
                raise ValueError(
                    f"AI trade-off {field_name} cannot "
                    "be empty."
                )
 
            object.__setattr__(
                self,
                field_name,
                normalized_value,
            )
 
        if not isinstance(
            self.guidance,
            str,
        ):
            raise ValueError(
                "'guidance' must be a string."
            )
 
        object.__setattr__(
            self,
            "guidance",
            self.guidance.strip(),
        )
 
        self._validate_source_ids(
            self.source_assessment_ids,
            "source_assessment_ids",
        )
 
        self._validate_source_ids(
            self.source_insight_ids,
            "source_insight_ids",
        )
 
        if (
            not self.source_assessment_ids
            and not self.source_insight_ids
        ):
            raise ValueError(
                "AI engineering trade-offs must reference "
                "at least one deterministic assessment or "
                "insight."
            )
 
    @staticmethod
    def _validate_source_ids(
        source_ids,
        field_name: str,
    ) -> None:
 
        if not isinstance(
            source_ids,
            tuple,
        ):
            raise ValueError(
                f"'{field_name}' must be a tuple."
            )
 
        if (
            len(set(source_ids))
            != len(source_ids)
        ):
            raise ValueError(
                f"IDs in '{field_name}' must be unique."
            )
 
        for source_id in source_ids:
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
 
 
@dataclass(frozen=True)
class EngineeringReviewAISynthesis:
    """
    Complete non-authoritative LLM synthesis output.
    """
 
    executive_summary: str
 
    section_summaries: tuple[
        EngineeringReviewAISectionSummary,
        ...,
    ] = ()
 
    tradeoffs: tuple[
        EngineeringReviewAITradeoff,
        ...,
    ] = ()
 
    def __post_init__(
        self,
    ) -> None:
 
        if not isinstance(
            self.executive_summary,
            str,
        ):
            raise ValueError(
                "'executive_summary' must be a string."
            )
 
        normalized_summary = (
            self.executive_summary.strip()
        )
 
        if not normalized_summary:
            raise ValueError(
                "AI engineering-review executive "
                "summary cannot be empty."
            )
 
        object.__setattr__(
            self,
            "executive_summary",
            normalized_summary,
        )
 
        if not isinstance(
            self.section_summaries,
            tuple,
        ):
            raise ValueError(
                "'section_summaries' must be a tuple."
            )
 
        seen_categories = set()
 
        for section in (
            self.section_summaries
        ):
            if not isinstance(
                section,
                EngineeringReviewAISectionSummary,
            ):
                raise ValueError(
                    "Every AI section summary must be an "
                    "EngineeringReviewAISectionSummary."
                )
 
            if (
                section.category
                in seen_categories
            ):
                raise ValueError(
                    "Duplicate AI section-summary "
                    "category: "
                    f"'{section.category.value}'."
                )
 
            seen_categories.add(
                section.category
            )
 
        if not isinstance(
            self.tradeoffs,
            tuple,
        ):
            raise ValueError(
                "'tradeoffs' must be a tuple."
            )
 
        seen_tradeoff_ids: set[str] = set()
 
        for tradeoff in self.tradeoffs:
            if not isinstance(
                tradeoff,
                EngineeringReviewAITradeoff,
            ):
                raise ValueError(
                    "Every AI trade-off must be an "
                    "EngineeringReviewAITradeoff."
                )
 
            if (
                tradeoff.tradeoff_id
                in seen_tradeoff_ids
            ):
                raise ValueError(
                    "Duplicate AI trade-off ID: "
                    f"'{tradeoff.tradeoff_id}'."
                )
 
            seen_tradeoff_ids.add(
                tradeoff.tradeoff_id
            )