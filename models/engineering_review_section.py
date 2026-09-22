"""
engineering_review_section.py
 
Category-specific section within a structured engineering
review.
 
Each section consolidates deterministic engineering
insights and assessments belonging to one engineering
discipline.
"""
 
from dataclasses import dataclass
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_review_item import (
    EngineeringReviewItem,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
 
 
@dataclass(frozen=True)
class EngineeringReviewSection:
    """
    Structured review of one engineering category.
 
    Parameters
    ----------
    category:
        Engineering discipline represented by the section.
 
    status:
        Consolidated status for the category.
 
    summary:
        Concise synthesis of the category-specific
        engineering evidence.
 
    findings:
        Structured strengths, concerns, or observations
        associated with the category.
 
    source_assessment_ids:
        All deterministic assessment IDs considered by the
        section.
 
    source_insight_ids:
        All deterministic insight IDs considered by the
        section.
    """
 
    category: EngineeringCategory
 
    status: EngineeringReviewStatus
 
    summary: str
 
    findings: tuple[
        EngineeringReviewItem,
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
        Validate the structured review section.
        """
 
        if not isinstance(
            self.category,
            EngineeringCategory,
        ):
            raise ValueError(
                "'category' must be an "
                "EngineeringCategory value."
            )
 
        if not isinstance(
            self.status,
            EngineeringReviewStatus,
        ):
            raise ValueError(
                "'status' must be an "
                "EngineeringReviewStatus value."
            )
 
        if not isinstance(
            self.summary,
            str,
        ):
            raise ValueError(
                "'summary' must be a string."
            )
 
        normalized_summary = self.summary.strip()
 
        if not normalized_summary:
            raise ValueError(
                "Engineering review section summary cannot "
                "be empty."
            )
 
        object.__setattr__(
            self,
            "summary",
            normalized_summary,
        )
 
        if not isinstance(
            self.findings,
            tuple,
        ):
            raise ValueError(
                "'findings' must be a tuple."
            )
 
        seen_item_ids: set[str] = set()
 
        for finding in self.findings:
            if not isinstance(
                finding,
                EngineeringReviewItem,
            ):
                raise ValueError(
                    "Every section finding must be an "
                    "EngineeringReviewItem object."
                )
 
            if (
                finding.category
                != self.category
            ):
                raise ValueError(
                    "Every section finding must use the "
                    "same engineering category as its "
                    "section."
                )
 
            if finding.item_id in seen_item_ids:
                raise ValueError(
                    (
                        "Duplicate engineering review item "
                        f"ID: '{finding.item_id}'."
                    )
                )
 
            seen_item_ids.add(
                finding.item_id
            )
 
        normalized_assessment_ids = (
            self._validate_source_ids(
                source_ids=(
                    self.source_assessment_ids
                ),
                field_name=(
                    "source_assessment_ids"
                ),
            )
        )
 
        object.__setattr__(
            self,
            "source_assessment_ids",
            normalized_assessment_ids,
        )
 
        normalized_insight_ids = (
            self._validate_source_ids(
                source_ids=(
                    self.source_insight_ids
                ),
                field_name="source_insight_ids",
            )
        )
 
        object.__setattr__(
            self,
            "source_insight_ids",
            normalized_insight_ids,
        )
 
    @staticmethod
    def _validate_source_ids(
        source_ids,
        field_name: str,
    ) -> tuple[str, ...]:
        """
        Validate and normalize section-level source IDs.
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
                    (
                        f"Every ID in '{field_name}' must "
                        "be a string."
                    )
                )
 
            normalized_id = source_id.strip()
 
            if not normalized_id:
                raise ValueError(
                    (
                        f"IDs in '{field_name}' cannot be "
                        "empty."
                    )
                )
 
            normalized_ids.append(
                normalized_id
            )
 
        if (
            len(set(normalized_ids))
            != len(normalized_ids)
        ):
            raise ValueError(
                (
                    f"IDs in '{field_name}' must be "
                    "unique."
                )
            )
 
        return tuple(
            normalized_ids
        )
 
    @property
    def has_findings(
        self,
    ) -> bool:
        """
        Return True when the section contains findings.
        """
 
        return bool(
            self.findings
        )