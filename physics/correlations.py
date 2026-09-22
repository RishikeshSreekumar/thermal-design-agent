"""
correlations.py
 
Engineering heat-transfer correlations used by the Physics Engine.
"""
 
import math
 
 
def fully_developed_laminar_constant_wall_temperature() -> float:
    """
    Return the Nusselt number for the currently supported
    fully developed laminar-flow model with constant wall temperature.
    """
 
    return 7.54
 
 
def fully_developed_laminar_constant_heat_flux() -> float:
    """
    Return the Nusselt number for the currently supported
    fully developed laminar-flow model with constant heat flux.
    """
 
    return 8.235
 
 
def petukhov_friction_factor(
    reynolds_number: float,
) -> float:
    """
    Calculate the smooth-duct Darcy friction factor used by
    the Gnielinski heat-transfer correlation.
 
    f = [0.79 ln(Re) - 1.64]^-2
    """
 
    if reynolds_number <= 0:
        raise ValueError("Reynolds number must be greater than zero.")
 
    return (
        0.79 * math.log(reynolds_number) - 1.64
    ) ** -2
 
 
def gnielinski_turbulent(
    reynolds_number: float,
    prandtl_number: float,
) -> float:
    """
    Calculate the turbulent-flow Nusselt number using the
    Gnielinski correlation.
    """
 
    if reynolds_number < 3000:
        raise ValueError(
            "Gnielinski correlation requires Reynolds number >= 3000."
        )
 
    if prandtl_number <= 0:
        raise ValueError("Prandtl number must be greater than zero.")
 
    friction_factor = petukhov_friction_factor(reynolds_number)
 
    numerator = (
        (friction_factor / 8.0)
        * (reynolds_number - 1000.0)
        * prandtl_number
    )
 
    denominator = (
        1.0
        + 12.7
        * math.sqrt(friction_factor / 8.0)
        * (
            prandtl_number ** (2.0 / 3.0)
            - 1.0
        )
    )
 
    return numerator / denominator
 
 
def transitional_internal_flow(
    reynolds_number: float,
    prandtl_number: float,
) -> float:
    """
    Estimate the Nusselt number in the transition region by
    linearly interpolating between the laminar result at Re=2300
    and the turbulent result at Re=4000.
    """
 
    if not 2300.0 <= reynolds_number < 4000.0:
        raise ValueError(
            "Transition correlation requires "
            "2300 <= Reynolds number < 4000."
        )
 
    laminar_nusselt = (
        fully_developed_laminar_constant_wall_temperature()
    )
 
    turbulent_nusselt_at_4000 = gnielinski_turbulent(
        reynolds_number=4000.0,
        prandtl_number=prandtl_number,
    )
 
    interpolation_factor = (
        (reynolds_number - 2300.0)
        / (4000.0 - 2300.0)
    )
 
    return (
        laminar_nusselt
        + interpolation_factor
        * (
            turbulent_nusselt_at_4000
            - laminar_nusselt
        )
    )