from dataclasses import dataclass
from typing import Sequence
 
 
@dataclass(frozen=True)
class FanCurvePoint:
    """
    A single point on a fan performance curve.
 
    Parameters
    ----------
    volumetric_flow_rate:
        Volumetric airflow rate in m³/s.
 
    static_pressure:
        Fan static pressure in Pa.
    """
 
    volumetric_flow_rate: float
    static_pressure: float
 
    def __post_init__(self) -> None:
        if self.volumetric_flow_rate < 0:
            raise ValueError(
                "Volumetric flow rate cannot be negative."
            )
 
        if self.static_pressure < 0:
            raise ValueError(
                "Static pressure cannot be negative."
            )
 
 
@dataclass(frozen=True)
class FanCurve:
    """
    Represents a fan pressure-flow performance curve.
 
    The curve points must be provided in ascending order
    of volumetric flow rate.
    """
 
    points: Sequence[FanCurvePoint]
 
    def __post_init__(self) -> None:
        if len(self.points) < 2:
            raise ValueError(
                "A fan curve requires at least two points."
            )
 
        previous_flow_rate = -1.0
 
        for point in self.points:
            if (
                point.volumetric_flow_rate
                <= previous_flow_rate
            ):
                raise ValueError(
                    "Fan curve flow rates must be "
                    "strictly increasing."
                )
 
            previous_flow_rate = (
                point.volumetric_flow_rate
            )
 
    @property
    def minimum_flow_rate(self) -> float:
        """
        Return the minimum flow rate represented
        by the fan curve.
        """
 
        return self.points[0].volumetric_flow_rate
 
    @property
    def maximum_flow_rate(self) -> float:
        """
        Return the maximum flow rate represented
        by the fan curve.
        """
 
        return self.points[-1].volumetric_flow_rate
 
    def pressure_at_flow_rate(
        self,
        volumetric_flow_rate: float,
    ) -> float:
        """
        Calculate fan static pressure at a specified
        volumetric flow rate using linear interpolation.
 
        Parameters
        ----------
        volumetric_flow_rate:
            Requested flow rate in m³/s.
 
        Returns
        -------
        Fan static pressure in Pa.
        """
 
        if volumetric_flow_rate < 0:
            raise ValueError(
                "Volumetric flow rate cannot be negative."
            )
 
        if (
            volumetric_flow_rate
            < self.minimum_flow_rate
            or volumetric_flow_rate
            > self.maximum_flow_rate
        ):
            raise ValueError(
                "Requested flow rate lies outside "
                "the fan curve range."
            )
 
        for index in range(len(self.points) - 1):
            lower_point = self.points[index]
            upper_point = self.points[index + 1]
 
            if (
                lower_point.volumetric_flow_rate
                <= volumetric_flow_rate
                <= upper_point.volumetric_flow_rate
            ):
                flow_rate_span = (
                    upper_point.volumetric_flow_rate
                    - lower_point.volumetric_flow_rate
                )
 
                interpolation_fraction = (
                    volumetric_flow_rate
                    - lower_point.volumetric_flow_rate
                ) / flow_rate_span
 
                pressure_span = (
                    upper_point.static_pressure
                    - lower_point.static_pressure
                )
 
                return (
                    lower_point.static_pressure
                    + interpolation_fraction
                    * pressure_span
                )
 
        raise RuntimeError(
            "Unable to interpolate the fan curve."
        )