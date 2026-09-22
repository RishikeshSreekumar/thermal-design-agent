"""
engineering_intelligence_result.py
 
Immutable aggregate returned by the deterministic
engineering-intelligence pipeline.
"""
 
from dataclasses import dataclass
 
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_insight import (
    EngineeringInsight,
)
 
 
@dataclass(frozen=True)
class EngineeringIntelligenceResult:
    """
    Complete deterministic engineering-intelligence result.
 
    This object groups:
 
    - the validated EngineeringContext;
    - deterministic EngineeringInsight objects;
    - deterministic EngineeringAssessment objects.
    """
 
    context: EngineeringContext
 
    insights: tuple[
        EngineeringInsight,
        ...,
    ]
 
    assessments: tuple[
        EngineeringAssessment,
        ...,
    ]
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the aggregate result.
        """
 
        if not isinstance(
            self.context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )
 
        if not isinstance(
            self.insights,
            tuple,
        ):
            raise ValueError(
                "'insights' must be a tuple."
            )
 
        for insight in self.insights:
            if not isinstance(
                insight,
                EngineeringInsight,
            ):
                raise ValueError(
                    "Every insight must be an "
                    "EngineeringInsight object."
                )
 
        if not isinstance(
            self.assessments,
            tuple,
        ):
            raise ValueError(
                "'assessments' must be a tuple."
            )
 
        for assessment in self.assessments:
            if not isinstance(
                assessment,
                EngineeringAssessment,
            ):
                raise ValueError(
                    "Every assessment must be an "
                    "EngineeringAssessment object."
                )
 
    @property
    def has_insights(
        self,
    ) -> bool:
        """
        Return True when the pipeline generated insights.
        """
 
        return bool(
            self.insights
        )
 
    @property
    def has_assessments(
        self,
    ) -> bool:
        """
        Return True when the pipeline generated assessments.
        """
 
        return bool(
            self.assessments
        )
 
    @property
    def failed_assessments(
        self,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Return all assessments whose rules did not pass.
        """
 
        return tuple(
            assessment
            for assessment in self.assessments
            if not assessment.passed
        )
 
    @property
    def passed_assessments(
        self,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Return all assessments whose rules passed.
        """
 
        return tuple(
            assessment
            for assessment in self.assessments
            if assessment.passed
        )