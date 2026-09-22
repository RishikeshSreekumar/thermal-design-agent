"""
Regression test for fan-coupled optimizer mode.
"""
 
import math
 
from core.thermal_optimizer import ThermalOptimizer
 
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    FanSpecification,
    Requirements,
)
 
 
def main() -> None:
 
    requirements = EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="forced",
        requirements=Requirements(
            heat_load=165.0,
            ambient_temperature=30.0,
            air_velocity=None,
        ),
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=8.0,
        ),
        fan=FanSpecification(
            fan_name="demo_120mm",
        ),
    )
 
    optimizer = ThermalOptimizer()
 
    result = optimizer.optimize_with_details(
        requirements
    )
 
    assert result.has_feasible_design, (
        "Fan-coupled optimizer did not find a "
        "feasible design."
    )
 
    assert result.best_result is not None
 
    assert result.feasible_candidate_count > 0
 
    for index, candidate in enumerate(
        result.candidates,
        start=1,
    ):
 
        assert math.isfinite(
            candidate.approach_velocity
        ), (
            f"Candidate {index}: approach velocity "
            "is not finite."
        )
 
        assert candidate.approach_velocity > 0.0, (
            f"Candidate {index}: approach velocity "
            "must be positive."
        )
 
        assert candidate.channel_velocity > 0.0, (
            f"Candidate {index}: channel velocity "
            "must be positive."
        )
 
        assert candidate.reynolds_number > 0.0, (
            f"Candidate {index}: Reynolds number "
            "must be positive."
        )
 
        assert candidate.friction_factor > 0.0, (
            f"Candidate {index}: friction factor "
            "must be positive."
        )
 
        assert candidate.pressure_drop > 0.0, (
            f"Candidate {index}: pressure drop "
            "must be positive."
        )
 
        assert candidate.pumping_power > 0.0, (
            f"Candidate {index}: pumping power "
            "must be positive."
        )
 
        assert candidate.thermal_resistance > 0.0, (
            f"Candidate {index}: thermal resistance "
            "must be positive."
        )
 
    print(
        "ALL FAN-COUPLED OPTIMIZER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()
 