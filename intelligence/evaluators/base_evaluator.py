"""
base_evaluator.py
 
Common interface for deterministic rule-based engineering
evaluators.
"""
 
from abc import ABC, abstractmethod
 
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_insight import (
    EngineeringInsight,
)
 
 
class EngineeringEvaluator(
    ABC,
):
    """
    Base interface for one deterministic engineering
    evaluator.
 
    An evaluator interprets validated deterministic facts
    using explicit engineering rules.
 
    Evaluators must not:
 
    - perform hidden LLM reasoning;
    - alter the EngineeringContext;
    - alter EngineeringInsight objects;
    - replace deterministic physics calculations;
    - introduce untraceable engineering judgment.
    """
 
    @abstractmethod
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
        Evaluate explicit engineering rules against the
        supplied context and deterministic insights.
 
        An evaluator may return an empty tuple when none
        of its rules apply.
        """
 
        raise NotImplementedError