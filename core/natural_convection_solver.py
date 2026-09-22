"""
natural_convection_solver.py
 
High-level deterministic natural-convection resolver.
 
Converts thermal boundary conditions and a characteristic
geometry length into the common ConvectionState.
 
The current implementation uses the Churchill-Chu
vertical-plate correlation.
 
This module does not perform:
- geometry optimization;
- fin-efficiency calculations;
- total thermal-resistance calculations;
- surface-temperature iteration.
"""
 
from models.convection_state import ConvectionState
 
from physics.fluid_properties import air_properties
from physics.natural_convection import (
    churchill_chu_vertical_plate_nusselt,
    film_temperature_c,
    grashof_number,
    heat_transfer_coefficient,
    kinematic_viscosity,
    rayleigh_number,
    volumetric_thermal_expansion_coefficient,
)
 
 
class NaturalConvectionSolver:
    """
    Resolve a natural-convection heat-transfer state.
    """
 
    @staticmethod
    def solve(
        *,
        surface_temperature_c: float,
        ambient_temperature_c: float,
        characteristic_length: float,
    ) -> ConvectionState:
        """
        Calculate the natural-convection state for an
        isothermal vertical surface.
        """
 
        NaturalConvectionSolver._validate_inputs(
            surface_temperature_c=(
                surface_temperature_c
            ),
            ambient_temperature_c=(
                ambient_temperature_c
            ),
            characteristic_length=(
                characteristic_length
            ),
        )
 
        temperature_difference = (
            surface_temperature_c
            - ambient_temperature_c
        )
 
        film_temperature = film_temperature_c(
            surface_temperature_c,
            ambient_temperature_c,
        )
 
        rho, mu, air_k, _, pr = air_properties(
            film_temperature
        )
 
        beta = (
            volumetric_thermal_expansion_coefficient(
                film_temperature
            )
        )
 
        nu = kinematic_viscosity(
            density=rho,
            dynamic_viscosity=mu,
        )
 
        gr = grashof_number(
            beta=beta,
            temperature_difference=(
                temperature_difference
            ),
            characteristic_length=(
                characteristic_length
            ),
            kinematic_viscosity_value=nu,
        )
 
        ra = rayleigh_number(
            grashof_number_value=gr,
            prandtl_number=pr,
        )
 
        nusselt = (
            churchill_chu_vertical_plate_nusselt(
                rayleigh_number_value=ra,
                prandtl_number=pr,
            )
        )
 
        h = heat_transfer_coefficient(
            nusselt_number=nusselt,
            thermal_conductivity=air_k,
            characteristic_length=(
                characteristic_length
            ),
        )
 
        return ConvectionState(
            mode="natural",
            nusselt_number=nusselt,
            heat_transfer_coefficient=h,
            characteristic_length=(
                characteristic_length
            ),
            correlation_name=(
                "churchill_chu_vertical_plate"
            ),
            rayleigh_number=ra,
            grashof_number=gr,
            prandtl_number=pr,
        )
 
    @staticmethod
    def _validate_inputs(
        *,
        surface_temperature_c: float,
        ambient_temperature_c: float,
        characteristic_length: float,
    ) -> None:
        """
        Validate natural-convection boundary conditions.
        """
 
        if (
            surface_temperature_c
            <= ambient_temperature_c
        ):
            raise ValueError(
                "Surface temperature must be greater "
                "than ambient temperature for the "
                "current natural-convection model."
            )
 
        if characteristic_length <= 0:
            raise ValueError(
                "Characteristic length must be greater "
                "than zero."
            )