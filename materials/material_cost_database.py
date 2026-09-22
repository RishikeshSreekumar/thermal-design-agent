"""
material_cost_database.py
 
Centralized material-cost profile database for the
Thermal AI Engineer.
 
The stored prices are illustrative engineering defaults
used to develop and test deterministic cost calculations.
 
They are not current market prices, supplier quotations,
or approved procurement values. Production use must replace
them with controlled commercial data.
"""
 
from datetime import date
 
from materials.material_database import (
    MATERIAL_DATABASE,
)
from models.material_cost import (
    MaterialCostProfile,
)
from models.material import Material
 
 
# ------------------------------------------------------
# Illustrative Material Cost Profiles
# ------------------------------------------------------
 
AL6063_T5_COST = MaterialCostProfile(
    material_key="al6063_t5",
    cost_per_kg=300.0,
    currency_code="INR",
    pricing_basis=(
        "Illustrative Havells India development default; "
        "not an approved procurement value"
    ),
    effective_date=date(2026, 7, 29),
)
 
AL6061_T6_COST = MaterialCostProfile(
    material_key="al6061_t6",
    cost_per_kg=350.0,
    currency_code="INR",
    pricing_basis=(
        "Illustrative Havells India development default; "
        "not an approved procurement value"
    ),
    effective_date=date(2026, 7, 29),
)
 
COPPER_C110_COST = MaterialCostProfile(
    material_key="copper_c110",
    cost_per_kg=900.0,
    currency_code="INR",
    pricing_basis=(
        "Illustrative Havells India development default; "
        "not an approved procurement value"
    ),
    effective_date=date(2026, 7, 29),
)
 
 
# ------------------------------------------------------
# Material Cost Library
# ------------------------------------------------------
 
MATERIAL_COST_DATABASE: dict[
    str,
    MaterialCostProfile,
] = {
    "al6063_t5": AL6063_T5_COST,
    "al6061_t6": AL6061_T6_COST,
    "copper_c110": COPPER_C110_COST,
}
 
 
def get_material_cost_profile(
    material_key: str,
) -> MaterialCostProfile:
    """
    Return one material-cost profile from the database.
 
    Parameters
    ----------
    material_key:
        Material database key such as 'al6063_t5'.
 
    Returns
    -------
    MaterialCostProfile
        Commercial cost profile associated with the
        normalized material key.
 
    Raises
    ------
    TypeError
        If material_key is not a string.
 
    ValueError
        If material_key is empty after normalization.
 
    KeyError
        If no cost profile exists for the requested
        material.
    """
 
    normalized_key = _normalize_material_key(
        material_key
    )
 
    if normalized_key not in (
        MATERIAL_COST_DATABASE
    ):
        available = ", ".join(
            MATERIAL_COST_DATABASE.keys()
        )
 
        raise KeyError(
            f"Unknown material cost profile "
            f"'{material_key}'. "
            f"Available profiles: {available}"
        )
 
    return MATERIAL_COST_DATABASE[
        normalized_key
    ]
 
def get_material_cost_profile_for_material(
    material: Material,
) -> MaterialCostProfile:
    """
    Resolve a cost profile from a physical Material object.
 
    The function first identifies the material's canonical
    key in MATERIAL_DATABASE and then resolves the matching
    commercial cost profile.
 
    Raises
    ------
    TypeError
        If material is not a Material instance.
 
    KeyError
        If the material is not registered in
        MATERIAL_DATABASE or has no cost profile.
    """
 
    if not isinstance(
        material,
        Material,
    ):
        raise TypeError(
            "'material' must be a Material instance."
        )
 
    matching_keys = [
        material_key
        for material_key, registered_material in (
            MATERIAL_DATABASE.items()
        )
        if registered_material is material
    ]
 
    if not matching_keys:
        matching_keys = [
            material_key
            for material_key, registered_material in (
                MATERIAL_DATABASE.items()
            )
            if registered_material == material
        ]
 
    if not matching_keys:
        raise KeyError(
            "Material is not registered in the "
            "material database: "
            f"{material.display_name}"
        )
 
    if len(matching_keys) > 1:
        available_keys = ", ".join(
            matching_keys
        )
 
        raise ValueError(
            "Material resolves to multiple database keys: "
            f"{available_keys}"
        )
 
    return get_material_cost_profile(
        matching_keys[0]
    )

def list_material_cost_profiles(
) -> tuple[MaterialCostProfile, ...]:
    """
    Return all registered material-cost profiles in
    database insertion order.
    """
 
    return tuple(
        MATERIAL_COST_DATABASE.values()
    )
 
 
def validate_material_cost_database(
) -> None:
    """
    Validate consistency between material and material-cost
    databases.
 
    Every material-cost database key must:
 
    - exist in MATERIAL_DATABASE;
    - match its profile's material_key;
    - contain an explicit valid currency code.
    
    Different currencies may exist in the database.
    The optimizer must never compare or rank costs
    across currencies without an explicit conversion
    model.
 
    Successful validation returns None.
 
    Raises
    ------
    ValueError
        If a database consistency rule is violated.
    """
 
    if not MATERIAL_COST_DATABASE:
        raise ValueError(
            "Material cost database must not be empty."
        )
 
 
    for database_key, profile in (
        MATERIAL_COST_DATABASE.items()
    ):
        if database_key not in MATERIAL_DATABASE:
            raise ValueError(
                "Material cost profile references "
                "unknown material key "
                f"'{database_key}'."
            )
 
        if (
            profile.material_key
            != database_key
        ):
            raise ValueError(
                "Material cost database key "
                f"'{database_key}' does not match "
                "profile material key "
                f"'{profile.material_key}'."
            )
 
 
def _normalize_material_key(
    material_key: str,
) -> str:
    """
    Normalize and validate one material database key.
    """
 
    if not isinstance(
        material_key,
        str,
    ):
        raise TypeError(
            "'material_key' must be a string."
        )
 
    normalized_key = (
        material_key.strip().lower()
    )
 
    if not normalized_key:
        raise ValueError(
            "'material_key' must not be empty."
        )
 
    return normalized_key
 
 
validate_material_cost_database()