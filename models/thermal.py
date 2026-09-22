"""
thermal.py
 
Thermal solver output models.
"""
 
from dataclasses import dataclass
 
 
@dataclass
class ThermalResults:
    """
    Results produced by the thermal solver.
    """
 
    # --------------------------------------------------
    # Flow Geometry
    # --------------------------------------------------
 
    gross_frontal_area: float
 
    open_flow_area: float
 
    blockage_ratio: float
 
    approach_velocity: float
 
    channel_velocity: float
 
    # --------------------------------------------------
    # Flow and Convection
    # --------------------------------------------------
 
    reynolds_number: float
 
    hydraulic_diameter: float
 
    nusselt_number: float
 
    heat_transfer_coefficient: float

    friction_factor: float
    pressure_drop: float
    pumping_power: float
 
    # --------------------------------------------------
    # Heat-Sink Geometry
    # --------------------------------------------------
 
    fin_count: int
 
    fin_thickness: float
 
    fin_spacing: float
 
    fin_height: float
 
    base_thickness: float
 
    # --------------------------------------------------
    # Thermal Performance
    # --------------------------------------------------
 
    thermal_resistance: float
 
    estimated_base_temperature: float
 
    material: str

    # --------------------------------------------------
    # Radiation State
    # --------------------------------------------------
 
    radiative_heat_transfer_coefficient: float = 0.0
 
    @property
    def effective_heat_transfer_coefficient(
        self,
    ) -> float:
        """
        Return the total environmental heat-transfer
        coefficient used in the thermal solution.
        """
 
        return self.heat_transfer_coefficient
 
    @property
    def convective_heat_transfer_coefficient(
        self,
    ) -> float:
        """
        Return the convection-only component.
        """
 
        return (
            self.heat_transfer_coefficient
            - self.radiative_heat_transfer_coefficient
        )
 
    @property
    def radiation_enabled(
        self,
    ) -> bool:
        """
        Return whether radiation contributed to this
        thermal result.
        """
 
        return (
            self.radiative_heat_transfer_coefficient
            > 0.0
        )