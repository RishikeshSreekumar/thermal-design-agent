"""
End-to-end regression checks for multi-objective
selection through ThermalOptimizer.
 
The test covers:
 
- Default minimum-thermal-resistance selection
- Explicit minimum-thermal-resistance selection
- Weighted-score selection
- Pareto-front selection
- Single-result and multi-result optimizer contracts
"""
 
import math
 
from core.thermal_optimizer import ThermalOptimizer
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def create_requirements(
) -> EngineeringRequirements:
    """
    Create a deliberately small but valid design envelope
    for end-to-end optimizer regression.
    """
 
    return EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        requirements=Requirements(
            heat_load=165.0,
            ambient_temperature=30.0,
            air_velocity=5.0,
        ),
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=8.0,
        ),
    )
 
 
def create_weighted_configuration(
) -> OptimizationSelectionConfiguration:
    """
    Create a balanced thermal-and-airflow scoring
    configuration.
    """
 
    scoring_configuration = (
        ScoringConfiguration(
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
    )
 
    return OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .WEIGHTED_SCORE
        ),
        scoring_configuration=(
            scoring_configuration
        ),
    )
 
 
def create_pareto_configuration(
) -> OptimizationSelectionConfiguration:
    """
    Create a weight-free Pareto selection configuration.
    """
 
    return OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .PARETO_FRONT
        )
    )
 
 
def assert_same_candidate_values(
    first_candidate,
    second_candidate,
) -> None:
    """
    Verify that two separately generated optimizer
    candidates represent the same selected design.
    """
 
    assert math.isclose(
        first_candidate.base_thickness,
        second_candidate.base_thickness,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        first_candidate.fin_thickness,
        second_candidate.fin_thickness,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        first_candidate.fin_height,
        second_candidate.fin_height,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        first_candidate.fin_spacing,
        second_candidate.fin_spacing,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert (
        first_candidate.fin_count
        == second_candidate.fin_count
    )
 
    assert math.isclose(
        first_candidate.thermal_resistance,
        second_candidate.thermal_resistance,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        first_candidate.pressure_drop,
        second_candidate.pressure_drop,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        first_candidate.pumping_power,
        second_candidate.pumping_power,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
 
def main() -> None:
    requirements = create_requirements()
 
    optimizer = ThermalOptimizer()
 
    # --------------------------------------------------
    # 1. Default legacy selection
    # --------------------------------------------------
 
    default_result = (
        optimizer.optimize_with_details(
            requirements
        )
    )
 
    assert default_result.has_feasible_design
 
    assert (
        default_result
        .has_single_selected_design
    )
 
    assert default_result.best_result is not None
 
    assert (
        default_result.selection_result
        is not None
    )
 
    assert (
        default_result.selection_result.mode
        == OptimizationSelectionMode
        .MINIMUM_THERMAL_RESISTANCE
    )
 
    assert (
        default_result.selection_result
        .uses_legacy_selection
    )
 
    assert (
        default_result.selected_candidate
        is not None
    )
 
    assert (
        len(default_result.selected_candidates)
        == 1
    )
 
    minimum_resistance_candidate = min(
        default_result.candidates,
        key=lambda candidate: (
            candidate.thermal_resistance
        ),
    )
 
    assert (
        default_result.selected_candidate
        is minimum_resistance_candidate
    )
 
    assert (
        default_result.selected_candidates
        == (
            minimum_resistance_candidate,
        )
    )
 
    assert math.isclose(
        (
            default_result
            .best_result
            .thermal_resistance
        ),
        (
            minimum_resistance_candidate
            .thermal_resistance
        ),
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert (
        default_result
        .feasible_candidate_count
        == len(default_result.candidates)
    )
 
    assert (
        default_result.total_candidate_count
        == (
            default_result
            .feasible_candidate_count
 
            + default_result
            .rejected_candidate_count
        )
    )
 
    # --------------------------------------------------
    # 2. Existing optimize() API remains compatible
    # --------------------------------------------------
 
    direct_legacy_result = optimizer.optimize(
        requirements
    )
 
    assert math.isclose(
        direct_legacy_result.thermal_resistance,
        (
            default_result
            .best_result
            .thermal_resistance
        ),
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        direct_legacy_result.pressure_drop,
        default_result.best_result.pressure_drop,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert (
        direct_legacy_result.fin_count
        == default_result.best_result.fin_count
    )
 
    # --------------------------------------------------
    # 3. Explicit legacy selection matches default
    # --------------------------------------------------
 
    explicit_legacy_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .MINIMUM_THERMAL_RESISTANCE
            )
        )
    )
 
    explicit_legacy_result = (
        optimizer.optimize_with_details(
            requirements,
            explicit_legacy_configuration,
        )
    )
 
    assert (
        explicit_legacy_result
        .selection_result
        is not None
    )
 
    assert (
        explicit_legacy_result
        .selection_result
        .configuration
        is explicit_legacy_configuration
    )
 
    assert (
        explicit_legacy_result
        .selected_candidate
        is not None
    )
 
    assert_same_candidate_values(
        default_result.selected_candidate,
        explicit_legacy_result.selected_candidate,
    )
 
    # --------------------------------------------------
    # 4. Weighted-score selection
    # --------------------------------------------------
 
    weighted_configuration = (
        create_weighted_configuration()
    )
 
    weighted_result = (
        optimizer.optimize_with_details(
            requirements,
            weighted_configuration,
        )
    )
 
    assert weighted_result.has_feasible_design
 
    assert (
        weighted_result
        .has_single_selected_design
    )
 
    assert weighted_result.best_result is not None
 
    assert (
        weighted_result.selection_result
        is not None
    )
 
    assert (
        weighted_result.selection_result.mode
        == OptimizationSelectionMode
        .WEIGHTED_SCORE
    )
 
    assert (
        weighted_result.selection_result
        .uses_weighted_selection
    )
 
    assert (
        weighted_result.selection_result
        .weighted_result
        is not None
    )
 
    assert (
        weighted_result.selection_result
        .pareto_result
        is None
    )
 
    assert (
        weighted_result.selected_candidate
        is not None
    )
 
    assert (
        len(weighted_result.selected_candidates)
        == 1
    )
 
    weighted_pipeline_result = (
        weighted_result
        .selection_result
        .weighted_result
    )
 
    expected_weighted_candidate = (
        weighted_pipeline_result
        .best_candidate
        .scored_candidate
        .analysis
        .candidate
    )
 
    assert (
        weighted_result.selected_candidate
        is expected_weighted_candidate
    )
 
    assert math.isclose(
        weighted_result
        .best_result
        .thermal_resistance,
        expected_weighted_candidate
        .thermal_resistance,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    weighted_direct_result = optimizer.optimize(
        requirements,
        weighted_configuration,
    )
 
    assert math.isclose(
        weighted_direct_result
        .thermal_resistance,
        weighted_result
        .best_result
        .thermal_resistance,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        weighted_direct_result.pressure_drop,
        weighted_result.best_result.pressure_drop,
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # 5. Pareto-front selection
    # --------------------------------------------------
 
    pareto_configuration = (
        create_pareto_configuration()
    )
 
    pareto_result = (
        optimizer.optimize_with_details(
            requirements,
            pareto_configuration,
        )
    )
 
    assert pareto_result.has_feasible_design
 
    assert (
        pareto_result.selection_result
        is not None
    )
 
    assert (
        pareto_result.selection_result.mode
        == OptimizationSelectionMode
        .PARETO_FRONT
    )
 
    assert (
        pareto_result.selection_result
        .uses_pareto_selection
    )
 
    assert (
        pareto_result.selection_result
        .pareto_result
        is not None
    )
 
    assert (
        pareto_result.selection_result
        .weighted_result
        is None
    )
 
    assert (
        len(pareto_result.selected_candidates)
        >= 1
    )
 
    pareto_pipeline_result = (
        pareto_result
        .selection_result
        .pareto_result
    )
 
    expected_pareto_candidates = tuple(
        analysis.candidate
        for analysis
        in pareto_pipeline_result
        .pareto_candidates
    )
 
    assert (
        pareto_result.selected_candidates
        == expected_pareto_candidates
    )
 
    assert (
        pareto_pipeline_result
        .total_candidate_count
        == pareto_result
        .feasible_candidate_count
    )
 
    assert (
        pareto_pipeline_result
        .pareto_candidate_count
        == len(
            pareto_result.selected_candidates
        )
    )
 
    assert (
        pareto_pipeline_result
        .dominated_candidate_count
        == (
            pareto_result
            .feasible_candidate_count
 
            - len(
                pareto_result
                .selected_candidates
            )
        )
    )
 
    # --------------------------------------------------
    # 6. Pareto single-result and multi-result contracts
    # --------------------------------------------------
 
    if len(
        pareto_result.selected_candidates
    ) == 1:
        assert (
            pareto_result
            .has_single_selected_design
        )
 
        assert pareto_result.best_result is not None
 
        assert (
            pareto_result.selected_candidate
            is pareto_result
            .selected_candidates[0]
        )
 
        pareto_direct_result = optimizer.optimize(
            requirements,
            pareto_configuration,
        )
 
        assert math.isclose(
            pareto_direct_result
            .thermal_resistance,
            pareto_result
            .best_result
            .thermal_resistance,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
 
    else:
        assert not (
            pareto_result
            .has_single_selected_design
        )
 
        assert pareto_result.best_result is None
 
        assert (
            pareto_result.selected_candidate
            is None
        )
 
        try:
            optimizer.optimize(
                requirements,
                pareto_configuration,
            )
 
        except ValueError as exc:
            assert (
                "did not produce one uniquely "
                "selected design"
                in str(exc)
            )
 
        else:
            raise AssertionError(
                "optimize() must reject a "
                "multi-candidate Pareto result."
            )
 
    # --------------------------------------------------
    # 7. Every selected Pareto candidate is feasible
    # --------------------------------------------------
 
    feasible_candidate_ids = {
        id(candidate)
        for candidate
        in pareto_result.candidates
    }
 
    assert all(
        id(candidate)
        in feasible_candidate_ids
        for candidate
        in pareto_result.selected_candidates
    )
 
    print(
        "ALL MULTI-OBJECTIVE OPTIMIZER "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()