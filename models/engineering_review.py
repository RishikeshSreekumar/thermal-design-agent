"""
engineering_review.py
 
Immutable structured output of engineering review
synthesis.
 
The review consolidates the complete deterministic
engineering-intelligence result into a readable,
category-organized, and traceable engineering artifact.
 
The review does not replace the underlying deterministic
context, insights, assessments, evidence, or calculations.
"""
 
from dataclasses import dataclass
 
from models.engineering_review_item import (
    EngineeringReviewItem,
)
from models.engineering_review_section import (
    EngineeringReviewSection,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
from models.engineering_tradeoff import (
    EngineeringTradeoff,
)
 
 
@dataclass(frozen=True)
class EngineeringReview:
    """
    Complete structured engineering review.
 
    Parameters
    ----------
    status:
        Consolidated overall engineering-review status.
 
    executive_summary:
        Concise high-level synthesis of the current design.
 
    strengths:
        Traceable positive design findings.
 
    concerns:
        Traceable engineering concerns.
 
    sections:
        Category-specific review sections.
 
    tradeoffs:
        Cross-category engineering trade-offs.
 
    required_actions:
        Actions supported by the current deterministic
        engineering evidence.
 
    validation_requirements:
        Testing, simulation, supplier confirmation, or
        other validation required before progression.
 
    source_assessment_ids:
        Complete deterministic assessment population
        considered during review synthesis.
 
    source_insight_ids:
        Complete deterministic insight population
        considered during review synthesis.
    """
 
    status: EngineeringReviewStatus
 
    executive_summary: str
 
    strengths: tuple[
        EngineeringReviewItem,
        ...,
    ] = ()
 
    concerns: tuple[
        EngineeringReviewItem,
        ...,
    ] = ()
 
    sections: tuple[
        EngineeringReviewSection,
        ...,
    ] = ()
 
    tradeoffs: tuple[
        EngineeringTradeoff,
        ...,
    ] = ()
 
    required_actions: tuple[
        EngineeringReviewItem,
        ...,
    ] = ()
 
    validation_requirements: tuple[
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
        Validate the complete engineering review.
        """
 
        if not isinstance(
            self.status,
            EngineeringReviewStatus,
        ):
            raise ValueError(
                "'status' must be an "
                "EngineeringReviewStatus value."
            )
 
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
                "Engineering review executive summary "
                "cannot be empty."
            )
 
        object.__setattr__(
            self,
            "executive_summary",
            normalized_summary,
        )
 
        self._validate_review_items(
            items=self.strengths,
            field_name="strengths",
        )
 
        self._validate_review_items(
            items=self.concerns,
            field_name="concerns",
        )
 
        self._validate_review_items(
            items=self.required_actions,
            field_name="required_actions",
        )
 
        self._validate_review_items(
            items=(
                self.validation_requirements
            ),
            field_name=(
                "validation_requirements"
            ),
        )
 
        if not isinstance(
            self.sections,
            tuple,
        ):
            raise ValueError(
                "'sections' must be a tuple."
            )
 
        seen_categories = set()
 
        for section in self.sections:
            if not isinstance(
                section,
                EngineeringReviewSection,
            ):
                raise ValueError(
                    "Every review section must be an "
                    "EngineeringReviewSection object."
                )
 
            if section.category in seen_categories:
                raise ValueError(
                    (
                        "Duplicate engineering review "
                        "section category: "
                        f"'{section.category.value}'."
                    )
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
                EngineeringTradeoff,
            ):
                raise ValueError(
                    "Every review trade-off must be an "
                    "EngineeringTradeoff object."
                )
 
            if (
                tradeoff.tradeoff_id
                in seen_tradeoff_ids
            ):
                raise ValueError(
                    (
                        "Duplicate engineering trade-off "
                        f"ID: '{tradeoff.tradeoff_id}'."
                    )
                )
 
            seen_tradeoff_ids.add(
                tradeoff.tradeoff_id
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
    def _validate_review_items(
        items,
        field_name: str,
    ) -> None:
        """
        Validate one tuple of structured review items.
 
        Item IDs must be unique within one collection.
        The same item may intentionally appear in a
        top-level review collection and in its associated
        category section.
        """
 
        if not isinstance(
            items,
            tuple,
        ):
            raise ValueError(
                f"'{field_name}' must be a tuple."
            )
 
        seen_item_ids: set[str] = set()
 
        for item in items:
            if not isinstance(
                item,
                EngineeringReviewItem,
            ):
                raise ValueError(
                    (
                        f"Every item in '{field_name}' must "
                        "be an EngineeringReviewItem "
                        "object."
                    )
                )
 
            if item.item_id in seen_item_ids:
                raise ValueError(
                    (
                        f"Duplicate engineering review "
                        f"item ID in '{field_name}': "
                        f"'{item.item_id}'."
                    )
                )
 
            seen_item_ids.add(
                item.item_id
            )
 
    @staticmethod
    def _validate_source_ids(
        source_ids,
        field_name: str,
    ) -> tuple[str, ...]:
        """
        Validate and normalize review-level source IDs.
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
    def has_strengths(
        self,
    ) -> bool:
        """
        Return True when positive findings are present.
        """
 
        return bool(
            self.strengths
        )
 
    @property
    def has_concerns(
        self,
    ) -> bool:
        """
        Return True when engineering concerns are present.
        """
 
        return bool(
            self.concerns
        )
 
    @property
    def has_tradeoffs(
        self,
    ) -> bool:
        """
        Return True when engineering trade-offs are present.
        """
 
        return bool(
            self.tradeoffs
        )
 
    @property
    def has_required_actions(
        self,
    ) -> bool:
        """
        Return True when required actions are present.
        """
 
        return bool(
            self.required_actions
        )
 
    @property
    def requires_validation(
        self,
    ) -> bool:
        """
        Return True when explicit validation requirements
        are present.
        """
 
        return bool(
            self.validation_requirements
        )