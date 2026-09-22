"""
Regression checks for completed-candidate validation at
the unified candidate-selection boundary.
 
The test verifies that:
 
- Valid completed candidates reach every selection mode.
- Invalid candidates are rejected before selection.
- Candidate index and field details remain available
  through the wrapped validation exception.
- Legacy, weighted, and Pareto modes share the same
  validation boundary.
"""
 
from dataclasses import replace
 
from core.candidate_selector import (
    CandidateSelectionError,
    select_candidates,
)
from core.candidate_state_validator import (
    CandidateStateValidationError,
)
from models.design_candidate import DesignCandidate
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def create_valid_candidate(
) -> DesignCandidate:
    """
    Create one fully evaluated and physically valid
    candidate.
    """
 
    return DesignCandidate(
        base_thickness=3.0,
        fin_thickness=0.8,
        fin_height=8.0,
        fin_spacing=1.6,
        fin_count=21,
        total_height=11.0,
 
        gross_frontal_area=0.0004,
        open_flow_area=0.000256,
        blockage_ratio=0.36,
        approach_velocity=5.0,
        channel_velocity=7.8125,
 
        reynolds_number=1295.405982905983,
        nusselt_number=7.54,
        heat_transfer_coefficient=74.36325,
 
        friction_factor=0.049405,
        pressure_drop=86.1899,
        pumping_power=0.1723798,
 
        thermal_resistance=0.680824,
        estimated_base_temperature=142.33596,
 
        hydraulic_diameter=(
            0.0026666666666666666
        ),
    )
 
 
def create_weighted_configuration(
) -> OptimizationSelectionConfiguration:
    """
    Create a valid weighted-selection configuration.
    """
 
    return OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .WEIGHTED_SCORE
        ),
        scoring_configuration=(
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
        ),
    )
 
 
def assert_selection_rejects_candidate(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    configuration: (
        OptimizationSelectionConfiguration | None
    ),
    expected_detail: str,
) -> None:
    """
    Confirm that the selection API wraps a completed-state
    validation error while retaining the detailed cause.
    """
 
    try:
        select_candidates(
            candidates,
            configuration,
        )
 
    except CandidateSelectionError as exc:
        assert (
            "requires complete and physically valid"
            in str(exc)
        )
 
        assert isinstance(
            exc.__cause__,
            CandidateStateValidationError,
        )
 
        assert expected_detail in str(
            exc.__cause__
        )
 
    else:
        raise AssertionError(
            "Selection accepted an invalid completed "
            "candidate."
        )
 
 
def main() -> None:
    valid_candidate = create_valid_candidate()
 
    second_valid_candidate = replace(
        valid_candidate,
        fin_spacing=2.0,
        hydraulic_diameter=0.0032,
        thermal_resistance=0.75,
        pressure_drop=60.0,
        pumping_power=0.12,
    )
 
    valid_candidates = (
        valid_candidate,
        second_valid_candidate,
    )
 
    # --------------------------------------------------
    # Valid candidates reach each selection mode
    # --------------------------------------------------
 
    legacy_result = select_candidates(
        valid_candidates
    )
 
    assert legacy_result.uses_legacy_selection
 
    assert (
        legacy_result.selected_candidate
        is valid_candidate
    )
 
    weighted_result = select_candidates(
        valid_candidates,
        create_weighted_configuration(),
    )
 
    assert weighted_result.uses_weighted_selection
 
    assert weighted_result.selected_candidate is not None
 
    pareto_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .PARETO_FRONT
            )
        )
    )
 
    pareto_result = select_candidates(
        valid_candidates,
        pareto_configuration,
    )
 
    assert pareto_result.uses_pareto_selection
 
    assert (
        pareto_result.selected_candidate_count
        >= 1
    )
 
    # --------------------------------------------------
    # Legacy mode rejects incomplete hydraulic state
    # --------------------------------------------------
 
    unresolved_candidate = replace(
        valid_candidate,
        hydraulic_diameter=0.0,
    )
 
    assert_selection_rejects_candidate(
        (
            unresolved_candidate,
        ),
        None,
        (
            "'hydraulic_diameter' must be "
            "greater than zero"
        ),
    )
 
    # --------------------------------------------------
    # Weighted mode rejects non-finite objective state
    # before normalization or scoring
    # --------------------------------------------------
 
    non_finite_candidate = replace(
        valid_candidate,
        thermal_resistance=float("nan"),
    )
 
    assert_selection_rejects_candidate(
        (
            valid_candidate,
            non_finite_candidate,
        ),
        create_weighted_configuration(),
        (
            "Candidate 2 is invalid: "
            "'thermal_resistance' must be finite"
        ),
    )
 
    # --------------------------------------------------
    # Pareto mode rejects invalid flow geometry before
    # dominance analysis
    # --------------------------------------------------
 
    impossible_flow_candidate = replace(
        valid_candidate,
        open_flow_area=0.0005,
    )
 
    assert_selection_rejects_candidate(
        (
            impossible_flow_candidate,
            valid_candidate,
        ),
        pareto_configuration,
        (
            "Candidate 1 is invalid: "
            "'open_flow_area' cannot exceed"
        ),
    )
 
    # --------------------------------------------------
    # Invalid non-objective fields are also rejected
    # --------------------------------------------------
 
    invalid_total_height_candidate = replace(
        valid_candidate,
        total_height=12.0,
    )
 
    assert_selection_rejects_candidate(
        (
            invalid_total_height_candidate,
        ),
        None,
        "'total_height' must equal",
    )
 
    # --------------------------------------------------
    # Empty collection retains the selector's existing
    # public error contract
    # --------------------------------------------------
 
    try:
        select_candidates(())
 
    except CandidateSelectionError as exc:
        assert (
            "At least one evaluated design candidate"
            in str(exc)
        )
 
        assert exc.__cause__ is None
 
    else:
        raise AssertionError(
            "Empty candidate collection was accepted."
        )
 
    print(
        "ALL CANDIDATE SELECTION VALIDATION "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()