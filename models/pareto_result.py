"""
Models representing Pareto dominance relationships,
Pareto-front extraction, and candidate-level dominance
metadata.
"""
 
from dataclasses import dataclass
 
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
 
 
@dataclass(frozen=True)
class ParetoDominanceResult:
    """
    Result of comparing two candidate objective analyses.
    """
 
    candidate: CandidateObjectiveAnalysis
 
    compared_candidate: CandidateObjectiveAnalysis
 
    candidate_dominates: bool
 
    compared_candidate_dominates: bool
 
    @property
    def is_tradeoff(
        self,
    ) -> bool:
        """
        Return True when neither candidate dominates the
        other.
        """
 
        return (
            not self.candidate_dominates
            and not self.compared_candidate_dominates
        )
 
 
@dataclass(frozen=True)
class ParetoFrontResult:
    """
    Complete result of Pareto-front extraction.
    """
 
    pareto_candidates: tuple[
        CandidateObjectiveAnalysis,
        ...
    ]
 
    dominated_candidates: tuple[
        CandidateObjectiveAnalysis,
        ...
    ]
 
    @property
    def pareto_candidate_count(
        self,
    ) -> int:
        """
        Return the number of non-dominated candidates.
        """
 
        return len(
            self.pareto_candidates
        )
 
    @property
    def dominated_candidate_count(
        self,
    ) -> int:
        """
        Return the number of dominated candidates.
        """
 
        return len(
            self.dominated_candidates
        )
 
    @property
    def total_candidate_count(
        self,
    ) -> int:
        """
        Return the total number of analyzed candidates.
        """
 
        return (
            self.pareto_candidate_count
            + self.dominated_candidate_count
        )
 
    @property
    def has_tradeoff_set(
        self,
    ) -> bool:
        """
        Return True when the Pareto front contains more
        than one non-dominated candidate.
        """
 
        return (
            self.pareto_candidate_count > 1
        )
 
 
@dataclass(frozen=True)
class ParetoCandidateMetadata:
    """
    Candidate-level Pareto dominance information.
    """
 
    analysis: CandidateObjectiveAnalysis
 
    dominates_count: int
 
    dominated_by_count: int
 
    def __post_init__(
        self,
    ) -> None:
        if self.dominates_count < 0:
            raise ValueError(
                "Dominates count cannot be negative."
            )
 
        if self.dominated_by_count < 0:
            raise ValueError(
                "Dominated-by count cannot be negative."
            )
 
    @property
    def is_pareto_candidate(
        self,
    ) -> bool:
        """
        Return True when no other candidate dominates this
        candidate.
        """
 
        return (
            self.dominated_by_count == 0
        )
 
 
@dataclass(frozen=True)
class ParetoMetadataResult:
    """
    Pareto metadata for a complete candidate collection.
    """
 
    candidates: tuple[
        ParetoCandidateMetadata,
        ...
    ]
 
    @property
    def pareto_candidates(
        self,
    ) -> tuple[
        ParetoCandidateMetadata,
        ...
    ]:
        """
        Return metadata for all non-dominated candidates.
        """
 
        return tuple(
            metadata
            for metadata in self.candidates
            if metadata.is_pareto_candidate
        )
 
    @property
    def dominated_candidates(
        self,
    ) -> tuple[
        ParetoCandidateMetadata,
        ...
    ]:
        """
        Return metadata for all dominated candidates.
        """
 
        return tuple(
            metadata
            for metadata in self.candidates
            if not metadata.is_pareto_candidate
        )
 
    @property
    def total_candidate_count(
        self,
    ) -> int:
        """
        Return the total number of candidates.
        """
 
        return len(
            self.candidates
        )
 
    @property
    def pareto_candidate_count(
        self,
    ) -> int:
        """
        Return the number of non-dominated candidates.
        """
 
        return len(
            self.pareto_candidates
        )
 
    @property
    def dominated_candidate_count(
        self,
    ) -> int:
        """
        Return the number of dominated candidates.
        """
 
        return len(
            self.dominated_candidates
        )
 
    def get_metadata(
        self,
        analysis: CandidateObjectiveAnalysis,
    ) -> ParetoCandidateMetadata:
        """
        Return metadata for a specific candidate analysis.
        """
 
        for metadata in self.candidates:
            if metadata.analysis is analysis:
                return metadata
 
        raise KeyError(
            "No Pareto metadata exists for the supplied "
            "candidate analysis."
        )