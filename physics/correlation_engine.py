"""
Correlation Engine
 
This module is responsible for selecting the appropriate engineering
correlation based on the flow conditions.
 
Examples:
- Fully developed laminar flow
- Developing laminar flow
- Turbulent flow
- Natural convection
- Mixed convection
 
Initially, only fully developed laminar flow is supported.
"""
 
from enum import Enum

from physics.correlations import (
    fully_developed_laminar_constant_wall_temperature,
    fully_developed_laminar_constant_heat_flux,
    gnielinski_turbulent,
    transitional_internal_flow,
)
 
class FlowRegime(Enum):
    LAMINAR = "Laminar"
    TRANSITION = "Transition"
    TURBULENT = "Turbulent"
 
 
class CorrelationType(Enum):
    FULLY_DEVELOPED_LAMINAR = "Fully Developed Laminar"
    DEVELOPING_LAMINAR = "Developing Laminar"
    TRANSITIONAL_INTERNAL_FLOW = "Transitional Internal Flow"
    GNIELINSKI_TURBULENT = "Gnielinski Turbulent"

def classify_flow_regime(reynolds_number: float) -> FlowRegime:
    """
    Classify the flow regime based on Reynolds number.
    """
 
    if reynolds_number < 2300:
        return FlowRegime.LAMINAR
 
    if reynolds_number < 4000:
        return FlowRegime.TRANSITION
 
    return FlowRegime.TURBULENT

def select_correlation(
    reynolds_number: float,
) -> CorrelationType:
    """
    Select the heat-transfer correlation based on flow regime.
    """
 
    flow_regime = classify_flow_regime(reynolds_number)
 
    if flow_regime == FlowRegime.LAMINAR:
        return CorrelationType.FULLY_DEVELOPED_LAMINAR
 
    if flow_regime == FlowRegime.TRANSITION:
        return CorrelationType.TRANSITIONAL_INTERNAL_FLOW
 
    return CorrelationType.GNIELINSKI_TURBULENT

def evaluate_correlation(
    reynolds_number: float,
    prandtl_number: float,
) -> float:
    """
    Evaluate the selected heat-transfer correlation and return
    the Nusselt number.
    """
 
    correlation = select_correlation(reynolds_number)
 
    if correlation == CorrelationType.FULLY_DEVELOPED_LAMINAR:
        return fully_developed_laminar_constant_wall_temperature()
 
    if correlation == CorrelationType.TRANSITIONAL_INTERNAL_FLOW:
        return transitional_internal_flow(
            reynolds_number=reynolds_number,
            prandtl_number=prandtl_number,
        )
 
    if correlation == CorrelationType.GNIELINSKI_TURBULENT:
        return gnielinski_turbulent(
            reynolds_number=reynolds_number,
            prandtl_number=prandtl_number,
        )
 
    raise NotImplementedError(
        f"Correlation '{correlation.value}' has not been implemented."
    )