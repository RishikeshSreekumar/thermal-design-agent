"""
Regression checks for the common convection-state model.
"""
 
from models.convection_state import ConvectionState
 
 
def expect_value_error(
    factory,
    expected_message: str,
) -> None:
 
    try:
        factory()
 
    except ValueError as error:
        assert expected_message in str(error)
 
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Forced convection
    # --------------------------------------------------
 
    forced = ConvectionState(
        mode="forced",
        nusselt_number=12.4,
        heat_transfer_coefficient=82.5,
        characteristic_length=0.00462,
        correlation_name="internal_forced_convection",
        reynolds_number=1450.0,
        prandtl_number=0.71,
    )
 
    assert forced.mode == "forced"
    assert forced.reynolds_number == 1450.0
    assert forced.rayleigh_number is None
    assert forced.grashof_number is None
 
    # --------------------------------------------------
    # Natural convection
    # --------------------------------------------------
 
    natural = ConvectionState(
        mode="natural",
        nusselt_number=8.2,
        heat_transfer_coefficient=6.4,
        characteristic_length=0.05,
        correlation_name="natural_convection",
        rayleigh_number=2.5e6,
        grashof_number=3.52e6,
        prandtl_number=0.71,
    )
 
    assert natural.mode == "natural"
    assert natural.reynolds_number is None
    assert natural.rayleigh_number == 2.5e6
 
    # --------------------------------------------------
    # Validation
    # --------------------------------------------------
 
    expect_value_error(
        lambda: ConvectionState(
            mode="invalid",
            nusselt_number=1.0,
            heat_transfer_coefficient=5.0,
            characteristic_length=0.05,
            correlation_name="test",
        ),
        "'mode' must be either 'forced' or 'natural'",
    )
 
    expect_value_error(
        lambda: ConvectionState(
            mode="natural",
            nusselt_number=0.0,
            heat_transfer_coefficient=5.0,
            characteristic_length=0.05,
            correlation_name="test",
        ),
        "'nusselt_number' must be greater than zero",
    )
 
    expect_value_error(
        lambda: ConvectionState(
            mode="natural",
            nusselt_number=5.0,
            heat_transfer_coefficient=0.0,
            characteristic_length=0.05,
            correlation_name="test",
        ),
        "'heat_transfer_coefficient' must be greater",
    )
 
    expect_value_error(
        lambda: ConvectionState(
            mode="natural",
            nusselt_number=5.0,
            heat_transfer_coefficient=5.0,
            characteristic_length=0.0,
            correlation_name="test",
        ),
        "'characteristic_length' must be greater",
    )
 
    expect_value_error(
        lambda: ConvectionState(
            mode="natural",
            nusselt_number=5.0,
            heat_transfer_coefficient=5.0,
            characteristic_length=0.05,
            correlation_name="",
        ),
        "'correlation_name' must not be empty",
    )
 
    expect_value_error(
        lambda: ConvectionState(
            mode="natural",
            nusselt_number=5.0,
            heat_transfer_coefficient=5.0,
            characteristic_length=0.05,
            correlation_name="test",
            rayleigh_number=-1.0,
        ),
        "'rayleigh_number' cannot be negative",
    )
 
    print(
        "ALL CONVECTION STATE CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()