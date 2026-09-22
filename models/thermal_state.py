"""
thermal_state.py
 
Typed result produced by the thermal solver.
 
ThermalState contains only the quantities calculated
by the thermal-analysis stage after the convection state
has already been resolved.
 
The legacy 'heat_transfer_coefficient' field represents
the effective environmental heat-transfer coefficient.
 
When radiation is disabled:
 
    h_effective = h_convective
 
When radiation is enabled:
 
    h_effective = h_convective + h_radiative
 
Nusselt number remains a convection-only quantity.
"""
 
from dataclasses import dataclass
 
 
@dataclass(frozen=True)
class ThermalState:
    """
    Thermal-performance state for one heat-sink
    design candidate.
    """
 
    # --------------------------------------------------
    # Convection / Environmental Heat Transfer
    # --------------------------------------------------
 
    nusselt_number: float
 
    heat_transfer_coefficient: float
 
    # --------------------------------------------------
    # Surface and Fin Performance
    # --------------------------------------------------
 
    total_surface_area: float
 
    fin_efficiency: float
 
    # --------------------------------------------------
    # Thermal Performance
    # --------------------------------------------------
 
    thermal_resistance: float
 
    estimated_base_temperature: float
 
    # --------------------------------------------------
    # Radiation
    # --------------------------------------------------
 
    radiative_heat_transfer_coefficient: float = 0.0
 
    @property
    def effective_heat_transfer_coefficient(
        self,
    ) -> float:
        """
        Return the total linearized environmental
        heat-transfer coefficient used by the thermal
        resistance and fin-efficiency calculations.
        """
 
        return self.heat_transfer_coefficient
 
    @property
    def convective_heat_transfer_coefficient(
        self,
    ) -> float:
        """
        Return the convection-only heat-transfer
        coefficient.
 
        The legacy heat_transfer_coefficient stores the
        effective coefficient, so the convective component
        is recovered by subtracting the explicitly stored
        radiative contribution.
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
        Return whether radiation contributes to the
        current thermal state.
        """
 
        return (
            self.radiative_heat_transfer_coefficient
            > 0.0
        )