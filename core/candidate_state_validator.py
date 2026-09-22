"""
candidate_state_validator.py
 
Validation boundary for fully evaluated thermal-design
candidates.
 
Geometry placeholder candidates are intentionally allowed
to contain unresolved zero or infinite result fields before
airflow and thermal evaluation.
 
This validator is only for completed candidates that are
about to enter optimization-objective analysis and
candidate selection.
"""
 
import math
 
from models.design_candidate import DesignCandidate
 
 
class CandidateStateValidationError(ValueError):
    """
    Raised when a completed DesignCandidate contains an
    incomplete, non-finite, inconsistent, or physically
    invalid evaluated state.
    """

def validate_candidate_physical_properties(
    candidate: DesignCandidate,
) -> None:
    """
    Validate the resolved physical material properties of
    one evaluated design candidate.
 
    This validation is intentionally separate from the
    default completed-candidate contract until physical
    properties become mandatory selection inputs.
 
    Raises
    ------
    CandidateStateValidationError
        If solid volume or mass is non-finite or not
        greater than zero.
    """
 
    if not isinstance(
        candidate,
        DesignCandidate,
    ):
        raise CandidateStateValidationError(
            "Physical-property validation requires a "
            "DesignCandidate."
        )
 
    physical_properties = {
        "solid_volume": candidate.solid_volume,
        "mass": candidate.mass,
    }
 
    for field_name, value in (
        physical_properties.items()
    ):
        if not math.isfinite(value):
            raise CandidateStateValidationError(
                f"'{field_name}' must be finite."
            )
 
        if value <= 0.0:
            raise CandidateStateValidationError(
                f"'{field_name}' must be greater "
                "than zero."
            ) 
 
def validate_completed_candidate(
    candidate: DesignCandidate,
    require_physical_properties: bool = False,
) -> None:
    """
    Validate one fully evaluated thermal-design candidate.
 
    Physical material properties are validated only when
    require_physical_properties is True. This preserves
    compatibility with legacy completed-candidate fixtures
    created before solid volume and mass were introduced.
 
    Successful validation returns None.
 
    Raises
    ------
    CandidateStateValidationError
        If any required geometry, airflow, hydraulic, or
        thermal value is invalid.
    """
 
    if not isinstance(
        candidate,
        DesignCandidate,
    ):
        raise CandidateStateValidationError(
            "Completed candidate must be a "
            "DesignCandidate."
        )
    
    if not isinstance(
        require_physical_properties,
        bool,
    ):
        raise CandidateStateValidationError(
            "'require_physical_properties' must be "
            "a boolean."
        )
 
    _validate_finite_values(candidate)
    _validate_geometry(candidate)
 
    if candidate.convection_mode == "forced":
        _validate_flow_geometry(candidate)
        _validate_hydraulic_state(candidate)
 
        if (
            candidate
            .radiative_heat_transfer_coefficient
            != 0.0
        ):
            raise CandidateStateValidationError(
                "'radiative_heat_transfer_coefficient' "
                "must be zero for the current "
                "forced-convection model."
            )
 
    elif candidate.convection_mode == "natural":
        _validate_natural_convection_state(
            candidate
        )
 
    else:
        raise CandidateStateValidationError(
            "'convection_mode' must be either "
            "'forced' or 'natural'."
        )
 
    _validate_thermal_state(candidate)
 
    if require_physical_properties:
        validate_candidate_physical_properties(
            candidate
        )
 
 
def validate_completed_candidates(
    candidates: tuple[
        DesignCandidate,
        ...
    ],
    require_physical_properties: bool = False,
) -> None:
    """
    Validate every candidate in a completed candidate
    collection.
    """
    if not isinstance(
        require_physical_properties,
        bool,
    ):
        raise CandidateStateValidationError(
            "'require_physical_properties' must be "
            "a boolean."
        )

    if not candidates:
        raise CandidateStateValidationError(
            "At least one completed design candidate is "
            "required."
        )
 
    for index, candidate in enumerate(
        candidates,
        start=1,
    ):
        try:
            validate_completed_candidate(
                candidate,
                require_physical_properties=(
                    require_physical_properties
                ),
            )
 
        except CandidateStateValidationError as exc:
            raise CandidateStateValidationError(
                f"Candidate {index} is invalid: {exc}"
            ) from exc
 
 
def _validate_finite_values(
    candidate: DesignCandidate,
) -> None:
    """
    Ensure every floating-point candidate field required
    for selection contains a finite value.
    """
 
    finite_values = {
        "base_thickness": (
            candidate.base_thickness
        ),
        "fin_thickness": (
            candidate.fin_thickness
        ),
        "fin_height": candidate.fin_height,
        "fin_spacing": candidate.fin_spacing,
        "total_height": candidate.total_height,
        "gross_frontal_area": (
            candidate.gross_frontal_area
        ),
        "open_flow_area": (
            candidate.open_flow_area
        ),
        "blockage_ratio": (
            candidate.blockage_ratio
        ),
        "approach_velocity": (
            candidate.approach_velocity
        ),
        "channel_velocity": (
            candidate.channel_velocity
        ),
        "hydraulic_diameter": (
            candidate.hydraulic_diameter
        ),
        "reynolds_number": (
            candidate.reynolds_number
        ),
        "nusselt_number": (
            candidate.nusselt_number
        ),
        "heat_transfer_coefficient": (
            candidate
            .heat_transfer_coefficient
        ),
        "radiative_heat_transfer_coefficient": (
            candidate
            .radiative_heat_transfer_coefficient
        ),
        "friction_factor": (
            candidate.friction_factor
        ),
        "pressure_drop": (
            candidate.pressure_drop
        ),
        "pumping_power": (
            candidate.pumping_power
        ),
        "thermal_resistance": (
            candidate.thermal_resistance
        ),
        "estimated_base_temperature": (
            candidate
            .estimated_base_temperature
        ),
    }
 
    for field_name, value in finite_values.items():
        if not math.isfinite(value):
            raise CandidateStateValidationError(
                f"'{field_name}' must be finite."
            )
 
 
def _validate_geometry(
    candidate: DesignCandidate,
) -> None:
    """
    Validate completed candidate geometry.
    """
 
    positive_values = {
        "base_thickness": (
            candidate.base_thickness
        ),
        "fin_thickness": (
            candidate.fin_thickness
        ),
        "fin_height": candidate.fin_height,
        "fin_spacing": candidate.fin_spacing,
        "total_height": candidate.total_height,
    }
 
    for field_name, value in positive_values.items():
        if value <= 0.0:
            raise CandidateStateValidationError(
                f"'{field_name}' must be greater "
                "than zero."
            )
 
    if candidate.fin_count < 2:
        raise CandidateStateValidationError(
            "'fin_count' must be at least 2."
        )
 
    calculated_total_height = (
        candidate.base_thickness
        + candidate.fin_height
    )
 
    if not math.isclose(
        candidate.total_height,
        calculated_total_height,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise CandidateStateValidationError(
            "'total_height' must equal base thickness "
            "plus fin height."
        )
 
 
def _validate_flow_geometry(
    candidate: DesignCandidate,
) -> None:
    """
    Validate completed candidate flow geometry.
    """
 
    if candidate.gross_frontal_area <= 0.0:
        raise CandidateStateValidationError(
            "'gross_frontal_area' must be greater "
            "than zero."
        )
 
    if candidate.open_flow_area <= 0.0:
        raise CandidateStateValidationError(
            "'open_flow_area' must be greater than zero."
        )
 
    if (
        candidate.open_flow_area
        > candidate.gross_frontal_area
    ):
        raise CandidateStateValidationError(
            "'open_flow_area' cannot exceed "
            "'gross_frontal_area'."
        )
 
    if not (
        0.0
        <= candidate.blockage_ratio
        <= 1.0
    ):
        raise CandidateStateValidationError(
            "'blockage_ratio' must lie between "
            "0 and 1."
        )
 
    if candidate.approach_velocity <= 0.0:
        raise CandidateStateValidationError(
            "'approach_velocity' must be greater "
            "than zero."
        )
 
    if candidate.channel_velocity <= 0.0:
        raise CandidateStateValidationError(
            "'channel_velocity' must be greater "
            "than zero."
        )
 
 
def _validate_hydraulic_state(
    candidate: DesignCandidate,
) -> None:
    """
    Validate the completed hydraulic result.
    """
 
    if candidate.hydraulic_diameter <= 0.0:
        raise CandidateStateValidationError(
            "'hydraulic_diameter' must be greater "
            "than zero."
        )
 
    if candidate.reynolds_number <= 0.0:
        raise CandidateStateValidationError(
            "'reynolds_number' must be greater "
            "than zero."
        )
 
    if candidate.friction_factor <= 0.0:
        raise CandidateStateValidationError(
            "'friction_factor' must be greater "
            "than zero."
        )
 
    if candidate.pressure_drop < 0.0:
        raise CandidateStateValidationError(
            "'pressure_drop' cannot be negative."
        )
 
    if candidate.pumping_power < 0.0:
        raise CandidateStateValidationError(
            "'pumping_power' cannot be negative."
        )


def _validate_natural_convection_state(
    candidate: DesignCandidate,
) -> None:
    """
    Validate non-applicable forced-flow fields for a
    completed natural-convection candidate.
 
    Natural convection has no imposed approach velocity,
    fan pressure drop, pumping power, or Reynolds-number
    flow state in the current model.
    """
 
    zero_fields = {
        "approach_velocity": (
            candidate.approach_velocity
        ),
        "channel_velocity": (
            candidate.channel_velocity
        ),
        "hydraulic_diameter": (
            candidate.hydraulic_diameter
        ),
        "reynolds_number": (
            candidate.reynolds_number
        ),
        "friction_factor": (
            candidate.friction_factor
        ),
        "pressure_drop": (
            candidate.pressure_drop
        ),
        "pumping_power": (
            candidate.pumping_power
        ),
    }
 
    for field_name, value in zero_fields.items():
        if value != 0.0:
            raise CandidateStateValidationError(
                f"'{field_name}' must be zero for the "
                "current natural-convection model."
            )
 
    if candidate.gross_frontal_area <= 0.0:
        raise CandidateStateValidationError(
            "'gross_frontal_area' must be greater "
            "than zero."
        )
 
    if candidate.open_flow_area <= 0.0:
        raise CandidateStateValidationError(
            "'open_flow_area' must be greater than zero."
        )
 
    if (
        candidate.open_flow_area
        > candidate.gross_frontal_area
    ):
        raise CandidateStateValidationError(
            "'open_flow_area' cannot exceed "
            "'gross_frontal_area'."
        )
 
    if not (
        0.0
        <= candidate.blockage_ratio
        <= 1.0
    ):
        raise CandidateStateValidationError(
            "'blockage_ratio' must lie between "
            "0 and 1."
        )
 
def _validate_thermal_state(
    candidate: DesignCandidate,
) -> None:
    """
    Validate the completed convection and thermal result.
    """
 
    if candidate.nusselt_number <= 0.0:
        raise CandidateStateValidationError(
            "'nusselt_number' must be greater "
            "than zero."
        )
 
    if (
        candidate
        .heat_transfer_coefficient
        <= 0.0
    ):
        raise CandidateStateValidationError(
            "'heat_transfer_coefficient' must be "
            "greater than zero."
        )

    if (
        candidate
        .radiative_heat_transfer_coefficient
        < 0.0
    ):
        raise CandidateStateValidationError(
            "'radiative_heat_transfer_coefficient' "
            "cannot be negative."
        )
 
    if (
        candidate
        .radiative_heat_transfer_coefficient
        > candidate.heat_transfer_coefficient
    ):
        raise CandidateStateValidationError(
            "Radiative heat-transfer coefficient cannot "
            "exceed the effective heat-transfer "
            "coefficient."
        )
 
    if (
        candidate
        .convective_heat_transfer_coefficient
        <= 0.0
    ):
        raise CandidateStateValidationError(
            "Convective heat-transfer coefficient must "
            "remain greater than zero."
        )
 
    if candidate.thermal_resistance <= 0.0:
        raise CandidateStateValidationError(
            "'thermal_resistance' must be greater "
            "than zero."
        )