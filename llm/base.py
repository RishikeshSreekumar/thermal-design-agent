"""
base.py
 
Common interface for all LLM providers used by the
Thermal AI Engineer application.
"""
 
from abc import ABC, abstractmethod
 
 
class LLMProvider(ABC):
    """
    Base class for every supported LLM provider.
 
    Provider-specific API details remain isolated from the
    rest of the engineering application.
    """
 
    @abstractmethod
    def extract_requirements(
        self,
        user_prompt: str,
    ) -> dict:
        """
        Convert a natural-language engineering request into
        a structured requirements dictionary.
        """
 
        raise NotImplementedError(
            "Subclasses must implement "
            "'extract_requirements()'."
        )
 
    @abstractmethod
    def synthesize_engineering_review(
        self,
        payload: dict,
    ) -> dict:
        """
        Produce non-authoritative engineering-review
        synthesis from a grounded deterministic payload.
 
        Implementations must return a dictionary matching
        the engineering-review synthesis schema.
        """
 
        raise NotImplementedError(
            "Subclasses must implement "
            "'synthesize_engineering_review()'."
        )

    @abstractmethod
    def synthesize_engineering_recommendations(
        self,
        payload: dict,
    ) -> dict:
        """
        Generate grounded engineering recommendations
        from the supplied Step 35 evidence package.
 
        Implementations must return a dictionary matching
        the recommendation synthesis schema.
        """
        raise NotImplementedError