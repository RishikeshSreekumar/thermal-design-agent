"""
mass_model.py
 
Deterministic mass calculations for thermal-design
components.
 
The module converts solid material volume into component
mass using material density.
 
Material properties remain owned by the material database.
This module does not define or duplicate density values.
"""
 
import math
 
from models.material import Material
 
 
def component_mass(
    solid_volume_m3: float,
    material: Material,
) -> float:
    """
    Calculate component mass from solid volume and material
    density.
 
    Parameters
    ----------
    solid_volume_m3:
        Solid material volume in cubic metres.
 
    material:
        Material containing density in kilograms per cubic
        metre.
 
    Returns
    -------
    float
        Component mass in kilograms.
 
    Raises
    ------
    ValueError
        If volume or material density is non-finite or not
        greater than zero.
 
    TypeError
        If material is not a Material instance.
    """
 
    _validate_mass_inputs(
        solid_volume_m3=solid_volume_m3,
        material=material,
    )
 
    return (
        solid_volume_m3
        * material.density
    )
 
 
def _validate_mass_inputs(
    solid_volume_m3: float,
    material: Material,
) -> None:
    """
    Validate inputs required by the deterministic mass
    model.
    """
 
    if not isinstance(
        material,
        Material,
    ):
        raise TypeError(
            "'material' must be a Material instance."
        )
 
    if not math.isfinite(
        solid_volume_m3
    ):
        raise ValueError(
            "'solid_volume_m3' must be finite."
        )
 
    if solid_volume_m3 <= 0.0:
        raise ValueError(
            "'solid_volume_m3' must be greater "
            "than zero."
        )
 
    if not math.isfinite(
        material.density
    ):
        raise ValueError(
            "Material density must be finite."
        )
 
    if material.density <= 0.0:
        raise ValueError(
            "Material density must be greater "
            "than zero."
        )