"""
optimization_result.py
 
Container for optimization results.
"""
 
from dataclasses import dataclass, field
 
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.design_candidate import DesignCandidate
from models.thermal import ThermalResults
 
 
@dataclass
class OptimizationResult:
    """
    Complete output of one optimization run.
 
    best_result is populated only when the configured
    selection method produces one uniquely selected
    candidate.
 
    Pareto-front selection may produce multiple selected
    candidates, in which case best_result remains None
    and the candidates are available through
    selection_result.
    """
 
    best_result: ThermalResults | None
 
    candidates: list[DesignCandidate] = field(
        default_factory=list
    )
 
    feasible_candidate_count: int = 0
 
    rejected_candidate_count: int = 0
 
    selected_material: str = ""
 
    selected_process: str = ""
 
    selection_result: (
        CandidateSelectionResult | None
    ) = None
 
    @property
    def total_candidate_count(
        self,
    ) -> int:
        """
        Total explored candidates.
        """
 
        return (
            self.feasible_candidate_count
            + self.rejected_candidate_count
        )
 
    @property
    def feasibility_rate(
        self,
    ) -> float:
        """
        Percentage of candidates that are manufacturable.
        """
 
        if self.total_candidate_count == 0:
            return 0.0
 
        return (
            100.0
            * self.feasible_candidate_count
            / self.total_candidate_count
        )
 
    @property
    def has_feasible_design(
        self,
    ) -> bool:
        """
        Return True when at least one feasible candidate
        was generated.
 
        This remains True for a multi-candidate Pareto
        result even though no unique best_result exists.
        """
 
        return (
            self.feasible_candidate_count > 0
        )
 
    @property
    def has_single_selected_design(
        self,
    ) -> bool:
        """
        Return True when the configured selection method
        produced exactly one selected candidate and a
        converted ThermalResults object.
        """
 
        return (
            self.best_result is not None
            and self.selection_result is not None
            and (
                self.selection_result
                .has_single_selected_candidate
            )
        )
 
    @property
    def selected_candidates(
        self,
    ) -> tuple[
        DesignCandidate,
        ...
    ]:
        """
        Return candidates selected by the configured
        selection strategy.
        """
 
        if self.selection_result is None:
            return ()
 
        return (
            self.selection_result
            .selected_candidates
        )
 
    @property
    def selected_candidate(
        self,
    ) -> DesignCandidate | None:
        """
        Return the unique selected candidate when one
        exists.
 
        Multi-candidate Pareto results return None.
        """
 
        if self.selection_result is None:
            return None
 
        return (
            self.selection_result
            .selected_candidate
        )