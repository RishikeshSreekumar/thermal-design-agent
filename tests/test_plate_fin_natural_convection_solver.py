"""
Integration regression for plate-fin natural convection.
"""
 
from core.plate_fin_natural_convection_solver import (
    PlateFinNaturalConvectionSolver,
)
from models.design_candidate import DesignCandidate
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
from models.thermal_state import ThermalState
 
 
def main() -> None:
 
    candidate = DesignCandidate(
        base_thickness=3.0,
        fin_thickness=1.0,
        fin_height=25.0,
        fin_spacing=5.0,
        fin_count=10,
        total_height=28.0,
 
        gross_frontal_area=0.001,
        open_flow_area=0.001,
        blockage_ratio=0.0,
        approach_velocity=0.0,
        channel_velocity=0.0,
 
        hydraulic_diameter=0.001,
        reynolds_number=1.0,
        nusselt_number=1.0,
        heat_transfer_coefficient=1.0,
        friction_factor=1.0,
        pressure_drop=0.0,
        pumping_power=0.0,
 
        thermal_resistance=1.0,
        estimated_base_temperature=1.0,
    )
 
    requirements = EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="natural",
 
        requirements=Requirements(
            heat_load=20.0,
            ambient_temperature=30.0,
            air_velocity=None,
        ),
 
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=30.0,
        ),
    )
 
    thermal_state = (
        PlateFinNaturalConvectionSolver.solve(
            candidate=candidate,
            requirements=requirements,
            material_conductivity=201.0,
        )
    )
 
    assert isinstance(
        thermal_state,
        ThermalState,
    )
 
    assert thermal_state.nusselt_number > 0
 
    assert (
        thermal_state.heat_transfer_coefficient
        > 0
    )
 
    assert (
        0
        < thermal_state.fin_efficiency
        <= 1
    )
 
    assert thermal_state.thermal_resistance > 0
 
    assert (
        thermal_state.estimated_base_temperature
        > 30.0
    )
 
    print(
        "Natural convection result:"
    )
 
    print(
        "Nu:",
        thermal_state.nusselt_number,
    )
 
    print(
        "h:",
        thermal_state.heat_transfer_coefficient,
    )
 
    print(
        "Rth:",
        thermal_state.thermal_resistance,
    )
 
    print(
        "Base temperature:",
        thermal_state
        .estimated_base_temperature,
    )
 
    print(
        "ALL PLATE-FIN NATURAL CONVECTION "
        "SOLVER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()