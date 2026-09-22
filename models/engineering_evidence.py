"""
engineering_evidence.py
 
Structured evidence supporting an engineering insight.
"""
 
from dataclasses import dataclass
 
 
EngineeringEvidenceValue = (
    float
    | int
    | str
    | bool
)
 
 
@dataclass(frozen=True)
class EngineeringEvidence:
    """
    One traceable item of deterministic evidence supporting
    an engineering insight.
 
    The value must already have been produced or validated
    by the deterministic engineering backend.
    """
 
    key: str
 
    value: EngineeringEvidenceValue
 
    unit: str = ""
 
    description: str = ""
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the evidence definition.
        """
 
        if not isinstance(
            self.key,
            str,
        ):
            raise ValueError(
                "'key' must be a string."
            )
 
        if not self.key.strip():
            raise ValueError(
                "Engineering evidence key cannot be empty."
            )
 
        if not isinstance(
            self.value,
            (
                float,
                int,
                str,
                bool,
            ),
        ):
            raise ValueError(
                "Engineering evidence value must be a "
                "float, int, string, or boolean."
            )
 
        if isinstance(
            self.value,
            str,
        ) and not self.value.strip():
            raise ValueError(
                "Engineering evidence string value cannot "
                "be empty."
            )
 
        if not isinstance(
            self.unit,
            str,
        ):
            raise ValueError(
                "'unit' must be a string."
            )
 
        if not isinstance(
            self.description,
            str,
        ):
            raise ValueError(
                "'description' must be a string."
            )
 
        if (
            self.description
            and not self.description.strip()
        ):
            raise ValueError(
                "Engineering evidence description cannot "
                "contain only whitespace."
            )