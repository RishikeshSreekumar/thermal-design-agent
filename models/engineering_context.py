"""
engineering_context.py
 
Shared engineering context supplied to the engineering
intelligence layer.
 
The context contains validated deterministic engineering
data. It does not perform calculations and must not alter
the underlying optimization result.
"""
 
from dataclasses import dataclass
 
from models.design_candidate import DesignCandidate
from models.optimization_result import OptimizationResult
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.pareto_optimization_result import (
    ParetoOptimizationResult,
)
from models.weighted_optimization_result import (
    WeightedOptimizationResult,
)
from models.requirements import EngineeringRequirements
 
 
@dataclass(frozen=True)
class EngineeringContext:
    """
    Read-only engineering context for AI-assisted
    reasoning, explanation, recommendations, critique,
    reporting, and engineering conversation.
 
    All numerical engineering calculations must be
    completed by the deterministic backend before this
    context is created.
    """
 
    requirements: EngineeringRequirements
 
    optimization_result: OptimizationResult
 
    selection_mode: OptimizationSelectionMode
 
    selected_candidates: tuple[
        DesignCandidate,
        ...
    ]
 
    selected_material: str
 
    selected_process: str
 
    feasible_candidate_count: int
 
    rejected_candidate_count: int
 
    known_limitations: tuple[
        str,
        ...
    ] = ()
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate internal consistency of the engineering
        context.
        """
 
        if not isinstance(
            self.requirements,
            EngineeringRequirements,
        ):
            raise ValueError(
                "'requirements' must be an "
                "EngineeringRequirements object."
            )
 
        if not isinstance(
            self.optimization_result,
            OptimizationResult,
        ):
            raise ValueError(
                "'optimization_result' must be an "
                "OptimizationResult object."
            )
 
        if not isinstance(
            self.selection_mode,
            OptimizationSelectionMode,
        ):
            raise ValueError(
                "'selection_mode' must be an "
                "OptimizationSelectionMode value."
            )
 
        if not self.selected_candidates:
            raise ValueError(
                "Engineering context requires at least "
                "one selected candidate."
            )
 
        if self.feasible_candidate_count < 0:
            raise ValueError(
                "'feasible_candidate_count' cannot be "
                "negative."
            )
 
        if self.rejected_candidate_count < 0:
            raise ValueError(
                "'rejected_candidate_count' cannot be "
                "negative."
            )
 
        if (
            self.feasible_candidate_count
            != self.optimization_result
            .feasible_candidate_count
        ):
            raise ValueError(
                "Feasible candidate count does not match "
                "the optimization result."
            )
 
        if (
            self.rejected_candidate_count
            != self.optimization_result
            .rejected_candidate_count
        ):
            raise ValueError(
                "Rejected candidate count does not match "
                "the optimization result."
            )
 
        if (
            self.selected_material
            != self.optimization_result
            .selected_material
        ):
            raise ValueError(
                "Selected material does not match the "
                "optimization result."
            )
 
        if (
            self.selected_process
            != self.optimization_result
            .selected_process
        ):
            raise ValueError(
                "Selected process does not match the "
                "optimization result."
            )
 
        expected_candidates = (
            self.optimization_result
            .selected_candidates
        )
 
        if len(
            self.selected_candidates
        ) != len(
            expected_candidates
        ):
            raise ValueError(
                "Selected candidate count does not match "
                "the optimization result."
            )
 
        for (
            context_candidate,
            expected_candidate,
        ) in zip(
            self.selected_candidates,
            expected_candidates,
        ):
            if context_candidate is not expected_candidate:
                raise ValueError(
                    "Selected candidates do not match "
                    "the optimization result."
                )
 
        if (
            self.optimization_result
            .selection_result
            is None
        ):
            raise ValueError(
                "Engineering context requires an "
                "optimization selection result."
            )
 
        if (
            self.selection_mode
            != self.optimization_result
            .selection_result
            .configuration
            .mode
        ):
            raise ValueError(
                "Selection mode does not match the "
                "optimization result."
            )
 
        for limitation in self.known_limitations:
            if not isinstance(
                limitation,
                str,
            ):
                raise ValueError(
                    "Every known limitation must be a "
                    "string."
                )
 
            if not limitation.strip():
                raise ValueError(
                    "Known limitations cannot contain "
                    "empty strings."
                )
    
    @property
    def selection_result(
        self,
    ) -> CandidateSelectionResult:
        """
        Return the completed deterministic candidate
        selection result.
        """
 
        selection_result = (
            self.optimization_result
            .selection_result
        )
 
        if selection_result is None:
            raise RuntimeError(
                "Engineering context contains no "
                "candidate selection result."
            )
 
        return selection_result
    
    @property
    def selection_configuration(
        self,
    ) -> OptimizationSelectionConfiguration:
        """
        Return the deterministic selection
        configuration used for this optimization run.
        """
 
        return self.selection_result.configuration
    
    @property
    def uses_legacy_selection(
        self,
    ) -> bool:
        """
        Return True when minimum thermal resistance was
        used as the selection strategy.
        """
 
        return (
            self.selection_mode
            == OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE
        )
 
    @property
    def uses_weighted_selection(
        self,
    ) -> bool:
        """
        Return True when weighted multi-objective
        selection was used.
        """
 
        return (
            self.selection_mode
            == OptimizationSelectionMode
            .WEIGHTED_SCORE
        )
 
    @property
    def uses_pareto_selection(
        self,
    ) -> bool:
        """
        Return True when Pareto-front selection was used.
        """
 
        return (
            self.selection_mode
            == OptimizationSelectionMode
            .PARETO_FRONT
        )
    
    @property
    def weighted_result(
        self,
    ) -> WeightedOptimizationResult | None:
        """
        Return the weighted optimization result when
        weighted selection was used.
        """
 
        return self.selection_result.weighted_result
 
    @property
    def pareto_result(
        self,
    ) -> ParetoOptimizationResult | None:
        """
        Return the Pareto optimization result when
        Pareto-front selection was used.
        """
 
        return self.selection_result.pareto_result
    
    @property
    def selected_candidate_count(
        self,
    ) -> int:
        """
        Return the number of candidates selected by the
        configured optimization strategy.
        """
 
        return len(
            self.selected_candidates
        )
 
    @property
    def has_tradeoff_set(
        self,
    ) -> bool:
        """
        Return True when the context contains multiple
        Pareto-optimal candidates.
        """
 
        return (
            self.uses_pareto_selection
            and self.selected_candidate_count > 1
        )

    @property
    def total_candidate_count(
        self,
    ) -> int:
        """
        Return the total number of explored candidates.
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
        Return the percentage of explored candidates that
        were feasible.
        """
 
        if self.total_candidate_count == 0:
            return 0.0
 
        return (
            100.0
            * self.feasible_candidate_count
            / self.total_candidate_count
        )
 
    @property
    def has_single_selected_design(
        self,
    ) -> bool:
        """
        Return True when exactly one candidate was
        selected.
        """
 
        return len(
            self.selected_candidates
        ) == 1
 
    @property
    def selected_candidate(
        self,
    ) -> DesignCandidate | None:
        """
        Return the unique selected candidate when one
        exists.
 
        Multi-candidate Pareto contexts return None.
        """
 
        if not self.has_single_selected_design:
            return None
 
        return self.selected_candidates[0]
 
    @property
    def has_known_limitations(
        self,
    ) -> bool:
        """
        Return True when explicit model or workflow
        limitations are available.
        """
 
        return bool(
            self.known_limitations
        )