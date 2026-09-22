"""
material_cost.py
 
Commercial material-cost property model.
 
Material pricing is intentionally kept separate from the
stable thermal and physical properties stored in Material.
 
Prices may vary by supplier, purchasing volume, region,
material form, and effective date.
"""
 
import math
from dataclasses import dataclass
from datetime import date
 
 
@dataclass(frozen=True)
class MaterialCostProfile:
    """
    Commercial cost information for one material.
 
    Parameters
    ----------
    material_key:
        Key identifying the corresponding material in the
        material database.
 
    cost_per_kg:
        Material cost per kilogram in the stated currency.
 
    currency_code:
        Three-letter currency code such as "USD".
 
    pricing_basis:
        Human-readable description of the price source or
        commercial basis.
 
    effective_date:
        Date from which the pricing information applies.
    """
 
    material_key: str
 
    cost_per_kg: float
 
    currency_code: str
 
    pricing_basis: str
 
    effective_date: date
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the immutable material-cost profile.
        """
 
        normalized_material_key = (
            self.material_key.strip().lower()
        )
 
        normalized_currency_code = (
            self.currency_code.strip().upper()
        )
 
        normalized_pricing_basis = (
            self.pricing_basis.strip()
        )
 
        if not normalized_material_key:
            raise ValueError(
                "'material_key' must not be empty."
            )
 
        if not math.isfinite(
            self.cost_per_kg
        ):
            raise ValueError(
                "'cost_per_kg' must be finite."
            )
 
        if self.cost_per_kg <= 0.0:
            raise ValueError(
                "'cost_per_kg' must be greater "
                "than zero."
            )
 
        if (
            len(normalized_currency_code) != 3
            or not normalized_currency_code.isalpha()
        ):
            raise ValueError(
                "'currency_code' must contain exactly "
                "three alphabetic characters."
            )
 
        if not normalized_pricing_basis:
            raise ValueError(
                "'pricing_basis' must not be empty."
            )
 
        if not isinstance(
            self.effective_date,
            date,
        ):
            raise TypeError(
                "'effective_date' must be a "
                "datetime.date instance."
            )
 
        object.__setattr__(
            self,
            "material_key",
            normalized_material_key,
        )
 
        object.__setattr__(
            self,
            "currency_code",
            normalized_currency_code,
        )
 
        object.__setattr__(
            self,
            "pricing_basis",
            normalized_pricing_basis,
        )
 
    @property
    def display_unit(
        self,
    ) -> str:
        """
        Return the readable monetary unit for reporting.
        """
 
        return (
            f"{self.currency_code}/kg"
        )