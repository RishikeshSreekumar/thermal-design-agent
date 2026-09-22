"""
Regression checks for DesignCandidate physical-property
state validation.
 
The regression verifies that:
 
- Positive finite solid volume and mass are accepted.
- Zero, negative, NaN, and infinite values are rejected.
- Physical validation can be enabled for one candidate or
  an entire candidate collection.
- Default completed-candidate validation remains backward
  compatible.
"""
 
from dataclasses import replace
 
from core.candidate_state_validator import (
    CandidateStateValidationError,
    validate_candidate_physical_properties,
    validate_completed_candidate,
    validate_completed_candidates,
)
from models.design_candidate import DesignCandidate
 
 
def create_candidate(
) -> DesignCandidate:
    """
    Create one complete candidate with resolved hydraulic,
    thermal, and physical state.
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
 
        solid_volume=1.422e-5,
        mass=0.038394,
    )
 
 
def assert_invalid_physical_state(
    candidate: DesignCandidate,
    expected_message: str,
) -> None:
    """
    Verify that one invalid physical candidate state is
    rejected.
    """
 
    try:
        validate_candidate_physical_properties(
            candidate
        )
 
    except CandidateStateValidationError as exc:
        assert expected_message in str(exc)
 
    else:
        raise AssertionError(
            "Invalid candidate physical state was "
            "accepted."
        )
 
 
def main() -> None:
    valid_candidate = create_candidate()
 
    # --------------------------------------------------
    # Standalone physical validation
    # --------------------------------------------------
 
    assert (
        validate_candidate_physical_properties(
            valid_candidate
        )
        is None
    )
 
    # --------------------------------------------------
    # Combined strict completed-state validation
    # --------------------------------------------------
 
    assert (
        validate_completed_candidate(
            valid_candidate,
            require_physical_properties=True,
        )
        is None
    )
 
    assert (
        validate_completed_candidates(
            (
                valid_candidate,
                replace(
                    valid_candidate,
                    solid_volume=1.5e-5,
                    mass=0.0405,
                ),
            ),
            require_physical_properties=True,
        )
        is None
    )
 
    # --------------------------------------------------
    # Solid-volume validation
    # --------------------------------------------------
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            solid_volume=0.0,
        ),
        "'solid_volume' must be greater than zero",
    )
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            solid_volume=-1.0,
        ),
        "'solid_volume' must be greater than zero",
    )
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            solid_volume=float("inf"),
        ),
        "'solid_volume' must be finite",
    )
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            solid_volume=float("nan"),
        ),
        "'solid_volume' must be finite",
    )
 
    # --------------------------------------------------
    # Mass validation
    # --------------------------------------------------
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            mass=0.0,
        ),
        "'mass' must be greater than zero",
    )
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            mass=-0.01,
        ),
        "'mass' must be greater than zero",
    )
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            mass=float("inf"),
        ),
        "'mass' must be finite",
    )
 
    assert_invalid_physical_state(
        replace(
            valid_candidate,
            mass=float("nan"),
        ),
        "'mass' must be finite",
    )
 
    # --------------------------------------------------
    # Default completed validation remains compatible
    # with unresolved legacy physical fields.
    # --------------------------------------------------
 
    unresolved_physical_candidate = replace(
        valid_candidate,
        solid_volume=0.0,
        mass=0.0,
    )
 
    assert (
        validate_completed_candidate(
            unresolved_physical_candidate
        )
        is None
    )
 
    # Strict validation rejects the same candidate.
    try:
        validate_completed_candidate(
            unresolved_physical_candidate,
            require_physical_properties=True,
        )
 
    except CandidateStateValidationError as exc:
        assert (
            "'solid_volume' must be greater than zero"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Strict completed-state validation accepted "
            "unresolved physical properties."
        )
 
    # --------------------------------------------------
    # Collection error retains candidate position
    # --------------------------------------------------
 
    invalid_second_candidate = replace(
        valid_candidate,
        mass=float("nan"),
    )
 
    try:
        validate_completed_candidates(
            (
                valid_candidate,
                invalid_second_candidate,
            ),
            require_physical_properties=True,
        )
 
    except CandidateStateValidationError as exc:
        assert "Candidate 2 is invalid" in str(exc)
 
        assert "'mass' must be finite" in str(exc)
 
    else:
        raise AssertionError(
            "Strict collection validation accepted an "
            "invalid physical candidate."
        )
 
    print(
        "ALL CANDIDATE PHYSICAL STATE "
        "VALIDATION CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()