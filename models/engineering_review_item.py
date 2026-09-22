"""
engineering_review_item.py
 
Structured item used within an engineering review.
 
Review items may represent:
 
- design strengths;
- engineering concerns;
- required actions;
- validation requirements.
 
Every substantive review item must remain traceable to
deterministic engineering assessments and/or insights.
"""
 
from dataclasses import dataclass
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
@dataclass(frozen=True)
class EngineeringReviewItem:
    """
    One structured and traceable engineering-review item.
 
    Parameters
    ----------
    item_id:
        Stable identifier unique within the review.
 
    category:
        Engineering discipline associated with the item.
 
    severity:
        Importance or urgency of the item.
 
    title:
        Short user-facing title.
 
    summary:
        Clear explanation of the engineering finding,
        strength, concern, action, or validation need.
 
    consequence:
        Optional engineering consequence if the item is
        not addressed.
 
    verification:
        Optional method for resolving, confirming, or
        validating the item.
 
    source_assessment_ids:
        Deterministic assessment IDs supporting the item.
 
    source_insight_ids:
        Deterministic insight IDs supporting the item.
    """
 
    item_id: str
 
    category: EngineeringCategory
 
    severity: EngineeringSeverity
 
    title: str
 
    summary: str
 
    consequence: str = ""
 
    verification: str = ""
 
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
        Validate the structured review item.
        """
 
        if not isinstance(
            self.item_id,
            str,
        ):
            raise ValueError(
                "'item_id' must be a string."
            )
 
        normalized_item_id = (
            self.item_id.strip()
        )
 
        if not normalized_item_id:
            raise ValueError(
                "Engineering review item ID cannot be "
                "empty."
            )
 
        object.__setattr__(
            self,
            "item_id",
            normalized_item_id,
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
 
        if not isinstance(
            self.title,
            str,
        ):
            raise ValueError(
                "'title' must be a string."
            )
 
        normalized_title = self.title.strip()
 
        if not normalized_title:
            raise ValueError(
                "Engineering review item title cannot be "
                "empty."
            )
 
        object.__setattr__(
            self,
            "title",
            normalized_title,
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
                "Engineering review item summary cannot "
                "be empty."
            )
 
        object.__setattr__(
            self,
            "summary",
            normalized_summary,
        )
 
        if not isinstance(
            self.consequence,
            str,
        ):
            raise ValueError(
                "'consequence' must be a string."
            )
 
        object.__setattr__(
            self,
            "consequence",
            self.consequence.strip(),
        )
 
        if not isinstance(
            self.verification,
            str,
        ):
            raise ValueError(
                "'verification' must be a string."
            )
 
        object.__setattr__(
            self,
            "verification",
            self.verification.strip(),
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
 
        if (
            not self.source_assessment_ids
            and not self.source_insight_ids
        ):
            raise ValueError(
                "Engineering review items must reference "
                "at least one assessment or insight."
            )
 
    @staticmethod
    def _validate_source_ids(
        source_ids,
        field_name: str,
    ) -> tuple[str, ...]:
        """
        Validate and normalize one collection of source
        identifiers.
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
    def has_consequence(
        self,
    ) -> bool:
        """
        Return True when an engineering consequence is
        recorded.
        """
 
        return bool(
            self.consequence
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
 
    @property
    def is_traceable(
        self,
    ) -> bool:
        """
        Return True when at least one deterministic source
        is referenced.
        """
 
        return bool(
            self.source_assessment_ids
            or self.source_insight_ids
        )