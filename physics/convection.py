"""
convection.py
 
Convective heat-transfer models.
"""
 
from physics.correlation_engine import evaluate_correlation
 
 
def nusselt_number(
    reynolds_number: float,
    prandtl_number: float,
) -> float:
    """
    Calculate the Nusselt number using the Correlation Engine.
    """
 
    return evaluate_correlation(
        reynolds_number=reynolds_number,
        prandtl_number=prandtl_number,
    )
 
 
def heat_transfer_coefficient(
    nu: float,
    conductivity: float,
    hydraulic_diameter: float,
) -> float:
    """
    Calculate the convective heat-transfer coefficient.
 
    h = Nu * k / Dh
    """
 
    return (
        nu
        * conductivity
        / hydraulic_diameter
    )