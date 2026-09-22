"""
Models linking a design candidate with its raw and
normalized objective-evaluation reports.
"""
 
from dataclasses import dataclass
 
from models.design_candidate import DesignCandidate
from models.objective_result import (
    NormalizedObjectiveEvaluationResult,
    ObjectiveEvaluationResult,
)
 
 
@dataclass(frozen=True)
class CandidateObjectiveAnalysis:
    """
    Complete multi-objective analysis of one evaluated
    design candidate.
    """
 
    candidate: DesignCandidate
 
    raw_report: ObjectiveEvaluationResult
 
    normalized_report: (
        NormalizedObjectiveEvaluationResult
    )
 