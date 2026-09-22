"""
engineering_insight.py
 
Structured engineering observation produced from validated
deterministic engineering data.
"""
 
from dataclasses import dataclass
 
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_evidence import (
    EngineeringEvidence,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
@dataclass(frozen=True)
class EngineeringInsight:
    """
    One structured engineering conclusion supported by
    deterministic evidence.
 
    The insight records what the deterministic intelligence
    layer concluded. A future AI layer may explain,
    prioritize, compare, or communicate the insight, but
    must not alter its evidence.
    """
 
    insight_id: str
 
    severity: EngineeringSeverity
 
    category: EngineeringCategory
 
    title: str
 
    summary: str
 
    evidence: tuple[
        EngineeringEvidence,
        ...,
    ] = ()
 
    source: str = ""
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the structured engineering insight.
        """
 
        if not isinstance(
            self.insight_id,
            str,
        ):
            raise ValueError(
                "'insight_id' must be a string."
            )
 
        if not self.insight_id.strip():
            raise ValueError(
                "Engineering insight ID cannot be empty."
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
            self.category,
            EngineeringCategory,
        ):
            raise ValueError(
                "'category' must be an "
                "EngineeringCategory value."
            )
 
        if not isinstance(
            self.title,
            str,
        ):
            raise ValueError(
                "'title' must be a string."
            )
 
        if not self.title.strip():
            raise ValueError(
                "Engineering insight title cannot be "
                "empty."
            )
 
        if not isinstance(
            self.summary,
            str,
        ):
            raise ValueError(
                "'summary' must be a string."
            )
 
        if not self.summary.strip():
            raise ValueError(
                "Engineering insight summary cannot be "
                "empty."
            )
 
        for evidence_item in self.evidence:
            if not isinstance(
                evidence_item,
                EngineeringEvidence,
            ):
                raise ValueError(
                    "Every evidence item must be an "
                    "EngineeringEvidence object."
                )
 
        if not isinstance(
            self.source,
            str,
        ):
            raise ValueError(
                "'source' must be a string."
            )
 
        if (
            self.source
            and not self.source.strip()
        ):
            raise ValueError(
                "Engineering insight source cannot "
                "contain only whitespace."
            )
 
    @property
    def has_evidence(
        self,
    ) -> bool:
        """
        Return True when deterministic supporting evidence
        is attached.
        """
 
        return bool(
            self.evidence
        )
 
    @property
    def is_positive(
        self,
    ) -> bool:
        """
        Return True for a confirmed positive observation.
        """
 
        return (
            self.severity
            == EngineeringSeverity.SUCCESS
        )
 
    @property
    def requires_attention(
        self,
    ) -> bool:
        """
        Return True when the observation requires
        engineering attention.
        """
 
        return self.severity in {
            EngineeringSeverity.WARNING,
            EngineeringSeverity.CRITICAL,
        }
 
    @property
    def is_critical(
        self,
    ) -> bool:
        """
        Return True for a critical engineering concern.
        """
 
        return (
            self.severity
            == EngineeringSeverity.CRITICAL
        )