"""
Regression checks for completed DesignCandidate state
validation.
"""
 
from dataclasses import replace
 
from core.candidate_state_validator import (
    CandidateStateValidationError,
    validate_completed_candidate,
    validate_completed_candidates,
)
from models.design_candidate import DesignCandidate
 
 
def create_valid_candidate(
) -> DesignCandidate:
    """
    Create one complete and physically valid evaluated
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
 
 
def assert_invalid(
    candidate: DesignCandidate,
    expected_message: str,
) -> None:
    """
    Verify that one invalid candidate is rejected with
    an informative field-specific message.
    """
 
    try:
        validate_completed_candidate(
            candidate
        )
 
    except CandidateStateValidationError as exc:
        assert expected_message in str(exc)
 
    else:
        raise AssertionError(
            "Invalid completed candidate was accepted."
        )
 
 
def main() -> None:
    valid_candidate = create_valid_candidate()

    assert valid_candidate.solid_volume == 0.0
    assert valid_candidate.mass == 0.0
 
    # --------------------------------------------------
    # Valid completed candidate
    # --------------------------------------------------
 
    assert (
        validate_completed_candidate(
            valid_candidate
        )
        is None
    )
 
    assert (
        validate_completed_candidates(
            (
                valid_candidate,
                replace(
                    valid_candidate,
                    fin_spacing=2.0,
                    hydraulic_diameter=0.0032,
                ),
            )
        )
        is None
    )

    try:
        validate_completed_candidate(
            valid_candidate,
            require_physical_properties=True,
        )
 
    except CandidateStateValidationError as exc:
        assert (
            "'solid_volume' must be greater than zero"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Strict physical validation accepted an "
            "unresolved physical candidate."
        )
 
    # --------------------------------------------------
    # Non-finite result state
    # --------------------------------------------------
 
    assert_invalid(
        replace(
            valid_candidate,
            thermal_resistance=float("inf"),
        ),
        "'thermal_resistance' must be finite",
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            pressure_drop=float("nan"),
        ),
        "'pressure_drop' must be finite",
    )
 
    # --------------------------------------------------
    # Geometry state
    # --------------------------------------------------
 
    assert_invalid(
        replace(
            valid_candidate,
            fin_count=1,
        ),
        "'fin_count' must be at least 2",
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            total_height=12.0,
        ),
        "'total_height' must equal",
    )
 
    # --------------------------------------------------
    # Flow geometry
    # --------------------------------------------------
 
    assert_invalid(
        replace(
            valid_candidate,
            open_flow_area=0.0005,
        ),
        "'open_flow_area' cannot exceed",
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            blockage_ratio=1.2,
        ),
        "'blockage_ratio' must lie",
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            channel_velocity=0.0,
        ),
        "'channel_velocity' must be greater",
    )
 
    # --------------------------------------------------
    # Hydraulic state
    # --------------------------------------------------
 
    assert_invalid(
        replace(
            valid_candidate,
            hydraulic_diameter=0.0,
        ),
        "'hydraulic_diameter' must be greater",
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            reynolds_number=-1.0,
        ),
        "'reynolds_number' must be greater",
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            pressure_drop=-1.0,
        ),
        "'pressure_drop' cannot be negative",
    )
 
    # --------------------------------------------------
    # Thermal state
    # --------------------------------------------------
 
    assert_invalid(
        replace(
            valid_candidate,
            nusselt_number=0.0,
        ),
        "'nusselt_number' must be greater",
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            heat_transfer_coefficient=0.0,
        ),
        (
            "'heat_transfer_coefficient' must be "
            "greater"
        ),
    )
 
    assert_invalid(
        replace(
            valid_candidate,
            thermal_resistance=0.0,
        ),
        "'thermal_resistance' must be greater",
    )
 
    # --------------------------------------------------
    # Collection validation reports candidate position
    # --------------------------------------------------
 
    invalid_second_candidate = replace(
        valid_candidate,
        pumping_power=float("nan"),
    )
 
    try:
        validate_completed_candidates(
            (
                valid_candidate,
                invalid_second_candidate,
            )
        )
 
    except CandidateStateValidationError as exc:
        assert "Candidate 2 is invalid" in str(exc)
 
        assert (
            "'pumping_power' must be finite"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid candidate collection was accepted."
        )
 
    # --------------------------------------------------
    # Empty collection
    # --------------------------------------------------
 
    try:
        validate_completed_candidates(())
 
    except CandidateStateValidationError as exc:
        assert (
            "At least one completed design candidate"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Empty completed-candidate collection "
            "was accepted."
        )
    
    try:
        validate_completed_candidate(
            valid_candidate,
            require_physical_properties="yes",
        )
 
    except CandidateStateValidationError as exc:
        assert (
            "'require_physical_properties' must be "
            "a boolean"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid physical-validation option type "
            "was accepted."
        )

    print(
        "ALL CANDIDATE STATE VALIDATOR "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()