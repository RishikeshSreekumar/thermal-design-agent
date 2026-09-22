"""
pressure_drop.py
 
Pressure-drop models for internal flow through heat sink channels.
"""
 
import math
 
 
def darcy_friction_factor_laminar(
    reynolds_number: float,
) -> float:
    """
    Calculate the Darcy friction factor for fully developed
    laminar internal flow.
 
    f = 64 / Re
    """
 
    if reynolds_number <= 0:
        raise ValueError(
            "Reynolds number must be greater than zero."
        )
 
    return 64.0 / reynolds_number
 
 
def darcy_friction_factor_turbulent(
    reynolds_number: float,
) -> float:
    """
    Calculate the Darcy friction factor for smooth turbulent
    internal flow using the Blasius correlation.
 
    f = 0.3164 / Re^0.25
 
    Valid approximately for:
    4,000 <= Re <= 100,000
    """
 
    if reynolds_number < 4000.0:
        raise ValueError(
            "Turbulent friction-factor correlation requires "
            "Reynolds number >= 4000."
        )
 
    return 0.3164 / reynolds_number ** 0.25
 
 
def darcy_friction_factor_transition(
    reynolds_number: float,
) -> float:
    """
    Estimate the Darcy friction factor in the transition region
    by linearly interpolating between the laminar value at Re=2300
    and the turbulent value at Re=4000.
    """
 
    if not 2300.0 <= reynolds_number < 4000.0:
        raise ValueError(
            "Transition friction-factor model requires "
            "2300 <= Reynolds number < 4000."
        )
 
    laminar_factor_at_2300 = (
        darcy_friction_factor_laminar(2300.0)
    )
 
    turbulent_factor_at_4000 = (
        darcy_friction_factor_turbulent(4000.0)
    )
 
    interpolation_factor = (
        (reynolds_number - 2300.0)
        / (4000.0 - 2300.0)
    )
 
    return (
        laminar_factor_at_2300
        + interpolation_factor
        * (
            turbulent_factor_at_4000
            - laminar_factor_at_2300
        )
    )
 
 
def select_darcy_friction_factor(
    reynolds_number: float,
) -> float:
    """
    Select and evaluate the Darcy friction factor according to
    the Reynolds-number flow regime.
    """
 
    if reynolds_number <= 0:
        raise ValueError(
            "Reynolds number must be greater than zero."
        )
 
    if reynolds_number < 2300.0:
        return darcy_friction_factor_laminar(
            reynolds_number
        )
 
    if reynolds_number < 4000.0:
        return darcy_friction_factor_transition(
            reynolds_number
        )
 
    return darcy_friction_factor_turbulent(
        reynolds_number
    )

def channel_pressure_drop(
    reynolds_number: float,
    channel_length: float,
    hydraulic_diameter: float,
    air_density: float,
    channel_velocity: float,
) -> float:
    """
    Calculate the pressure drop due to wall friction
    using the Darcy-Weisbach equation.
 
    Returns
    -------
    Pressure drop (Pa)
    """
 
    if channel_length <= 0:
        raise ValueError(
            "Channel length must be greater than zero."
        )
 
    if hydraulic_diameter <= 0:
        raise ValueError(
            "Hydraulic diameter must be greater than zero."
        )
 
    if air_density <= 0:
        raise ValueError(
            "Air density must be greater than zero."
        )
 
    friction_factor = select_darcy_friction_factor(
        reynolds_number
    )
 
    dynamic_pressure = (
        air_density
        * channel_velocity ** 2
        / 2.0
    )
 
    return (
        friction_factor
        * (channel_length / hydraulic_diameter)
        * dynamic_pressure
    )

def entrance_pressure_drop(
    loss_coefficient: float,
    air_density: float,
    channel_velocity: float,
) -> float:
    """
    Calculate the pressure loss at the channel entrance.
 
    ΔP = K * ρ * V² / 2
    """
 
    if loss_coefficient < 0:
        raise ValueError(
            "Loss coefficient cannot be negative."
        )
 
    dynamic_pressure = (
        air_density
        * channel_velocity ** 2
        / 2.0
    )
 
    return loss_coefficient * dynamic_pressure
 
 
def exit_pressure_drop(
    loss_coefficient: float,
    air_density: float,
    channel_velocity: float,
) -> float:
    """
    Calculate the pressure loss at the channel exit.
 
    ΔP = K * ρ * V² / 2
    """
 
    if loss_coefficient < 0:
        raise ValueError(
            "Loss coefficient cannot be negative."
        )
 
    dynamic_pressure = (
        air_density
        * channel_velocity ** 2
        / 2.0
    )
 
    return loss_coefficient * dynamic_pressure

def total_pressure_drop(
    reynolds_number: float,
    channel_length: float,
    hydraulic_diameter: float,
    air_density: float,
    channel_velocity: float,
    entrance_loss_coefficient: float = 0.5,
    exit_loss_coefficient: float = 1.0,
) -> float:
    """
    Calculate the total pressure drop across the heat sink.
    """
 
    channel_dp = channel_pressure_drop(
        reynolds_number,
        channel_length,
        hydraulic_diameter,
        air_density,
        channel_velocity,
    )
 
    entrance_dp = entrance_pressure_drop(
        entrance_loss_coefficient,
        air_density,
        channel_velocity,
    )
 
    exit_dp = exit_pressure_drop(
        exit_loss_coefficient,
        air_density,
        channel_velocity,
    )
 
    return (
        entrance_dp
        + channel_dp
        + exit_dp
    )

def pumping_power(
    total_pressure_drop: float,
    volumetric_flow_rate: float,
) -> float:
    """
    Calculate the pumping power required to overcome
    the total pressure drop.
 
    P = ΔP × Q
 
    Parameters
    ----------
    total_pressure_drop : float
        Pressure drop (Pa)
 
    volumetric_flow_rate : float
        Flow rate (m³/s)
 
    Returns
    -------
    Pumping power (W)
    """
 
    if total_pressure_drop < 0:
        raise ValueError(
            "Pressure drop cannot be negative."
        )
 
    if volumetric_flow_rate < 0:
        raise ValueError(
            "Volumetric flow rate cannot be negative."
        )
 
    return (
        total_pressure_drop
        * volumetric_flow_rate
    )
 
 