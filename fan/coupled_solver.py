"""
coupled_solver.py
 
Iterative coupling between a fan performance curve and
a flow system whose pressure drop depends on airflow.
 
The solver repeatedly:
 
1. Evaluates system pressure drop at the current flow rate.
2. Constructs an equivalent quadratic system-resistance curve.
3. Solves the fan/system operating point.
4. Updates the flow-rate estimate.
5. Repeats until the flow rate converges.
"""
 
from dataclasses import dataclass
from typing import Callable
 
from fan.fan_curve import FanCurve
from fan.operating_point import (
    OperatingPoint,
    SystemResistance,
    solve_operating_point,
)
 
 
@dataclass(frozen=True)
class CoupledFlowResult:
    """
    Converged fan–system flow solution.
 
    Parameters
    ----------
    volumetric_flow_rate:
        Converged volumetric airflow rate in m³/s.
 
    fan_pressure:
        Fan static pressure at the converged operating
        point in Pa.
 
    system_pressure_drop:
        Calculated system pressure drop at the converged
        flow rate in Pa.
 
    resistance_coefficient:
        Equivalent system resistance coefficient in
        ΔP = K × Q².
 
    iteration_count:
        Number of coupling iterations performed.
 
    flow_rate_error:
        Absolute difference between the final two
        flow-rate estimates in m³/s.
    """
 
    volumetric_flow_rate: float
    fan_pressure: float
    system_pressure_drop: float
    resistance_coefficient: float
    iteration_count: int
    flow_rate_error: float
 
 
def solve_coupled_flow(
    fan_curve: FanCurve,
    pressure_drop_function: Callable[[float], float],
    initial_flow_rate: float | None = None,
    flow_rate_tolerance: float = 1e-6,
    maximum_iterations: int = 100,
    relaxation_factor: float = 0.5,
    operating_point_steps: int = 1000,
) -> CoupledFlowResult:
    """
    Solve the coupled fan and system operating point.
 
    Parameters
    ----------
    fan_curve:
        Fan pressure-flow performance curve.
 
    pressure_drop_function:
        Callable receiving volumetric flow rate in m³/s
        and returning system pressure drop in Pa.
 
    initial_flow_rate:
        Starting flow-rate estimate in m³/s. When omitted,
        the midpoint of the fan curve is used.
 
    flow_rate_tolerance:
        Maximum permitted difference between consecutive
        flow-rate estimates for convergence.
 
    maximum_iterations:
        Maximum number of coupling iterations.
 
    relaxation_factor:
        Fraction of the newly calculated operating-point
        flow used during each update. Must be greater than
        0 and no greater than 1.
 
    operating_point_steps:
        Number of search points used by the operating-point
        solver.
 
    Returns
    -------
    CoupledFlowResult
        Converged coupled-flow state.
 
    Raises
    ------
    ValueError
        If an input is invalid, the pressure-drop function
        returns an invalid value, or convergence is not
        achieved.
    """
 
    if flow_rate_tolerance <= 0:
        raise ValueError(
            "Flow-rate tolerance must be greater than zero."
        )
 
    if maximum_iterations < 1:
        raise ValueError(
            "Maximum iterations must be at least 1."
        )
 
    if not 0 < relaxation_factor <= 1:
        raise ValueError(
            "Relaxation factor must be greater than 0 "
            "and no greater than 1."
        )
 
    if operating_point_steps < 2:
        raise ValueError(
            "Operating-point steps must be at least 2."
        )
 
    if initial_flow_rate is None:
        current_flow_rate = (
            fan_curve.minimum_flow_rate
            + fan_curve.maximum_flow_rate
        ) / 2.0
 
    else:
        current_flow_rate = initial_flow_rate
 
    if current_flow_rate <= 0:
        raise ValueError(
            "Initial flow rate must be greater than zero."
        )
 
    if (
        current_flow_rate < fan_curve.minimum_flow_rate
        or current_flow_rate > fan_curve.maximum_flow_rate
    ):
        raise ValueError(
            "Initial flow rate must lie within the "
            "fan-curve range."
        )
 
    final_operating_point: OperatingPoint | None = None
    final_pressure_drop = 0.0
    final_resistance_coefficient = 0.0
    flow_rate_error = float("inf")
 
    for iteration_count in range(
        1,
        maximum_iterations + 1,
    ):
        system_pressure_drop = pressure_drop_function(
            current_flow_rate
        )
 
        if system_pressure_drop < 0:
            raise ValueError(
                "System pressure drop cannot be negative."
            )
 
        resistance_coefficient = (
            system_pressure_drop
            / current_flow_rate ** 2
        )
 
        system = SystemResistance(
            resistance_coefficient=(
                resistance_coefficient
            )
        )
 
        operating_point = solve_operating_point(
            fan_curve=fan_curve,
            system=system,
            number_of_steps=operating_point_steps,
        )
 
        relaxed_flow_rate = (
            current_flow_rate
            + relaxation_factor
            * (
                operating_point.volumetric_flow_rate
                - current_flow_rate
            )
        )
 
        flow_rate_error = abs(
            relaxed_flow_rate
            - current_flow_rate
        )
 
        current_flow_rate = relaxed_flow_rate
        final_operating_point = operating_point
        final_pressure_drop = system_pressure_drop
        final_resistance_coefficient = (
            resistance_coefficient
        )
 
        if flow_rate_error <= flow_rate_tolerance:
            final_pressure_drop = pressure_drop_function(
                current_flow_rate
            )
 
            if final_pressure_drop < 0:
                raise ValueError(
                    "System pressure drop cannot be negative."
                )
 
            final_resistance_coefficient = (
                final_pressure_drop
                / current_flow_rate ** 2
            )
 
            final_system = SystemResistance(
                resistance_coefficient=(
                    final_resistance_coefficient
                )
            )
 
            final_operating_point = solve_operating_point(
                fan_curve=fan_curve,
                system=final_system,
                number_of_steps=operating_point_steps,
            )
 
            return CoupledFlowResult(
                volumetric_flow_rate=(
                    current_flow_rate
                ),
                fan_pressure=(
                    final_operating_point.pressure
                ),
                system_pressure_drop=(
                    final_pressure_drop
                ),
                resistance_coefficient=(
                    final_resistance_coefficient
                ),
                iteration_count=iteration_count,
                flow_rate_error=flow_rate_error,
            )
 
    raise ValueError(
        "Coupled fan-system solver did not converge "
        f"within {maximum_iterations} iterations."
    )
 