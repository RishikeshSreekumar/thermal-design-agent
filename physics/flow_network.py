"""
flow_network.py
 
High-level flow-network evaluation for a straight
plate-fin heat sink.
 
This module coordinates the existing hydraulic and
pressure-drop models. It does not define new fluid-flow
correlations.
 
Calculation sequence:
 
1. Evaluate gross frontal area.
2. Evaluate total open channel area.
3. Convert volumetric flow rate to approach velocity.
4. Calculate channel velocity using continuity.
5. Calculate hydraulic diameter.
6. Calculate Reynolds number.
7. Select the Darcy friction factor.
8. Calculate total pressure drop.
9. Calculate pumping power.
"""
 
from dataclasses import dataclass

from typing import Callable
 
from physics.flow_model import (
    blockage_ratio as calculate_blockage_ratio,
    channel_velocity as calculate_channel_velocity,
    gross_frontal_area,
    open_flow_area,
)
from physics.fluid_properties import air_properties
from physics.hydraulic_model import (
    hydraulic_diameter as calculate_hydraulic_diameter,
    reynolds_number as calculate_reynolds_number,
)
from physics.pressure_drop import (
    pumping_power as calculate_pumping_power,
    select_darcy_friction_factor,
    total_pressure_drop as calculate_total_pressure_drop,
)
 
 
@dataclass(frozen=True)
class FlowNetworkResult:
    """
    Evaluated hydraulic state of a plate-fin heat sink.
 
    All dimensional outputs use SI units.
 
    Parameters
    ----------
    volumetric_flow_rate:
        Total airflow rate entering the heat sink in m³/s.
 
    approach_velocity:
        Average velocity based on the gross frontal area
        in m/s.
 
    channel_velocity:
        Average velocity inside the open fin channels
        in m/s.
 
    gross_flow_area:
        Gross frontal area of the finned region in m².
 
    open_flow_area:
        Total open flow area through all channels in m².
 
    blockage_ratio:
        Fraction of the gross frontal area blocked by fins.
 
    hydraulic_diameter:
        Hydraulic diameter of one fin channel in m.
 
    reynolds_number:
        Reynolds number based on channel velocity and
        hydraulic diameter.
 
    friction_factor:
        Darcy friction factor selected for the calculated
        Reynolds-number regime.
 
    pressure_drop:
        Total heat-sink pressure drop in Pa.
 
    pumping_power:
        Ideal fluid pumping power in W.
    """
 
    volumetric_flow_rate: float
 
    approach_velocity: float
    channel_velocity: float
 
    gross_flow_area: float
    open_flow_area: float
    blockage_ratio: float
 
    hydraulic_diameter: float
 
    reynolds_number: float
    friction_factor: float
 
    pressure_drop: float
    pumping_power: float
 
 
def evaluate_flow_network(
    volumetric_flow_rate: float,
    base_width_mm: float,
    fin_height_mm: float,
    fin_count_value: int,
    fin_spacing_mm: float,
    channel_length_mm: float,
    air_temperature_c: float,
    entrance_loss_coefficient: float = 0.5,
    exit_loss_coefficient: float = 1.0,
) -> FlowNetworkResult:
    """
    Evaluate the flow network of a straight plate-fin
    heat sink at a specified volumetric flow rate.
 
    Parameters
    ----------
    volumetric_flow_rate:
        Total airflow rate entering the heat sink in m³/s.
 
    base_width_mm:
        Heat-sink width normal to the fin channels in mm.
 
    fin_height_mm:
        Fin height in mm.
 
    fin_count_value:
        Total number of fins.
 
    fin_spacing_mm:
        Clear spacing between adjacent fins in mm.
 
    channel_length_mm:
        Flow length through the fin channels in mm.
 
    air_temperature_c:
        Air temperature used to evaluate fluid properties
        in °C.
 
    entrance_loss_coefficient:
        Dimensionless entrance-loss coefficient.
 
    exit_loss_coefficient:
        Dimensionless exit-loss coefficient.
 
    Returns
    -------
    FlowNetworkResult
        Complete evaluated hydraulic state.
 
    Raises
    ------
    ValueError
        If the flow rate, geometry, fluid properties, or
        loss coefficients are invalid.
    """
 
    if volumetric_flow_rate <= 0:
        raise ValueError(
            "Volumetric flow rate must be greater than zero."
        )
 
    if base_width_mm <= 0:
        raise ValueError(
            "Base width must be greater than zero."
        )
 
    if fin_height_mm <= 0:
        raise ValueError(
            "Fin height must be greater than zero."
        )
 
    if fin_count_value < 2:
        raise ValueError(
            "At least two fins are required to form a flow channel."
        )
 
    if fin_spacing_mm <= 0:
        raise ValueError(
            "Fin spacing must be greater than zero."
        )
 
    if channel_length_mm <= 0:
        raise ValueError(
            "Channel length must be greater than zero."
        )
 
    if entrance_loss_coefficient < 0:
        raise ValueError(
            "Entrance-loss coefficient cannot be negative."
        )
 
    if exit_loss_coefficient < 0:
        raise ValueError(
            "Exit-loss coefficient cannot be negative."
        )
 
    gross_area = gross_frontal_area(
        base_width_mm=base_width_mm,
        fin_height_mm=fin_height_mm,
    )
 
    open_area = open_flow_area(
        fin_count_value=fin_count_value,
        fin_spacing_mm=fin_spacing_mm,
        fin_height_mm=fin_height_mm,
    )
 
    if gross_area <= 0:
        raise ValueError(
            "Calculated gross frontal area must be greater than zero."
        )
 
    if open_area <= 0:
        raise ValueError(
            "Calculated open flow area must be greater than zero."
        )
 
    if open_area > gross_area:
        raise ValueError(
            "Open flow area cannot exceed gross frontal area. "
            "Check the fin count, spacing, and base width."
        )
 
    approach_velocity = (
        volumetric_flow_rate
        / gross_area
    )
 
    channel_velocity_value = calculate_channel_velocity(
        approach_velocity=approach_velocity,
        gross_area=gross_area,
        open_area=open_area,
    )
 
    blockage_ratio_value = calculate_blockage_ratio(
        gross_area=gross_area,
        open_area=open_area,
    )
 
    hydraulic_diameter_value = calculate_hydraulic_diameter(
        spacing_mm=fin_spacing_mm,
        fin_height_mm=fin_height_mm,
    )
 
    if hydraulic_diameter_value <= 0:
        raise ValueError(
            "Calculated hydraulic diameter must be greater than zero."
        )
 
    (
        air_density,
        dynamic_viscosity,
        _thermal_conductivity,
        _specific_heat_capacity,
        _prandtl_number,
    ) = air_properties(
        air_temperature_c
    )
 
    if air_density <= 0:
        raise ValueError(
            "Air density must be greater than zero."
        )
 
    if dynamic_viscosity <= 0:
        raise ValueError(
            "Air dynamic viscosity must be greater than zero."
        )
 
    reynolds_number_value = calculate_reynolds_number(
        rho=air_density,
        velocity=channel_velocity_value,
        hydraulic_diameter=hydraulic_diameter_value,
        mu=dynamic_viscosity,
    )
 
    if reynolds_number_value <= 0:
        raise ValueError(
            "Calculated Reynolds number must be greater than zero."
        )
 
    friction_factor_value = select_darcy_friction_factor(
        reynolds_number=reynolds_number_value,
    )
 
    channel_length = (
        channel_length_mm
        / 1000.0
    )
 
    pressure_drop_value = calculate_total_pressure_drop(
        reynolds_number=reynolds_number_value,
        channel_length=channel_length,
        hydraulic_diameter=hydraulic_diameter_value,
        air_density=air_density,
        channel_velocity=channel_velocity_value,
        entrance_loss_coefficient=(
            entrance_loss_coefficient
        ),
        exit_loss_coefficient=(
            exit_loss_coefficient
        ),
    )
 
    pumping_power_value = calculate_pumping_power(
        total_pressure_drop=pressure_drop_value,
        volumetric_flow_rate=volumetric_flow_rate,
    )
 
    return FlowNetworkResult(
        volumetric_flow_rate=volumetric_flow_rate,
        approach_velocity=approach_velocity,
        channel_velocity=channel_velocity_value,
        gross_flow_area=gross_area,
        open_flow_area=open_area,
        blockage_ratio=blockage_ratio_value,
        hydraulic_diameter=hydraulic_diameter_value,
        reynolds_number=reynolds_number_value,
        friction_factor=friction_factor_value,
        pressure_drop=pressure_drop_value,
        pumping_power=pumping_power_value,
    )

from typing import Callable
 
 
def create_pressure_drop_function(
    base_width_mm: float,
    fin_height_mm: float,
    fin_count_value: int,
    fin_spacing_mm: float,
    channel_length_mm: float,
    air_temperature_c: float,
    entrance_loss_coefficient: float = 0.5,
    exit_loss_coefficient: float = 1.0,
) -> Callable[[float], float]:
    """
    Create a pressure-drop callback for a fixed heat-sink
    geometry.
 
    The returned callable accepts only volumetric flow
    rate (m³/s) and returns the corresponding pressure
    drop (Pa).
 
    This function is intended for iterative fan/system
    coupling and avoids exposing geometry details to the
    coupled solver.
    """
 
    def pressure_drop_function(
        volumetric_flow_rate: float,
    ) -> float:
 
        result = evaluate_flow_network(
            volumetric_flow_rate=volumetric_flow_rate,
            base_width_mm=base_width_mm,
            fin_height_mm=fin_height_mm,
            fin_count_value=fin_count_value,
            fin_spacing_mm=fin_spacing_mm,
            channel_length_mm=channel_length_mm,
            air_temperature_c=air_temperature_c,
            entrance_loss_coefficient=(
                entrance_loss_coefficient
            ),
            exit_loss_coefficient=(
                exit_loss_coefficient
            ),
        )
 
        return result.pressure_drop
 
    return pressure_drop_function
 