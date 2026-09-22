"""
Regression tests for pressure-drop calculations.
"""
 
from physics.pressure_drop import (
    channel_pressure_drop,
    darcy_friction_factor_laminar,
    darcy_friction_factor_transition,
    darcy_friction_factor_turbulent,
    entrance_pressure_drop,
    exit_pressure_drop,
    pumping_power,
    select_darcy_friction_factor,
    total_pressure_drop,
)
 
 
def test_laminar_friction_factor() -> None:
    reynolds_number = 1000.0
 
    result = darcy_friction_factor_laminar(
        reynolds_number=reynolds_number,
    )
 
    expected = 64.0 / reynolds_number
 
    assert abs(result - expected) < 1e-12
 
 
def test_turbulent_friction_factor() -> None:
    reynolds_number = 10000.0
 
    result = darcy_friction_factor_turbulent(
        reynolds_number=reynolds_number,
    )
 
    expected = (
        0.3164
        / reynolds_number ** 0.25
    )
 
    assert abs(result - expected) < 1e-12
 
 
def test_transition_friction_factor_bounds() -> None:
    result = darcy_friction_factor_transition(
        reynolds_number=3000.0,
    )
 
    laminar_limit = (
        darcy_friction_factor_laminar(
            reynolds_number=2300.0,
        )
    )
 
    turbulent_limit = (
        darcy_friction_factor_turbulent(
            reynolds_number=4000.0,
        )
    )
 
    assert min(
        laminar_limit,
        turbulent_limit,
    ) <= result <= max(
        laminar_limit,
        turbulent_limit,
    )
 
 
def test_friction_factor_selection() -> None:
    laminar_result = (
        select_darcy_friction_factor(
            reynolds_number=1000.0,
        )
    )
 
    transition_result = (
        select_darcy_friction_factor(
            reynolds_number=3000.0,
        )
    )
 
    turbulent_result = (
        select_darcy_friction_factor(
            reynolds_number=10000.0,
        )
    )
 
    assert laminar_result > 0.0
    assert transition_result > 0.0
    assert turbulent_result > 0.0
 
 
def test_channel_pressure_drop_is_positive() -> None:
    result = channel_pressure_drop(
        reynolds_number=1500.0,
        channel_length=0.100,
        hydraulic_diameter=0.004,
        air_density=1.164,
        channel_velocity=5.0,
    )
 
    assert result > 0.0
 
 
def test_minor_losses_are_positive() -> None:
    entrance_result = entrance_pressure_drop(
        loss_coefficient=0.5,
        air_density=1.164,
        channel_velocity=5.0,
    )
 
    exit_result = exit_pressure_drop(
        loss_coefficient=1.0,
        air_density=1.164,
        channel_velocity=5.0,
    )
 
    assert entrance_result > 0.0
    assert exit_result > entrance_result
 
 
def test_total_pressure_drop_is_component_sum() -> None:
    reynolds_number = 1500.0
    channel_length = 0.100
    hydraulic_diameter = 0.004
    air_density = 1.164
    channel_velocity = 5.0
    entrance_loss_coefficient = 0.5
    exit_loss_coefficient = 1.0
 
    channel_result = channel_pressure_drop(
        reynolds_number=reynolds_number,
        channel_length=channel_length,
        hydraulic_diameter=hydraulic_diameter,
        air_density=air_density,
        channel_velocity=channel_velocity,
    )
 
    entrance_result = entrance_pressure_drop(
        loss_coefficient=(
            entrance_loss_coefficient
        ),
        air_density=air_density,
        channel_velocity=channel_velocity,
    )
 
    exit_result = exit_pressure_drop(
        loss_coefficient=(
            exit_loss_coefficient
        ),
        air_density=air_density,
        channel_velocity=channel_velocity,
    )
 
    total_result = total_pressure_drop(
        reynolds_number=reynolds_number,
        channel_length=channel_length,
        hydraulic_diameter=hydraulic_diameter,
        air_density=air_density,
        channel_velocity=channel_velocity,
        entrance_loss_coefficient=(
            entrance_loss_coefficient
        ),
        exit_loss_coefficient=(
            exit_loss_coefficient
        ),
    )
 
    expected = (
        channel_result
        + entrance_result
        + exit_result
    )
 
    assert abs(total_result - expected) < 1e-12
 
 
def test_pumping_power_relationship() -> None:
    pressure_drop = 80.0
    volumetric_flow_rate = 0.010
 
    result = pumping_power(
        total_pressure_drop=pressure_drop,
        volumetric_flow_rate=(
            volumetric_flow_rate
        ),
    )
 
    expected = (
        pressure_drop
        * volumetric_flow_rate
    )
 
    assert abs(result - expected) < 1e-12
 
 
def test_invalid_inputs_are_rejected() -> None:
    try:
        darcy_friction_factor_laminar(
            reynolds_number=0.0,
        )
 
    except ValueError:
        pass
 
    else:
        raise AssertionError(
            "Zero Reynolds number was not rejected."
        )
 
    try:
        pumping_power(
            total_pressure_drop=-1.0,
            volumetric_flow_rate=0.010,
        )
 
    except ValueError:
        pass
 
    else:
        raise AssertionError(
            "Negative pressure drop was not rejected."
        )
 
 
if __name__ == "__main__":
    test_laminar_friction_factor()
    test_turbulent_friction_factor()
    test_transition_friction_factor_bounds()
    test_friction_factor_selection()
    test_channel_pressure_drop_is_positive()
    test_minor_losses_are_positive()
    test_total_pressure_drop_is_component_sum()
    test_pumping_power_relationship()
    test_invalid_inputs_are_rejected()
 
    print("ALL PRESSURE DROP CHECKS PASSED")
 