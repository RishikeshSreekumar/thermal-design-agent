"""
fan_selection.py
 
Fan-selection logic for matching available fans to
a system-resistance curve and required airflow.
"""
 
from dataclasses import dataclass
from typing import Sequence
 
from fan.fan_curve import FanCurve
from fan.fan_database import get_fan_curve
from fan.operating_point import (
    OperatingPoint,
    SystemResistance,
    solve_operating_point,
)
 
 
@dataclass(frozen=True)
class FanSelectionResult:
    """
    Result of selecting a fan for a flow system.
    """
 
    fan_name: str
    fan_curve: FanCurve
    operating_point: OperatingPoint
    excess_flow_rate: float
 
 
def select_fan(
    fan_names: Sequence[str],
    system: SystemResistance,
    minimum_flow_rate: float,
) -> FanSelectionResult:
    """
    Select the closest-fitting fan that satisfies the
    minimum required volumetric flow rate.
 
    Parameters
    ----------
    fan_names:
        Names of fans registered in the fan database.
 
    system:
        System-resistance model against which each fan
        must operate.
 
    minimum_flow_rate:
        Minimum acceptable operating flow rate in m³/s.
 
    Returns
    -------
    FanSelectionResult
        The feasible fan having the smallest excess
        flow rate above the required minimum.
    """
 
    if not fan_names:
        raise ValueError(
            "At least one fan name must be supplied."
        )
 
    if minimum_flow_rate < 0:
        raise ValueError(
            "Minimum flow rate cannot be negative."
        )
 
    best_selection: FanSelectionResult | None = None
 
    for fan_name in fan_names:
        fan_curve = get_fan_curve(
            fan_name
        )
 
        operating_point = solve_operating_point(
            fan_curve=fan_curve,
            system=system,
        )
 
        if (
            operating_point.volumetric_flow_rate
            < minimum_flow_rate
        ):
            continue
 
        excess_flow_rate = (
            operating_point.volumetric_flow_rate
            - minimum_flow_rate
        )
 
        selection = FanSelectionResult(
            fan_name=fan_name,
            fan_curve=fan_curve,
            operating_point=operating_point,
            excess_flow_rate=excess_flow_rate,
        )
 
        if best_selection is None:
            best_selection = selection
            continue
 
        if (
            selection.excess_flow_rate
            < best_selection.excess_flow_rate
        ):
            best_selection = selection
 
    if best_selection is None:
        raise ValueError(
            "No supplied fan can satisfy the minimum "
            "required flow rate."
        )
 
    return best_selection