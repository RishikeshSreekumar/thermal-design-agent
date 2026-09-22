"""
design_candidate.py
 
Represents one candidate heat-sink design explored
by the thermal optimizer.
 
A design candidate contains:
 
1. Independent geometry variables explored by the optimizer
2. Derived geometry parameters
3. Calculated airflow and thermal-performance parameters
 
Manufacturing feasibility is assessed before complete
candidate evaluation and is not stored in this model.
"""
 
from dataclasses import dataclass
from models.material_cost_result import (
    MaterialCostResult,
)
 
 
@dataclass
class DesignCandidate:
    """
    Represents one heat-sink geometry evaluated
    by the optimizer.
    """
 
    # --------------------------------------------------
    # Independent Design Variables
    # --------------------------------------------------
 
    base_thickness: float
 
    fin_thickness: float
 
    fin_height: float
 
    fin_spacing: float
 
    # --------------------------------------------------
    # Derived Geometry
    # --------------------------------------------------
 
    fin_count: int
 
    total_height: float

    # --------------------------------------------------
    # Flow Geometry
    # --------------------------------------------------
 
    gross_frontal_area: float
 
    open_flow_area: float
 
    blockage_ratio: float
 
    approach_velocity: float
 
    channel_velocity: float
 
    # --------------------------------------------------
    # Flow and Heat Transfer
    # --------------------------------------------------
 
    reynolds_number: float
 
    nusselt_number: float
 
    heat_transfer_coefficient: float

    friction_factor: float
    pressure_drop: float
    pumping_power: float
 
 
    # --------------------------------------------------
    # Thermal Performance
    # --------------------------------------------------
 
    thermal_resistance: float
 
    estimated_base_temperature: float
 
    # --------------------------------------------------
    # Preserved Hydraulic State
    # --------------------------------------------------
 
    hydraulic_diameter: float = 0.0
 
    # --------------------------------------------------
    # Physical Material Properties
    # --------------------------------------------------
 
    solid_volume: float = 0.0
 
    mass: float = 0.0

    # --------------------------------------------------
    # Commercial Evaluation
    # --------------------------------------------------
 
    material_cost_result: (
        MaterialCostResult | None
    ) = None

    @property
    def material_cost(
        self,
    ) -> float | None:
        """
        Return the calculated raw-material cost amount.
 
        None means that no material-cost evaluation has
        been attached to this candidate.
        """
 
        if self.material_cost_result is None:
            return None
 
        return self.material_cost_result.amount
 
    @property
    def material_cost_currency(
        self,
    ) -> str | None:
        """
        Return the currency of the calculated material cost.
        """
 
        if self.material_cost_result is None:
            return None
 
        return (
            self.material_cost_result.currency_code
        )
 
    @property
    def has_material_cost(
        self,
    ) -> bool:
        """
        Return whether the candidate has a completed
        material-cost evaluation.
        """
 
        return (
            self.material_cost_result
            is not None
        )

    # --------------------------------------------------
    # Convection Mode
    # --------------------------------------------------
 
    convection_mode: str = "forced"
 
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
        coefficient used for fin efficiency and thermal
        resistance.
        """
 
        return self.heat_transfer_coefficient
 
    @property
    def convective_heat_transfer_coefficient(
        self,
    ) -> float:
        """
        Return the convection-only heat-transfer
        coefficient.
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
        Return whether thermal radiation contributes to
        this completed candidate.
        """
 
        return (
            self.radiative_heat_transfer_coefficient
            > 0.0
        )