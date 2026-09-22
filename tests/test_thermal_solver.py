"""
Regression checks for core.thermal_solver.
"""

from core.thermal_solver import ThermalSolver
from models.design_candidate import DesignCandidate
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
from models.thermal_state import ThermalState
from physics.flow_network import FlowNetworkResult
 
 
def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-9,
) -> None:
    """
    Assert that two floating-point values are sufficiently
    close.
    """
 
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"Expected {expected}, received {actual}."
        )
 
 
def main() -> None:
    """
    Run deterministic thermal-solver checks.
    """
 
    candidate = DesignCandidate(
        base_thickness=3.0,
        fin_thickness=0.8,
        fin_height=8.0,
        fin_spacing=1.6,
        fin_count=21,
        total_height=11.0,
 
        gross_frontal_area=0.0,
        open_flow_area=0.0,
        blockage_ratio=0.0,
        approach_velocity=0.0,
        channel_velocity=0.0,
 
        reynolds_number=0.0,
        nusselt_number=0.0,
        heat_transfer_coefficient=0.0,
        friction_factor=0.0,
        pressure_drop=0.0,
        pumping_power=0.0,
 
        thermal_resistance=0.0,
        estimated_base_temperature=0.0,
    )
 
    flow_state = FlowNetworkResult(
        volumetric_flow_rate=0.01,
    
        approach_velocity=5.0,
        channel_velocity=7.8125,
    
        gross_flow_area=0.0004,
        open_flow_area=0.000256,
        blockage_ratio=0.36,
    
        hydraulic_diameter=(
            0.0026666666666666666
        ),
    
        reynolds_number=1295.405982905983,
        friction_factor=0.049405,
    
        pressure_drop=86.189941,
        pumping_power=0.86189941,
    )
 
    requirements = EngineeringRequirements(
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
            max_height=30.0,
        ),
    )
 
    thermal_state = ThermalSolver.solve(
        candidate=candidate,
        flow_state=flow_state,
        requirements=requirements,
        air_conductivity=0.0263,
        prandtl_number=0.71,
        material_conductivity=201.0,
    )
 
    if not isinstance(
        thermal_state,
        ThermalState,
    ):
        raise AssertionError(
            "ThermalSolver.solve() must return "
            "ThermalState."
        )
 
    assert_close(
        thermal_state.nusselt_number,
        7.54,
    )
 
    assert_close(
        thermal_state.heat_transfer_coefficient,
        74.36325,
    )
 
    if thermal_state.total_surface_area <= 0:
        raise AssertionError(
            "Total surface area must be positive."
        )
 
    if not (
        0 < thermal_state.fin_efficiency <= 1
    ):
        raise AssertionError(
            "Fin efficiency must be greater than zero "
            "and no greater than one."
        )
 
    if thermal_state.thermal_resistance <= 0:
        raise AssertionError(
            "Thermal resistance must be positive."
        )
 
    expected_base_temperature = (
        30.0
        + 165.0
        * thermal_state.thermal_resistance
    )
 
    assert_close(
        thermal_state.estimated_base_temperature,
        expected_base_temperature,
    )
 
    print(
        "ALL THERMAL SOLVER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()