"""
Regression checks for deterministic thermal-radiation
utilities.
"""
 
import math
 
from physics.radiation import (
    STEFAN_BOLTZMANN_CONSTANT,
    celsius_to_kelvin,
    radiative_heat_flux,
    radiative_heat_transfer_coefficient,
)
 
 
def assert_value_error(
    callback,
) -> None:
    try:
        callback()
 
    except ValueError:
        return
 
    raise AssertionError(
        "Expected ValueError."
    )
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Temperature conversion
    # --------------------------------------------------
 
    assert math.isclose(
        celsius_to_kelvin(0.0),
        273.15,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        celsius_to_kelvin(100.0),
        373.15,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Reference radiation state
    # --------------------------------------------------
 
    surface_temperature_c = 100.0
    surroundings_temperature_c = 30.0
    emissivity = 0.85
 
    surface_temperature_k = 373.15
    surroundings_temperature_k = 303.15
 
    expected_heat_flux = (
        emissivity
        * STEFAN_BOLTZMANN_CONSTANT
        * (
            surface_temperature_k ** 4
            - surroundings_temperature_k ** 4
        )
    )
 
    heat_flux = radiative_heat_flux(
        surface_temperature_c=(
            surface_temperature_c
        ),
        surroundings_temperature_c=(
            surroundings_temperature_c
        ),
        emissivity=emissivity,
    )
 
    assert math.isclose(
        heat_flux,
        expected_heat_flux,
        rel_tol=0.0,
        abs_tol=1e-10,
    )
 
    # --------------------------------------------------
    # Linearized coefficient
    # --------------------------------------------------
 
    expected_h_rad = (
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
 
    h_rad = (
        radiative_heat_transfer_coefficient(
            surface_temperature_c=(
                surface_temperature_c
            ),
            surroundings_temperature_c=(
                surroundings_temperature_c
            ),
            emissivity=emissivity,
        )
    )
 
    assert math.isclose(
        h_rad,
        expected_h_rad,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # Exact linearization identity.
    assert math.isclose(
        heat_flux,
        h_rad
        * (
            surface_temperature_c
            - surroundings_temperature_c
        ),
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Zero emissivity
    # --------------------------------------------------
 
    assert (
        radiative_heat_transfer_coefficient(
            surface_temperature_c=100.0,
            surroundings_temperature_c=30.0,
            emissivity=0.0,
        )
        == 0.0
    )
 
    assert (
        radiative_heat_flux(
            surface_temperature_c=100.0,
            surroundings_temperature_c=30.0,
            emissivity=0.0,
        )
        == 0.0
    )
 
    # --------------------------------------------------
    # Equal temperatures
    # --------------------------------------------------
 
    equal_temperature_flux = (
        radiative_heat_flux(
            surface_temperature_c=30.0,
            surroundings_temperature_c=30.0,
            emissivity=0.85,
        )
    )
 
    assert math.isclose(
        equal_temperature_flux,
        0.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # h_rad itself remains positive at equal temperature.
    assert (
        radiative_heat_transfer_coefficient(
            surface_temperature_c=30.0,
            surroundings_temperature_c=30.0,
            emissivity=0.85,
        )
        > 0.0
    )
 
    # --------------------------------------------------
    # Invalid inputs
    # --------------------------------------------------
 
    assert_value_error(
        lambda: (
            radiative_heat_transfer_coefficient(
                surface_temperature_c=100.0,
                surroundings_temperature_c=30.0,
                emissivity=-0.1,
            )
        )
    )
 
    assert_value_error(
        lambda: radiative_heat_flux(
            surface_temperature_c=100.0,
            surroundings_temperature_c=30.0,
            emissivity=1.1,
        )
    )
 
    assert_value_error(
        lambda: celsius_to_kelvin(
            -273.15
        )
    )
 
    print()
    print(
        "Reference radiative HTC:",
        h_rad,
        "W/m²K",
    )
 
    print(
        "Reference radiative heat flux:",
        heat_flux,
        "W/m²",
    )
 
    print(
        "ALL THERMAL-RADIATION CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()