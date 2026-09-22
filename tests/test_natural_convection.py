"""
Regression checks for reusable natural-convection physics.
"""
 
from physics.natural_convection import (
    churchill_chu_vertical_plate_nusselt,
    film_temperature_c,
    grashof_number,
    heat_transfer_coefficient,
    kinematic_viscosity,
    rayleigh_number,
    thermal_diffusivity,
    volumetric_thermal_expansion_coefficient,
)
 
 
def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-9,
) -> None:
 
    if abs(actual - expected) > tolerance:
        raise AssertionError(
            f"Expected {expected}, received {actual}."
        )
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Representative air / vertical-plate case
    # --------------------------------------------------
 
    surface_temperature_c = 80.0
    ambient_temperature_c = 30.0
 
    density = 1.164
    dynamic_viscosity = 1.872e-5
    thermal_conductivity = 0.0263
    specific_heat = 1007.0
    prandtl_number = 0.71
 
    characteristic_length = 0.05
 
    film_temperature = film_temperature_c(
        surface_temperature_c,
        ambient_temperature_c,
    )
 
    assert_close(
        film_temperature,
        55.0,
    )
 
    beta = (
        volumetric_thermal_expansion_coefficient(
            film_temperature
        )
    )
 
    assert_close(
        beta,
        0.0030473868657626088,
    )
 
    nu = kinematic_viscosity(
        density,
        dynamic_viscosity,
    )
 
    assert_close(
        nu,
        1.6082474226804127e-05,
    )
 
    alpha = thermal_diffusivity(
        density,
        specific_heat,
        thermal_conductivity,
    )
 
    assert_close(
        alpha,
        2.2437439640727966e-05,
    )
 
    gr = grashof_number(
        beta=beta,
        temperature_difference=50.0,
        characteristic_length=(
            characteristic_length
        ),
        kinematic_viscosity_value=nu,
    )
 
    assert_close(
        gr,
        722141.9197246222,
        tolerance=1e-6,
    )
 
    ra = rayleigh_number(
        grashof_number_value=gr,
        prandtl_number=prandtl_number,
    )
 
    assert_close(
        ra,
        512720.76300448173,
        tolerance=1e-6,
    )
 
    nusselt = (
        churchill_chu_vertical_plate_nusselt(
            rayleigh_number_value=ra,
            prandtl_number=prandtl_number,
        )
    )
 
    assert_close(
        nusselt,
        13.893381527356016,
        tolerance=1e-9,
    )
 
    h = heat_transfer_coefficient(
        nusselt_number=nusselt,
        thermal_conductivity=(
            thermal_conductivity
        ),
        characteristic_length=(
            characteristic_length
        ),
    )
 
    assert_close(
        h,
        7.307918683389265,
        tolerance=1e-9,
    )
 
    # --------------------------------------------------
    # Validation checks
    # --------------------------------------------------
 
    try:
        grashof_number(
            beta=beta,
            temperature_difference=0.0,
            characteristic_length=0.05,
            kinematic_viscosity_value=nu,
        )
 
    except ValueError:
        pass
 
    else:
        raise AssertionError(
            "Zero natural-convection temperature "
            "difference was not rejected."
        )
 
    try:
        churchill_chu_vertical_plate_nusselt(
            rayleigh_number_value=0.0,
            prandtl_number=0.71,
        )
 
    except ValueError:
        pass
 
    else:
        raise AssertionError(
            "Zero Rayleigh number was not rejected."
        )
 
    print(
        "ALL NATURAL CONVECTION PHYSICS CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()