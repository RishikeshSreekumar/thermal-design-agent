"""
engineering_tradeoff.py
 
Structured engineering trade-off synthesized from
deterministic engineering evidence.
 
A trade-off explains a relationship between competing
design benefits, penalties, constraints, or objectives.
It does not perform a new engineering calculation.
"""
 
from dataclasses import dataclass
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
@dataclass(frozen=True)
class EngineeringTradeoff:
    """
    One traceable engineering trade-off.
 
    Parameters
    ----------
    tradeoff_id:
        Stable identifier unique within the review.
 
    title:
        Short name for the competing engineering factors.
 
    severity:
        Importance of the trade-off to the current design.
 
    categories:
        Engineering categories participating in the
        trade-off.
 
    benefit:
        Supported benefit associated with one design
        direction.
 
    penalty:
        Supported disadvantage, cost, or consequence.
 
    guidance:
        Optional explanation of how the trade-off should be
        handled or investigated.
 
    source_assessment_ids:
        Deterministic assessment IDs supporting the
        trade-off.
 
    source_insight_ids:
        Deterministic insight IDs supporting the trade-off.
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
        """
        Validate the structured engineering trade-off.
        """
 
        if not isinstance(
            self.tradeoff_id,
            str,
        ):
            raise ValueError(
                "'tradeoff_id' must be a string."
            )
 
        normalized_tradeoff_id = (
            self.tradeoff_id.strip()
        )
 
        if not normalized_tradeoff_id:
            raise ValueError(
                "Engineering trade-off ID cannot be "
                "empty."
            )
 
        object.__setattr__(
            self,
            "tradeoff_id",
            normalized_tradeoff_id,
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
                "Engineering trade-off title cannot be "
                "empty."
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
 
        if len(self.categories) < 2:
            raise ValueError(
                "Engineering trade-offs must reference at "
                "least two engineering categories."
            )
 
        for category in self.categories:
            if not isinstance(
                category,
                EngineeringCategory,
            ):
                raise ValueError(
                    "Every trade-off category must be an "
                    "EngineeringCategory value."
                )
 
        if (
            len(set(self.categories))
            != len(self.categories)
        ):
            raise ValueError(
                "Engineering trade-off categories must be "
                "unique."
            )
 
        if not isinstance(
            self.benefit,
            str,
        ):
            raise ValueError(
                "'benefit' must be a string."
            )
 
        normalized_benefit = self.benefit.strip()
 
        if not normalized_benefit:
            raise ValueError(
                "Engineering trade-off benefit cannot be "
                "empty."
            )
 
        object.__setattr__(
            self,
            "benefit",
            normalized_benefit,
        )
 
        if not isinstance(
            self.penalty,
            str,
        ):
            raise ValueError(
                "'penalty' must be a string."
            )
 
        normalized_penalty = self.penalty.strip()
 
        if not normalized_penalty:
            raise ValueError(
                "Engineering trade-off penalty cannot be "
                "empty."
            )
 
        object.__setattr__(
            self,
            "penalty",
            normalized_penalty,
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
                "Engineering trade-offs must reference at "
                "least one assessment or insight."
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