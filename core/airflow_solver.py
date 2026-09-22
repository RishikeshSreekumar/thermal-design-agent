"""
airflow_solver.py
 
High-level airflow solver for candidate heat-sink geometries.
 
This module couples the fan-performance model with the
heat-sink flow network and returns the converged hydraulic
state.
 
No flow physics are implemented here. The module simply
coordinates the existing fan and physics packages.
"""
 
from physics.flow_network import (
    FlowNetworkResult,
    create_pressure_drop_function,
    evaluate_flow_network,
)
 
from fan.coupled_solver import (
    solve_coupled_flow,
)
 
from fan.fan_curve import (
    FanCurve,
)
 
 
def solve_candidate_airflow(
    fan_curve: FanCurve,
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
    Solve the coupled fan/heat-sink airflow problem for a
    single candidate geometry.
 
    Parameters
    ----------
    fan_curve
        Selected fan performance curve.
 
    Remaining parameters
        Plate-fin heat-sink geometry.
 
    Returns
    -------
    FlowNetworkResult
        Fully converged hydraulic state.
    """
 
    pressure_drop_function = (
        create_pressure_drop_function(
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
    )
 
    coupled_result = solve_coupled_flow(
        fan_curve=fan_curve,
        pressure_drop_function=(
            pressure_drop_function
        ),
    )
 
    return evaluate_flow_network(
        volumetric_flow_rate=(
            coupled_result.volumetric_flow_rate
        ),
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