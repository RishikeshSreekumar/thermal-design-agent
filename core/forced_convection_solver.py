"""
forced_convection_solver.py
 
Deterministic forced-convection resolver.
 
Converts an already-resolved forced-airflow state into the
common ConvectionState used by downstream thermal analysis.
 
This module performs convection calculations only.
It does not solve airflow, fan operating points, geometry,
manufacturability, or thermal resistance.
"""
 
from models.convection_state import ConvectionState
 
from physics.convection import (
    heat_transfer_coefficient as calculate_heat_transfer_coefficient,
    nusselt_number as calculate_nusselt_number,
)
from physics.flow_network import FlowNetworkResult
 
 
class ForcedConvectionSolver:
    """
    Resolve forced-convection heat-transfer state from an
    existing FlowNetworkResult.
    """
 
    @staticmethod
    def solve(
        *,
        flow_state: FlowNetworkResult,
        air_conductivity: float,
        prandtl_number: float,
    ) -> ConvectionState:
        """
        Calculate the forced-convection state.
        """
 
        ForcedConvectionSolver._validate_inputs(
            flow_state=flow_state,
            air_conductivity=air_conductivity,
            prandtl_number=prandtl_number,
        )
 
        nusselt_number = calculate_nusselt_number(
            flow_state.reynolds_number,
            prandtl_number,
        )
 
        heat_transfer_coefficient = (
            calculate_heat_transfer_coefficient(
                nusselt_number,
                air_conductivity,
                flow_state.hydraulic_diameter,
            )
        )
 
        return ConvectionState(
            mode="forced",
            nusselt_number=nusselt_number,
            heat_transfer_coefficient=(
                heat_transfer_coefficient
            ),
            characteristic_length=(
                flow_state.hydraulic_diameter
            ),
            correlation_name=(
                "internal_forced_convection"
            ),
            reynolds_number=(
                flow_state.reynolds_number
            ),
            prandtl_number=prandtl_number,
        )
 
    @staticmethod
    def _validate_inputs(
        *,
        flow_state: FlowNetworkResult,
        air_conductivity: float,
        prandtl_number: float,
    ) -> None:
        """
        Validate the inputs required for forced convection.
        """
 
        if not isinstance(
            flow_state,
            FlowNetworkResult,
        ):
            raise ValueError(
                "'flow_state' must be a "
                "FlowNetworkResult object."
            )
 
        if flow_state.hydraulic_diameter <= 0:
            raise ValueError(
                "Hydraulic diameter must be greater "
                "than zero."
            )
 
        if flow_state.reynolds_number < 0:
            raise ValueError(
                "Reynolds number cannot be negative."
            )
 
        if air_conductivity <= 0:
            raise ValueError(
                "Air thermal conductivity must be "
                "greater than zero."
            )
 
        if prandtl_number <= 0:
            raise ValueError(
                "Prandtl number must be greater than zero."
            )