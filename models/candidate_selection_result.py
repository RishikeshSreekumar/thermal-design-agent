"""
Unified result model for evaluated-candidate selection.
 
The result supports:
 
- Legacy minimum-thermal-resistance selection
- Weighted multi-objective selection
- Pareto-front selection
"""
 
from dataclasses import dataclass
 
from models.design_candidate import DesignCandidate
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
 
 
@dataclass(frozen=True)
class CandidateSelectionResult:
    """
    Unified result of selecting from evaluated design
    candidates.
 
    Single-candidate modes populate selected_candidate.
 
    Pareto selection populates selected_candidates with
    all non-dominated candidates.
    """
 
    configuration: (
        OptimizationSelectionConfiguration
    )
 
    selected_candidates: tuple[
        DesignCandidate,
        ...
    ]
 
    weighted_result: (
        WeightedOptimizationResult | None
    ) = None
 
    pareto_result: (
        ParetoOptimizationResult | None
    ) = None
 
    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.configuration,
            OptimizationSelectionConfiguration,
        ):
            raise ValueError(
                "Configuration must be an "
                "OptimizationSelectionConfiguration."
            )
 
        if not self.selected_candidates:
            raise ValueError(
                "At least one selected candidate is "
                "required."
            )
 
        mode = self.configuration.mode
 
        if (
            mode
            == OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE
        ):
            self._validate_legacy_result()
 
        elif (
            mode
            == OptimizationSelectionMode
            .WEIGHTED_SCORE
        ):
            self._validate_weighted_result()
 
        elif (
            mode
            == OptimizationSelectionMode
            .PARETO_FRONT
        ):
            self._validate_pareto_result()
 
        else:
            raise ValueError(
                "Unsupported optimization selection "
                "mode."
            )
 
    def _validate_legacy_result(
        self,
    ) -> None:
        """
        Validate minimum-thermal-resistance selection.
        """
 
        if len(self.selected_candidates) != 1:
            raise ValueError(
                "Minimum-thermal-resistance selection "
                "must return exactly one candidate."
            )
 
        if self.weighted_result is not None:
            raise ValueError(
                "Legacy selection cannot contain a "
                "weighted optimization result."
            )
 
        if self.pareto_result is not None:
            raise ValueError(
                "Legacy selection cannot contain a "
                "Pareto optimization result."
            )
 
    def _validate_weighted_result(
        self,
    ) -> None:
        """
        Validate weighted-score selection.
        """
 
        if len(self.selected_candidates) != 1:
            raise ValueError(
                "Weighted-score selection must return "
                "exactly one candidate."
            )
 
        if self.weighted_result is None:
            raise ValueError(
                "Weighted-score selection requires a "
                "weighted optimization result."
            )
 
        if self.pareto_result is not None:
            raise ValueError(
                "Weighted-score selection cannot contain "
                "a Pareto optimization result."
            )
 
        expected_candidate = (
            self.weighted_result
            .best_candidate
            .scored_candidate
            .analysis
            .candidate
        )
 
        if (
            self.selected_candidates[0]
            is not expected_candidate
        ):
            raise ValueError(
                "Selected weighted candidate does not "
                "match the best ranked candidate."
            )
 
    def _validate_pareto_result(
        self,
    ) -> None:
        """
        Validate Pareto-front selection.
        """
 
        if self.pareto_result is None:
            raise ValueError(
                "Pareto-front selection requires a "
                "Pareto optimization result."
            )
 
        if self.weighted_result is not None:
            raise ValueError(
                "Pareto-front selection cannot contain "
                "a weighted optimization result."
            )
 
        expected_candidates = tuple(
            analysis.candidate
            for analysis
            in self.pareto_result.pareto_candidates
        )
 
        if len(expected_candidates) != len(
            self.selected_candidates
        ):
            raise ValueError(
                "Selected Pareto candidate count does "
                "not match the Pareto result."
            )
 
        for (
            selected_candidate,
            expected_candidate,
        ) in zip(
            self.selected_candidates,
            expected_candidates,
        ):
            if (
                selected_candidate
                is not expected_candidate
            ):
                raise ValueError(
                    "Selected Pareto candidates do not "
                    "match the extracted Pareto front."
                )
 
    @property
    def mode(
        self,
    ) -> OptimizationSelectionMode:
        """
        Return the configured selection mode.
        """
 
        return self.configuration.mode
 
    @property
    def selected_candidate(
        self,
    ) -> DesignCandidate | None:
        """
        Return the selected candidate for single-result
        modes.
 
        Pareto-front selection returns None because it may
        contain multiple equally non-dominated candidates.
        """
 
        if len(self.selected_candidates) != 1:
            return None
 
        return self.selected_candidates[0]
 
    @property
    def has_single_selected_candidate(
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
    def selected_candidate_count(
        self,
    ) -> int:
        """
        Return the number of selected candidates.
        """
 
        return len(
            self.selected_candidates
        )
 
    @property
    def uses_weighted_selection(
        self,
    ) -> bool:
        """
        Return True for weighted-score selection.
        """
 
        return (
            self.mode
            == OptimizationSelectionMode
            .WEIGHTED_SCORE
        )
 
    @property
    def uses_pareto_selection(
        self,
    ) -> bool:
        """
        Return True for Pareto-front selection.
        """
 
        return (
            self.mode
            == OptimizationSelectionMode
            .PARETO_FRONT
        )
 
    @property
    def uses_legacy_selection(
        self,
    ) -> bool:
        """
        Return True for minimum-thermal-resistance
        selection.
        """
 
        return (
            self.mode
            == OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE
        )