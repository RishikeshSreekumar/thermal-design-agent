"""
Regression checks for NaturalConvectionSolver.
"""
 
from core.natural_convection_solver import (
    NaturalConvectionSolver,
)
from models.convection_state import ConvectionState
 
 
def main() -> None:
 
    state = NaturalConvectionSolver.solve(
        surface_temperature_c=80.0,
        ambient_temperature_c=30.0,
        characteristic_length=0.05,
    )
 
    assert isinstance(
        state,
        ConvectionState,
    )
 
    assert state.mode == "natural"
 
    assert (
        state.correlation_name
        == "churchill_chu_vertical_plate"
    )
 
    assert state.reynolds_number is None
 
    assert state.grashof_number is not None
    assert state.grashof_number > 0
 
    assert state.rayleigh_number is not None
    assert state.rayleigh_number > 0
 
    assert state.prandtl_number is not None
    assert state.prandtl_number > 0
 
    assert state.nusselt_number > 0
 
    assert (
        state.heat_transfer_coefficient
        > 0
    )
 
    assert (
        state.characteristic_length
        == 0.05
    )
 
    # --------------------------------------------------
    # Invalid thermal boundary condition
    # --------------------------------------------------
 
    try:
        NaturalConvectionSolver.solve(
            surface_temperature_c=30.0,
            ambient_temperature_c=30.0,
            characteristic_length=0.05,
        )
 
    except ValueError as error:
        assert (
            "Surface temperature must be greater "
            "than ambient temperature"
            in str(error)
        )
 
    else:
        raise AssertionError(
            "Equal surface and ambient temperatures "
            "were not rejected."
        )
 
    # --------------------------------------------------
    # Invalid characteristic length
    # --------------------------------------------------
 
    try:
        NaturalConvectionSolver.solve(
            surface_temperature_c=80.0,
            ambient_temperature_c=30.0,
            characteristic_length=0.0,
        )
 
    except ValueError as error:
        assert (
            "Characteristic length must be greater "
            "than zero"
            in str(error)
        )
 
    else:
        raise AssertionError(
            "Zero characteristic length was not rejected."
        )
 
    print(
        "ALL NATURAL CONVECTION SOLVER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()