"""
Regression checks for deterministic component-mass
calculations.
"""
 
import math
 
from materials.material_database import (
    AL6061_T6,
    AL6063_T5,
    COPPER_C110,
)
from models.material import Material
from physics.mass_model import (
    component_mass,
)
from physics.solid_geometry import (
    plate_fin_heat_sink_volume,
)
 
 
def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-12,
) -> None:
    """
    Assert that two floating-point values are sufficiently
    close.
    """
 
    if not math.isclose(
        actual,
        expected,
        rel_tol=0.0,
        abs_tol=tolerance,
    ):
        raise AssertionError(
            f"Expected {expected}, received {actual}."
        )
 
 
def assert_value_error(
    expected_message: str,
    solid_volume_m3: float,
    material: Material,
) -> None:
    """
    Verify that invalid numerical mass-model inputs are
    rejected.
    """
 
    try:
        component_mass(
            solid_volume_m3,
            material,
        )
 
    except ValueError as exc:
        assert expected_message in str(exc)
 
    else:
        raise AssertionError(
            "Invalid mass-model input was accepted."
        )
 
 
def main() -> None:
    # --------------------------------------------------
    # Reference plate-fin heat-sink geometry
    # --------------------------------------------------
 
    solid_volume = (
        plate_fin_heat_sink_volume(
            base_length_mm=50.0,
            base_width_mm=50.0,
            base_thickness_mm=3.0,
            fin_height_mm=8.0,
            fin_thickness_mm=0.8,
            fin_count=21,
        )
    )
 
    assert_close(
        solid_volume,
        1.422e-5,
        tolerance=1e-15,
    )
 
    # --------------------------------------------------
    # Aluminium 6063-T5 reference mass
    # --------------------------------------------------
 
    aluminium_mass = component_mass(
        solid_volume,
        AL6063_T5,
    )
 
    expected_aluminium_mass = (
        1.422e-5
        * 2700.0
    )
 
    assert_close(
        aluminium_mass,
        expected_aluminium_mass,
    )
 
    assert_close(
        aluminium_mass,
        0.038394,
    )
 
    # Mass is returned in kilograms.
    # The reference geometry therefore weighs 38.394 g.
 
    assert_close(
        aluminium_mass * 1000.0,
        38.394,
    )
 
    # --------------------------------------------------
    # Materials with identical density produce identical
    # mass for identical volume.
    # --------------------------------------------------
 
    aluminium_6061_mass = component_mass(
        solid_volume,
        AL6061_T6,
    )
 
    assert_close(
        aluminium_6061_mass,
        aluminium_mass,
    )
 
    # --------------------------------------------------
    # Copper mass uses the density stored in the material
    # database rather than a density defined here.
    # --------------------------------------------------
 
    copper_mass = component_mass(
        solid_volume,
        COPPER_C110,
    )
 
    expected_copper_mass = (
        solid_volume
        * COPPER_C110.density
    )
 
    assert_close(
        copper_mass,
        expected_copper_mass,
    )
 
    assert copper_mass > aluminium_mass
 
    expected_mass_ratio = (
        COPPER_C110.density
        / AL6063_T5.density
    )
 
    actual_mass_ratio = (
        copper_mass
        / aluminium_mass
    )
 
    assert_close(
        actual_mass_ratio,
        expected_mass_ratio,
    )
 
    # --------------------------------------------------
    # Linear volume-to-mass behaviour
    # --------------------------------------------------
 
    unit_volume_mass = component_mass(
        1.0,
        AL6063_T5,
    )
 
    assert_close(
        unit_volume_mass,
        AL6063_T5.density,
    )
 
    doubled_volume_mass = component_mass(
        solid_volume * 2.0,
        AL6063_T5,
    )
 
    assert_close(
        doubled_volume_mass,
        aluminium_mass * 2.0,
    )
 
    # --------------------------------------------------
    # Invalid volume
    # --------------------------------------------------
 
    assert_value_error(
        "'solid_volume_m3' must be greater",
        0.0,
        AL6063_T5,
    )
 
    assert_value_error(
        "'solid_volume_m3' must be greater",
        -1.0,
        AL6063_T5,
    )
 
    assert_value_error(
        "'solid_volume_m3' must be finite",
        float("inf"),
        AL6063_T5,
    )
 
    assert_value_error(
        "'solid_volume_m3' must be finite",
        float("nan"),
        AL6063_T5,
    )
 
    # --------------------------------------------------
    # Invalid material density
    # --------------------------------------------------
 
    zero_density_material = Material(
        name="Invalid",
        grade="Zero Density",
        thermal_conductivity=1.0,
        density=0.0,
    )
 
    assert_value_error(
        "Material density must be greater",
        solid_volume,
        zero_density_material,
    )
 
    negative_density_material = Material(
        name="Invalid",
        grade="Negative Density",
        thermal_conductivity=1.0,
        density=-1.0,
    )
 
    assert_value_error(
        "Material density must be greater",
        solid_volume,
        negative_density_material,
    )
 
    infinite_density_material = Material(
        name="Invalid",
        grade="Infinite Density",
        thermal_conductivity=1.0,
        density=float("inf"),
    )
 
    assert_value_error(
        "Material density must be finite",
        solid_volume,
        infinite_density_material,
    )
 
    nan_density_material = Material(
        name="Invalid",
        grade="NaN Density",
        thermal_conductivity=1.0,
        density=float("nan"),
    )
 
    assert_value_error(
        "Material density must be finite",
        solid_volume,
        nan_density_material,
    )
 
    # --------------------------------------------------
    # Invalid material type
    # --------------------------------------------------
 
    try:
        component_mass(
            solid_volume,
            material=None,
        )
 
    except TypeError as exc:
        assert (
            "'material' must be a Material instance"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid material type was accepted."
        )
 
    print(
        "ALL MASS MODEL CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()