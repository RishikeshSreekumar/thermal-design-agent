"""
radiation.py
 
Deterministic thermal-radiation utilities for the
Thermal Design Agent.
 
Current scope:
 
- gray, diffuse surface;
- radiation exchange with large surroundings;
- surroundings temperature equal to ambient air
  when coupled into the current plate-fin solver;
- linearized radiative heat-transfer coefficient.
 
Detailed surface-to-surface view factors and inter-fin
radiative exchange are outside the current reduced-order
model.
"""
 
import math
 
 
STEFAN_BOLTZMANN_CONSTANT = 5.670374419e-8
 
 
def celsius_to_kelvin(
    temperature_c: float,
) -> float:
    """
    Convert degrees Celsius to kelvin.
    """
 
    if not math.isfinite(temperature_c):
        raise ValueError(
            "Temperature must be finite."
        )
 
    temperature_k = (
        temperature_c
        + 273.15
    )
 
    if temperature_k <= 0.0:
        raise ValueError(
            "Absolute temperature must be greater "
            "than zero kelvin."
        )
 
    return temperature_k
 
 
def radiative_heat_transfer_coefficient(
    *,
    surface_temperature_c: float,
    surroundings_temperature_c: float,
    emissivity: float,
) -> float:
    """
    Calculate the linearized radiation heat-transfer
    coefficient between a gray surface and large
    surroundings.
 
    h_r =
        epsilon * sigma
        * (T_s + T_sur)
        * (T_s^2 + T_sur^2)
 
    Temperatures are converted internally to kelvin.
 
    The resulting coefficient satisfies:
 
        q''_rad =
            h_r * (T_s - T_sur)
    """
 
    if not math.isfinite(emissivity):
        raise ValueError(
            "Emissivity must be finite."
        )
 
    if not (
        0.0
        <= emissivity
        <= 1.0
    ):
        raise ValueError(
            "Emissivity must lie between 0 and 1."
        )
 
    surface_temperature_k = (
        celsius_to_kelvin(
            surface_temperature_c
        )
    )
 
    surroundings_temperature_k = (
        celsius_to_kelvin(
            surroundings_temperature_c
        )
    )
 
    return (
        emissivity
        * STEFAN_BOLTZMANN_CONSTANT
        * (
            surface_temperature_k
            + surroundings_temperature_k
        )
        * (
            surface_temperature_k ** 2
            + surroundings_temperature_k ** 2
        )
    )
 
 
def radiative_heat_flux(
    *,
    surface_temperature_c: float,
    surroundings_temperature_c: float,
    emissivity: float,
) -> float:
    """
    Calculate net radiative heat flux from a gray
    surface to large surroundings.
 
    q'' =
        epsilon * sigma
        * (T_s^4 - T_sur^4)
 
    Positive values represent net heat rejection from
    the surface.
    """
 
    if not math.isfinite(emissivity):
        raise ValueError(
            "Emissivity must be finite."
        )
 
    if not (
        0.0
        <= emissivity
        <= 1.0
    ):
        raise ValueError(
            "Emissivity must lie between 0 and 1."
        )
 
    surface_temperature_k = (
        celsius_to_kelvin(
            surface_temperature_c
        )
    )
 
    surroundings_temperature_k = (
        celsius_to_kelvin(
            surroundings_temperature_c
        )
    )
 
    return (
        emissivity
        * STEFAN_BOLTZMANN_CONSTANT
        * (
            surface_temperature_k ** 4
            - surroundings_temperature_k ** 4
        )
    )