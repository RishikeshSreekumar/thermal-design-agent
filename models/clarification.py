"""
clarification.py
 
Models used by the engineering requirement clarification
and validation workflow.
"""
 
from dataclasses import dataclass, field
 
from models.requirements import EngineeringRequirements
 
 
@dataclass
class ClarificationQuestion:
    """
    One question that must be asked before the design
    workflow can continue.
    """
 
    field_name: str
    question: str
    reason: str
    required: bool = True
 
 
@dataclass
class RequirementsReview:
    """
    Result of reviewing parsed engineering requirements.
    """
 
    engineering_requirements: EngineeringRequirements
 
    clarification_questions: list[ClarificationQuestion] = field(
        default_factory=list
    )
 
    validation_errors: list[str] = field(
        default_factory=list
    )
 
    assumptions: list[str] = field(
        default_factory=list
    )
 
    @property
    def needs_clarification(self) -> bool:
        """
        Return True when required engineering information
        is missing.
        """
 
        return bool(self.clarification_questions)
 
    @property
    def has_validation_errors(self) -> bool:
        """
        Return True when supplied values are physically
        invalid or outside the supported range.
        """
 
        return bool(self.validation_errors)
 
    @property
    def can_proceed(self) -> bool:
        """
        Return True only when the design workflow has enough
        valid information to continue.
        """
 
        return (
            not self.needs_clarification
            and not self.has_validation_errors
        )