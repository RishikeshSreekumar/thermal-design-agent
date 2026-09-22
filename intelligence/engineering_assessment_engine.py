"""
engineering_assessment_engine.py
 
Orchestrates deterministic rule-based engineering
evaluators.
 
The engine receives:
 
- one validated EngineeringContext;
- deterministic EngineeringInsight objects;
- an ordered collection of EngineeringEvaluator objects.
 
It returns one immutable tuple of structured
EngineeringAssessment objects.
 
The engine does not contain engineering rules itself.
"""
 
from collections.abc import Iterable
 
from intelligence.evaluators.base_evaluator import (
    EngineeringEvaluator,
)
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_insight import (
    EngineeringInsight,
)
 
 
class EngineeringAssessmentEngine:
    """
    Run an ordered collection of deterministic engineering
    evaluators and combine their assessments.
    """
 
    def __init__(
        self,
        evaluators: tuple[
            EngineeringEvaluator,
            ...,
        ] = (),
    ) -> None:
        """
        Create the assessment engine.
 
        Evaluators are executed in the order supplied.
        """
 
        if not isinstance(
            evaluators,
            tuple,
        ):
            raise ValueError(
                "'evaluators' must be a tuple."
            )
 
        for evaluator in evaluators:
            if not isinstance(
                evaluator,
                EngineeringEvaluator,
            ):
                raise ValueError(
                    "Every evaluator must implement "
                    "EngineeringEvaluator."
                )
 
        self._evaluators = evaluators
 
    @property
    def evaluators(
        self,
    ) -> tuple[
        EngineeringEvaluator,
        ...,
    ]:
        """
        Return the configured evaluator collection.
        """
 
        return self._evaluators
 
    def evaluate(
        self,
        context: EngineeringContext,
        insights: tuple[
            EngineeringInsight,
            ...,
        ],
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Run every configured evaluator and return the
        combined ordered assessment collection.
        """
 
        if not isinstance(
            context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )
 
        if not isinstance(
            insights,
            tuple,
        ):
            raise ValueError(
                "'insights' must be a tuple."
            )
 
        for insight in insights:
            if not isinstance(
                insight,
                EngineeringInsight,
            ):
                raise ValueError(
                    "Every insight must be an "
                    "EngineeringInsight object."
                )
 
        assessments: list[
            EngineeringAssessment
        ] = []
 
        for evaluator in self._evaluators:
            evaluator_assessments = (
                evaluator.evaluate(
                    context=context,
                    insights=insights,
                )
            )
 
            self._validate_evaluator_output(
                evaluator=evaluator,
                assessments=evaluator_assessments,
            )
 
            assessments.extend(
                evaluator_assessments
            )
 
        self._validate_unique_assessment_ids(
            assessments
        )
 
        return tuple(
            assessments
        )
 
    @staticmethod
    def _validate_evaluator_output(
        evaluator: EngineeringEvaluator,
        assessments,
    ) -> None:
        """
        Validate the result returned by one evaluator.
        """
 
        if not isinstance(
            assessments,
            tuple,
        ):
            raise ValueError(
                (
                    f"{evaluator.__class__.__name__}.evaluate() "
                    "must return a tuple."
                )
            )
 
        for assessment in assessments:
            if not isinstance(
                assessment,
                EngineeringAssessment,
            ):
                raise ValueError(
                    (
                        f"{evaluator.__class__.__name__}.evaluate() "
                        "returned an item that is not an "
                        "EngineeringAssessment."
                    )
                )
 
    @staticmethod
    def _validate_unique_assessment_ids(
        assessments: Iterable[
            EngineeringAssessment
        ],
    ) -> None:
        """
        Reject duplicate assessment identifiers across the
        complete evaluator pipeline.
        """
 
        seen_ids: set[str] = set()
 
        for assessment in assessments:
            if (
                assessment.assessment_id
                in seen_ids
            ):
                raise ValueError(
                    (
                        "Duplicate engineering assessment ID: "
                        f"'{assessment.assessment_id}'."
                    )
                )
 
            seen_ids.add(
                assessment.assessment_id
            )