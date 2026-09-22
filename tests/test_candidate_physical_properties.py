"""
Regression checks for solid-volume and mass preservation
inside optimizer-generated DesignCandidate objects.
 
The regression verifies that:
 
- Every completed optimizer candidate has positive,
  finite solid volume and mass.
- The preserved volume matches the deterministic
  plate-fin solid-geometry model.
- The preserved mass matches volume multiplied by the
  selected material density.
- Existing legacy DesignCandidate constructors remain
  backward compatible.
"""
 
import math
 
from core.candidate_state_validator import (
    validate_completed_candidates,
)
from core.thermal_optimizer import ThermalOptimizer
from manufacturing.process_database import (
    get_process_capability,
)
from models.design_candidate import DesignCandidate
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
from physics.mass_model import component_mass
from physics.solid_geometry import (
    plate_fin_heat_sink_volume,
)
 
 
def create_requirements(
) -> EngineeringRequirements:
    """
    Create a deliberately small fixed-velocity design
    envelope for the focused regression.
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
 
 
def main() -> None:
    requirements = create_requirements()
 
    capability = get_process_capability(
        "al6063_t5_extrusion"
    )
 
    optimizer = ThermalOptimizer()
 
    optimization_result = (
        optimizer.optimize_with_details(
            requirements
        )
    )
 
    assert optimization_result.has_feasible_design
 
    assert optimization_result.candidates

    validate_completed_candidates(
        tuple(
            optimization_result.candidates
        ),
        require_physical_properties=True,
    )
 
    for index, candidate in enumerate(
        optimization_result.candidates,
        start=1,
    ):
        assert math.isfinite(
            candidate.solid_volume
        ), (
            f"Candidate {index}: solid volume "
            "must be finite."
        )
 
        assert candidate.solid_volume > 0.0, (
            f"Candidate {index}: solid volume "
            "must be positive."
        )
 
        assert math.isfinite(
            candidate.mass
        ), (
            f"Candidate {index}: mass must be finite."
        )
 
        assert candidate.mass > 0.0, (
            f"Candidate {index}: mass must be positive."
        )
 
        expected_volume = (
            plate_fin_heat_sink_volume(
                base_length_mm=(
                    requirements
                    .constraints
                    .base_length
                ),
                base_width_mm=(
                    requirements
                    .constraints
                    .base_width
                ),
                base_thickness_mm=(
                    candidate.base_thickness
                ),
                fin_height_mm=(
                    candidate.fin_height
                ),
                fin_thickness_mm=(
                    candidate.fin_thickness
                ),
                fin_count=candidate.fin_count,
            )
        )
 
        assert math.isclose(
            candidate.solid_volume,
            expected_volume,
            rel_tol=0.0,
            abs_tol=1e-15,
        ), (
            f"Candidate {index}: preserved solid "
            "volume does not match the geometry model."
        )
 
        expected_mass = component_mass(
            expected_volume,
            capability.material,
        )
 
        assert math.isclose(
            candidate.mass,
            expected_mass,
            rel_tol=0.0,
            abs_tol=1e-12,
        ), (
            f"Candidate {index}: preserved mass does "
            "not match the mass model."
        )
 
        assert math.isclose(
            candidate.mass,
            (
                candidate.solid_volume
                * capability.material.density
            ),
            rel_tol=0.0,
            abs_tol=1e-12,
        )
 
    # --------------------------------------------------
    # Selected candidate preserves the same physical
    # state as the candidate collection.
    # --------------------------------------------------
 
    selected_candidate = (
        optimization_result.selected_candidate
    )
 
    assert selected_candidate is not None
 
    assert selected_candidate in (
        optimization_result.candidates
    )
 
    assert selected_candidate.solid_volume > 0.0
    assert selected_candidate.mass > 0.0
 
    # --------------------------------------------------
    # Established reference design
    # --------------------------------------------------
 
    matching_candidates = [
        candidate
        for candidate in optimization_result.candidates
        if (
            candidate.base_thickness == 3.0
            and candidate.fin_height == 5.0
            and candidate.fin_thickness == 0.8
            and candidate.fin_spacing == 1.6
            and candidate.fin_count == 21
        )
    ]
 
    assert len(matching_candidates) == 1
 
    reference_candidate = matching_candidates[0]
 
    expected_reference_volume = (
        plate_fin_heat_sink_volume(
            base_length_mm=50.0,
            base_width_mm=50.0,
            base_thickness_mm=3.0,
            fin_height_mm=5.0,
            fin_thickness_mm=0.8,
            fin_count=21,
        )
    )
 
    expected_reference_mass = (
        component_mass(
            expected_reference_volume,
            capability.material,
        )
    )
 
    assert math.isclose(
        reference_candidate.solid_volume,
        expected_reference_volume,
        rel_tol=0.0,
        abs_tol=1e-15,
    )
 
    assert math.isclose(
        reference_candidate.mass,
        expected_reference_mass,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Backward-compatible constructor
    # --------------------------------------------------
 
    legacy_candidate = DesignCandidate(
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
 
        reynolds_number=1295.0,
        nusselt_number=7.54,
        heat_transfer_coefficient=74.0,
 
        friction_factor=0.049,
        pressure_drop=86.0,
        pumping_power=0.17,
 
        thermal_resistance=0.68,
        estimated_base_temperature=142.0,
    )
 
    assert legacy_candidate.solid_volume == 0.0
    assert legacy_candidate.mass == 0.0
 
    print(
        "ALL CANDIDATE PHYSICAL PROPERTY "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()