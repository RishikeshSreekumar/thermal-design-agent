"""
optimization_objective.py
 
Defines the data models used to describe optimization
objectives.
 
This module does not calculate, normalize, weight, or rank
objective values. It only provides a standard description
of what an optimization objective represents.
"""
 
from dataclasses import dataclass
from enum import Enum
 
 
class ObjectiveDirection(str, Enum):
    """
    Defines whether an optimization objective should be
    minimized or maximized.
    """
 
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
 
 
@dataclass(frozen=True)
class OptimizationObjective:
    """
    Describes one engineering optimization objective.
 
    Parameters
    ----------
    name:
        Human-readable objective name.
 
    candidate_attribute:
        Name of the DesignCandidate attribute containing
        the raw objective value.
 
    direction:
        Whether lower or higher values are preferred.
 
    unit:
        Engineering unit used by the raw objective value.
 
    description:
        Explanation of the engineering meaning of the
        objective.
    """
 
    name: str
 
    candidate_attribute: str
 
    direction: ObjectiveDirection
 
    unit: str
 
    description: str = ""