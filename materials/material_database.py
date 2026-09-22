"""
material_database.py
 
Material-property database for the Thermal AI Engineer.
 
The database stores the material properties required for
thermal calculations, weight estimation, and design ranking.
 
Values are initial engineering defaults and should later be
validated against approved internal or supplier data.
"""
 
from models.material import Material
 
 
# ------------------------------------------------------
# Aluminium Alloys
# ------------------------------------------------------
 
AL6063_T5 = Material(
    name="Aluminium",
    grade="6063-T5",
    thermal_conductivity=201.0,
    density=2700.0,
)
 
AL6061_T6 = Material(
    name="Aluminium",
    grade="6061-T6",
    thermal_conductivity=167.0,
    density=2700.0,
)
 
 
# ------------------------------------------------------
# Copper
# ------------------------------------------------------
 
COPPER_C110 = Material(
    name="Copper",
    grade="C110",
    thermal_conductivity=391.0,
    density=8960.0,
)
 
 
# ------------------------------------------------------
# Material Library
# ------------------------------------------------------
 
MATERIAL_DATABASE = {
    "al6063_t5": AL6063_T5,
    "al6061_t6": AL6061_T6,
    "copper_c110": COPPER_C110,
}
 
 
def get_material(
    material_key: str,
) -> Material:
    """
    Return a material from the database.
 
    Parameters
    ----------
    material_key:
        Database key such as 'al6063_t5'.
 
    Raises
    ------
    KeyError
        If the requested material does not exist.
    """
 
    normalized_key = material_key.strip().lower()
 
    if normalized_key not in MATERIAL_DATABASE:
        available = ", ".join(
            MATERIAL_DATABASE.keys()
        )
 
        raise KeyError(
            f"Unknown material '{material_key}'. "
            f"Available materials: {available}"
        )
 
    return MATERIAL_DATABASE[normalized_key]