"""
Models configuring how evaluated thermal-design
candidates should be selected.
"""
 
import math
from dataclasses import dataclass
from enum import Enum
 
from models.optimization_objective import (
    OptimizationObjective,
)
from models.scoring_configuration import (
    ScoringConfiguration,
)
 
 
class OptimizationSelectionMode(
    str,
    Enum,
):
    """
    Supported candidate-selection methods.
    """
 
    MINIMUM_THERMAL_RESISTANCE = (
        "minimum_thermal_resistance"
    )
 
    WEIGHTED_SCORE = "weighted_score"
 
    PARETO_FRONT = "pareto_front"
 
 
@dataclass(frozen=True)
class OptimizationSelectionConfiguration:
    """
    Configuration controlling how evaluated design
    candidates are selected.
 
    The default configuration preserves the existing
    minimum-thermal-resistance optimizer behaviour.
    """
 
    mode: OptimizationSelectionMode = (
        OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    )
 
    scoring_configuration: (
        ScoringConfiguration | None
    ) = None
 
    objectives: tuple[
        OptimizationObjective,
        ...,
    ] | None = None
 
    score_tolerance: float = 1e-12
 
    objective_tolerance: float = 1e-12
 
    def __post_init__(
        self,
    ) -> None:
        if not isinstance(
            self.mode,
            OptimizationSelectionMode,
        ):
            raise ValueError(
                "Selection mode must be an "
                "OptimizationSelectionMode."
            )
 
        if (
            self.objectives is not None
            and not self.objectives
        ):
            raise ValueError(
                "Custom optimization objectives cannot "
                "be empty."
            )
 
        if (
            not math.isfinite(
                self.score_tolerance
            )
            or self.score_tolerance < 0.0
        ):
            raise ValueError(
                "Score tolerance must be finite and "
                "non-negative."
            )
 
        if (
            not math.isfinite(
                self.objective_tolerance
            )
            or self.objective_tolerance < 0.0
        ):
            raise ValueError(
                "Objective tolerance must be finite and "
                "non-negative."
            )
 
        if (
            self.mode
            == OptimizationSelectionMode
            .WEIGHTED_SCORE
        ):
            if self.scoring_configuration is None:
                raise ValueError(
                    "Weighted-score selection requires "
                    "a scoring configuration."
                )
 
        elif self.scoring_configuration is not None:
            raise ValueError(
                "Scoring configuration is supported only "
                "for weighted-score selection."
            )
 
    @property
    def uses_multi_objective_selection(
        self,
    ) -> bool:
        """
        Return True when weighted or Pareto selection is
        configured.
        """
 
        return self.mode in {
            OptimizationSelectionMode
            .WEIGHTED_SCORE,
 
            OptimizationSelectionMode
            .PARETO_FRONT,
        }
 
    @property
    def requires_single_best_candidate(
        self,
    ) -> bool:
        """
        Return True when the configured mode directly
        selects one best candidate.
        """
 
        return self.mode in {
            OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE,
 
            OptimizationSelectionMode
            .WEIGHTED_SCORE,
        }