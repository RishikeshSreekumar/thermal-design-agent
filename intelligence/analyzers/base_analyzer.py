"""
base_analyzer.py
 
Common interface for deterministic engineering analyzers.
"""
 
from abc import ABC, abstractmethod
 
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_insight import (
    EngineeringInsight,
)
 
 
class EngineeringAnalyzer(
    ABC,
):
    """
    Base interface for one deterministic engineering
    analysis module.
 
    Each analyzer examines a validated EngineeringContext
    and returns zero or more structured insights.
    """
 
    @abstractmethod
    def analyze(
        self,
        context: EngineeringContext,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Generate the insights owned by this analyzer.
        """
 
        raise NotImplementedError