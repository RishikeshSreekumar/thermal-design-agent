"""
material_cost_model.py
 
Deterministic material-cost calculations.
 
This module converts component mass into material cost
using an externally supplied MaterialCostProfile.
 
It does not define material prices, perform currency
conversion, or estimate manufacturing cost.
"""
 
import math
 
from models.material_cost import (
    MaterialCostProfile,
)
from models.material_cost_result import (
    MaterialCostResult,
)
 
 
def calculate_material_cost(
    mass_kg: float,
    cost_profile: MaterialCostProfile,
) -> MaterialCostResult:
    """
    Calculate component material cost.
 
    Parameters
    ----------
    mass_kg:
        Solid component mass in kilograms.
 
    cost_profile:
        Commercial cost profile containing price per
        kilogram and associated pricing metadata.
 
    Returns
    -------
    MaterialCostResult
        Calculated cost with preserved currency and pricing
        context.
 
    Raises
    ------
    TypeError
        If cost_profile is not a MaterialCostProfile.
 
    ValueError
        If mass is non-finite or not greater than zero.
    """
 
    _validate_material_cost_inputs(
        mass_kg=mass_kg,
        cost_profile=cost_profile,
    )
 
    amount = (
        mass_kg
        * cost_profile.cost_per_kg
    )
 
    if not math.isfinite(amount):
        raise ValueError(
            "Calculated material cost must be finite."
        )
 
    if amount <= 0.0:
        raise ValueError(
            "Calculated material cost must be greater "
            "than zero."
        )
 
    return MaterialCostResult(
        material_key=(
            cost_profile.material_key
        ),
        mass_kg=mass_kg,
        cost_per_kg=(
            cost_profile.cost_per_kg
        ),
        amount=amount,
        currency_code=(
            cost_profile.currency_code
        ),
        pricing_basis=(
            cost_profile.pricing_basis
        ),
        effective_date=(
            cost_profile.effective_date
        ),
    )
 
 
def _validate_material_cost_inputs(
    mass_kg: float,
    cost_profile: MaterialCostProfile,
) -> None:
    """
    Validate deterministic material-cost inputs.
    """
 
    if not isinstance(
        cost_profile,
        MaterialCostProfile,
    ):
        raise TypeError(
            "'cost_profile' must be a "
            "MaterialCostProfile instance."
        )
 
    if not math.isfinite(mass_kg):
        raise ValueError(
            "'mass_kg' must be finite."
        )
 
    if mass_kg <= 0.0:
        raise ValueError(
            "'mass_kg' must be greater than zero."
        )