"""
Models representing the complete Pareto optimization
pipeline result.
"""
 
from dataclasses import dataclass
 
from models.candidate_objective_analysis import (
    CandidateObjectiveAnalysis,
)
from models.pareto_result import (
    ParetoCandidateMetadata,
    ParetoFrontResult,
    ParetoMetadataResult,
)
 
 
@dataclass(frozen=True)
class ParetoOptimizationResult:
    """
    Complete output of the Pareto optimization pipeline.
    """
 
    analyses: tuple[
        CandidateObjectiveAnalysis,
        ...
    ]
 
    metadata: ParetoMetadataResult
 
    front: ParetoFrontResult
 
    @property
    def pareto_candidates(
        self,
    ) -> tuple[
        CandidateObjectiveAnalysis,
        ...
    ]:
        """
        Return all non-dominated candidate analyses.
        """
 
        return self.front.pareto_candidates
 
    @property
    def dominated_candidates(
        self,
    ) -> tuple[
        CandidateObjectiveAnalysis,
        ...
    ]:
        """
        Return all dominated candidate analyses.
        """
 
        return self.front.dominated_candidates
 
    @property
    def pareto_metadata(
        self,
    ) -> tuple[
        ParetoCandidateMetadata,
        ...
    ]:
        """
        Return metadata for all non-dominated candidates.
        """
 
        return self.metadata.pareto_candidates
 
    @property
    def pareto_candidate_count(
        self,
    ) -> int:
        """
        Return the number of Pareto-front candidates.
        """
 
        return self.front.pareto_candidate_count
 
    @property
    def dominated_candidate_count(
        self,
    ) -> int:
        """
        Return the number of dominated candidates.
        """
 
        return self.front.dominated_candidate_count
 
    @property
    def total_candidate_count(
        self,
    ) -> int:
        """
        Return the total number of analyzed candidates.
        """
 
        return self.front.total_candidate_count
 
    @property
    def has_tradeoff_set(
        self,
    ) -> bool:
        """
        Return True when multiple Pareto-optimal solutions
        exist.
        """
 
        return self.front.has_tradeoff_set