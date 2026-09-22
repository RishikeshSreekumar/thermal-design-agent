"""
Regression checks for the forced-convection solver.
"""
 
from core.forced_convection_solver import (
    ForcedConvectionSolver,
)
from models.convection_state import ConvectionState
from physics.flow_network import FlowNetworkResult
 
 
def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-9,
) -> None:
 
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"Expected {expected}, received {actual}."
        )
 
 
def main() -> None:
 
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
 
    state = ForcedConvectionSolver.solve(
        flow_state=flow_state,
        air_conductivity=0.0263,
        prandtl_number=0.71,
    )
 
    assert isinstance(
        state,
        ConvectionState,
    )
 
    assert state.mode == "forced"
 
    assert_close(
        state.nusselt_number,
        7.54,
    )
 
    assert_close(
        state.heat_transfer_coefficient,
        74.36325,
    )
 
    assert_close(
        state.characteristic_length,
        flow_state.hydraulic_diameter,
    )
 
    assert_close(
        state.reynolds_number,
        flow_state.reynolds_number,
    )
 
    assert_close(
        state.prandtl_number,
        0.71,
    )
 
    assert state.rayleigh_number is None
    assert state.grashof_number is None
 
    print(
        "ALL FORCED CONVECTION SOLVER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()