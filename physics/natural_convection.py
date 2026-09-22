"""
natural_convection.py
 
Reusable deterministic natural-convection physics.
 
This module contains topology-independent buoyancy and
natural-convection calculations.
 
Current implemented correlation:
- Churchill-Chu correlation for an isothermal vertical plate
 
The module does not:
- perform geometry optimization;
- determine heat-sink orientation;
- solve surface temperature iteratively;
- calculate fin efficiency;
- calculate total thermal resistance.
 
Those responsibilities remain in higher-level modules.
"""
 
import math
 
 
STANDARD_GRAVITY = 9.80665
 
 
def film_temperature_c(
    surface_temperature_c: float,
    ambient_temperature_c: float,
) -> float:
    """
    Return arithmetic-mean film temperature in °C.
    """
 
    return (
        surface_temperature_c
        + ambient_temperature_c
    ) / 2.0
 
 
def volumetric_thermal_expansion_coefficient(
    film_temperature_c_value: float,
) -> float:
    """
    Return the ideal-gas volumetric thermal expansion
    coefficient for air.
 
    beta = 1 / T_film
 
    Temperature is converted to kelvin.
    """
 
    film_temperature_k = (
        film_temperature_c_value
        + 273.15
    )
 
    if film_temperature_k <= 0:
        raise ValueError(
            "Film temperature must be greater than "
            "absolute zero."
        )
 
    return 1.0 / film_temperature_k
 
 
def kinematic_viscosity(
    density: float,
    dynamic_viscosity: float,
) -> float:
    """
    Calculate kinematic viscosity.
 
    nu = mu / rho
    """
 
    if density <= 0:
        raise ValueError(
            "Density must be greater than zero."
        )
 
    if dynamic_viscosity <= 0:
        raise ValueError(
            "Dynamic viscosity must be greater than zero."
        )
 
    return dynamic_viscosity / density
 
 
def thermal_diffusivity(
    density: float,
    specific_heat: float,
    thermal_conductivity: float,
) -> float:
    """
    Calculate thermal diffusivity.
 
    alpha = k / (rho * cp)
    """
 
    if density <= 0:
        raise ValueError(
            "Density must be greater than zero."
        )
 
    if specific_heat <= 0:
        raise ValueError(
            "Specific heat must be greater than zero."
        )
 
    if thermal_conductivity <= 0:
        raise ValueError(
            "Thermal conductivity must be greater "
            "than zero."
        )
 
    return (
        thermal_conductivity
        / (
            density
            * specific_heat
        )
    )
 
 
def grashof_number(
    *,
    beta: float,
    temperature_difference: float,
    characteristic_length: float,
    kinematic_viscosity_value: float,
    gravity: float = STANDARD_GRAVITY,
) -> float:
    """
    Calculate the Grashof number.
 
    Gr = g * beta * delta_T * L^3 / nu^2
    """
 
    if beta <= 0:
        raise ValueError(
            "Thermal expansion coefficient must be "
            "greater than zero."
        )
 
    if temperature_difference <= 0:
        raise ValueError(
            "Temperature difference must be greater "
            "than zero for natural convection."
        )
 
    if characteristic_length <= 0:
        raise ValueError(
            "Characteristic length must be greater "
            "than zero."
        )
 
    if kinematic_viscosity_value <= 0:
        raise ValueError(
            "Kinematic viscosity must be greater "
            "than zero."
        )
 
    if gravity <= 0:
        raise ValueError(
            "Gravity must be greater than zero."
        )
 
    return (
        gravity
        * beta
        * temperature_difference
        * characteristic_length ** 3
        / kinematic_viscosity_value ** 2
    )
 
 
def rayleigh_number(
    *,
    grashof_number_value: float,
    prandtl_number: float,
) -> float:
    """
    Calculate the Rayleigh number.
 
    Ra = Gr * Pr
    """
 
    if grashof_number_value < 0:
        raise ValueError(
            "Grashof number cannot be negative."
        )
 
    if prandtl_number <= 0:
        raise ValueError(
            "Prandtl number must be greater than zero."
        )
 
    return (
        grashof_number_value
        * prandtl_number
    )
 
 
def churchill_chu_vertical_plate_nusselt(
    *,
    rayleigh_number_value: float,
    prandtl_number: float,
) -> float:
    """
    Calculate average Nusselt number for natural
    convection over an isothermal vertical plate using
    the Churchill-Chu correlation.
 
    This correlation provides a continuous relation over
    a broad natural-convection Rayleigh-number range.
    """
 
    if rayleigh_number_value <= 0:
        raise ValueError(
            "Rayleigh number must be greater than zero."
        )
 
    if prandtl_number <= 0:
        raise ValueError(
            "Prandtl number must be greater than zero."
        )
 
    numerator = (
        0.387
        * rayleigh_number_value ** (1.0 / 6.0)
    )
 
    denominator = (
        1.0
        + (
            0.492
            / prandtl_number
        ) ** (9.0 / 16.0)
    ) ** (8.0 / 27.0)
 
    return (
        0.825
        + numerator / denominator
    ) ** 2
 
 
def heat_transfer_coefficient(
    *,
    nusselt_number: float,
    thermal_conductivity: float,
    characteristic_length: float,
) -> float:
    """
    Calculate natural-convection heat-transfer
    coefficient.
 
    h = Nu * k / L
    """
 
    if nusselt_number <= 0:
        raise ValueError(
            "Nusselt number must be greater than zero."
        )
 
    if thermal_conductivity <= 0:
        raise ValueError(
            "Thermal conductivity must be greater "
            "than zero."
        )
 
    if characteristic_length <= 0:
        raise ValueError(
            "Characteristic length must be greater "
            "than zero."
        )
 
    return (
        nusselt_number
        * thermal_conductivity
        / characteristic_length
    )