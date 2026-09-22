from dataclasses import dataclass
 
 
@dataclass(frozen=True)
class SystemResistance:
    """
    Represents the pressure drop characteristics
    of a flow system.
 
    Pressure drop follows:
 
        ΔP = K × Q²
 
    where
 
    ΔP : Pressure drop (Pa)
    Q  : Volumetric flow rate (m³/s)
    K  : System resistance coefficient
    """
 
    resistance_coefficient: float
 
    def __post_init__(self) -> None:
        if self.resistance_coefficient < 0:
            raise ValueError(
                "Resistance coefficient cannot be negative."
            )
 
    def pressure_drop(
        self,
        volumetric_flow_rate: float,
    ) -> float:
        """
        Calculate system pressure drop.
 
        Parameters
        ----------
        volumetric_flow_rate
            m³/s
 
        Returns
        -------
        Pressure drop (Pa)
        """
 
        if volumetric_flow_rate < 0:
            raise ValueError(
                "Flow rate cannot be negative."
            )
 
        return (
            self.resistance_coefficient
            * volumetric_flow_rate ** 2
        )
from dataclasses import dataclass
 
from fan.fan_curve import FanCurve
 
 
@dataclass(frozen=True)
class OperatingPoint:
    """
    Fan operating point.
    """
 
    volumetric_flow_rate: float
    pressure: float
 
 
def solve_operating_point(
    fan_curve: FanCurve,
    system: SystemResistance,
    number_of_steps: int = 1000,
) -> OperatingPoint:
    """
    Determine the operating point by searching for the
    minimum pressure difference between the fan curve
    and the system resistance curve.
    """
 
    if number_of_steps < 2:
        raise ValueError(
            "number_of_steps must be at least 2."
        )
 
    minimum_flow = fan_curve.minimum_flow_rate
    maximum_flow = fan_curve.maximum_flow_rate
 
    flow_step = (
        maximum_flow - minimum_flow
    ) / (number_of_steps - 1)
 
    best_flow = minimum_flow
    best_pressure = fan_curve.pressure_at_flow_rate(
        minimum_flow
    )
 
    smallest_error = float("inf")
 
    for step in range(number_of_steps):
 
        flow_rate = (
            minimum_flow
            + step * flow_step
        )
 
        fan_pressure = (
            fan_curve.pressure_at_flow_rate(
                flow_rate
            )
        )
 
        system_pressure = (
            system.pressure_drop(
                flow_rate
            )
        )
 
        error = abs(
            fan_pressure
            - system_pressure
        )
 
        if error < smallest_error:
            smallest_error = error
            best_flow = flow_rate
            best_pressure = fan_pressure
 
    return OperatingPoint(
        volumetric_flow_rate=best_flow,
        pressure=best_pressure,
    )