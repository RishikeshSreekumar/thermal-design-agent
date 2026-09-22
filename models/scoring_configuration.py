"""
Models defining objective weights for multi-objective
candidate scoring.
"""
 
import math
from dataclasses import dataclass
 
 
@dataclass(frozen=True)
class ObjectiveWeight:
    """
    Importance assigned to one optimization objective.
    """
 
    objective_key: str
 
    weight: float
 
    def __post_init__(self) -> None:
        normalized_key = (
            self.objective_key
            .strip()
            .lower()
        )
 
        if not normalized_key:
            raise ValueError(
                "Objective key cannot be empty."
            )
 
        if isinstance(self.weight, bool):
            raise ValueError(
                "Objective weight must be numerical."
            )
 
        numeric_weight = float(self.weight)
 
        if not math.isfinite(numeric_weight):
            raise ValueError(
                "Objective weight must be finite."
            )
 
        if numeric_weight < 0.0:
            raise ValueError(
                "Objective weight cannot be negative."
            )
 
        object.__setattr__(
            self,
            "objective_key",
            normalized_key,
        )
 
        object.__setattr__(
            self,
            "weight",
            numeric_weight,
        )
 
 
@dataclass(frozen=True)
class ScoringConfiguration:
    """
    Collection of objective weights used for candidate
    scoring.
    """
 
    objective_weights: tuple[
        ObjectiveWeight,
        ...
    ]
 
    def __post_init__(self) -> None:
        if not self.objective_weights:
            raise ValueError(
                "At least one objective weight is required."
            )
 
        objective_keys = tuple(
            objective_weight.objective_key
            for objective_weight
            in self.objective_weights
        )
 
        if len(set(objective_keys)) != len(
            objective_keys
        ):
            raise ValueError(
                "Objective weights cannot contain "
                "duplicate objective keys."
            )
 
        if self.total_weight <= 0.0:
            raise ValueError(
                "Total objective weight must be "
                "greater than zero."
            )
 
    @property
    def total_weight(self) -> float:
        return sum(
            objective_weight.weight
            for objective_weight
            in self.objective_weights
        )
 
    def get_weight(
        self,
        objective_key: str,
    ) -> float:
        normalized_key = (
            objective_key
            .strip()
            .lower()
        )
 
        for objective_weight in (
            self.objective_weights
        ):
            if (
                objective_weight.objective_key
                == normalized_key
            ):
                return objective_weight.weight
 
        raise KeyError(
            f"No weight configured for objective "
            f"'{objective_key}'."
        )