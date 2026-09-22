"""
Regression checks for optimization-selection
configuration.
"""
 
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def create_scoring_configuration(
) -> ScoringConfiguration:
    return ScoringConfiguration(
        objective_weights=(
            ObjectiveWeight(
                objective_key=(
                    "thermal_resistance"
                ),
                weight=0.6,
            ),
            ObjectiveWeight(
                objective_key=(
                    "pressure_drop"
                ),
                weight=0.3,
            ),
            ObjectiveWeight(
                objective_key=(
                    "pumping_power"
                ),
                weight=0.1,
            ),
        )
    )
 
 
def main() -> None:
    legacy_configuration = (
        OptimizationSelectionConfiguration()
    )
 
    assert (
        legacy_configuration.mode
        == OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    )
 
    assert not (
        legacy_configuration
        .uses_multi_objective_selection
    )
 
    assert (
        legacy_configuration
        .requires_single_best_candidate
    )
 
    weighted_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .WEIGHTED_SCORE
            ),
            scoring_configuration=(
                create_scoring_configuration()
            ),
        )
    )
 
    assert (
        weighted_configuration
        .uses_multi_objective_selection
    )
 
    assert (
        weighted_configuration
        .requires_single_best_candidate
    )
 
    assert (
        weighted_configuration
        .scoring_configuration
        is not None
    )
 
    pareto_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .PARETO_FRONT
            )
        )
    )
 
    assert (
        pareto_configuration
        .uses_multi_objective_selection
    )
 
    assert not (
        pareto_configuration
        .requires_single_best_candidate
    )
 
    try:
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .WEIGHTED_SCORE
            )
        )
 
    except ValueError as exc:
        assert (
            "requires a scoring configuration"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Weighted selection without scoring "
            "configuration must be rejected."
        )
 
    try:
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .PARETO_FRONT
            ),
            scoring_configuration=(
                create_scoring_configuration()
            ),
        )
 
    except ValueError as exc:
        assert (
            "supported only for weighted-score"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Pareto selection must reject scoring "
            "configuration."
        )
 
    try:
        OptimizationSelectionConfiguration(
            objectives=()
        )
 
    except ValueError as exc:
        assert (
            "objectives cannot be empty"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Empty custom objectives must be rejected."
        )
 
    try:
        OptimizationSelectionConfiguration(
            score_tolerance=-1.0
        )
 
    except ValueError as exc:
        assert (
            "Score tolerance"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Negative score tolerance must be rejected."
        )
 
    try:
        OptimizationSelectionConfiguration(
            objective_tolerance=-1.0
        )
 
    except ValueError as exc:
        assert (
            "Objective tolerance"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Negative objective tolerance must be "
            "rejected."
        )
 
    try:
        OptimizationSelectionConfiguration(
            mode="weighted_score",
            scoring_configuration=(
                create_scoring_configuration()
            ),
        )
 
    except ValueError as exc:
        assert (
            "OptimizationSelectionMode"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Raw selection-mode strings must be rejected."
        )
 
    print(
        "ALL OPTIMIZATION SELECTION "
        "CONFIGURATION CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()