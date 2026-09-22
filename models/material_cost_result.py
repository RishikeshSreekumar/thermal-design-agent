"""
material_cost_result.py
 
Immutable result model for deterministic material-cost
calculations.
"""
 
import math
from dataclasses import dataclass
from datetime import date
 
 
@dataclass(frozen=True)
class MaterialCostResult:
    """
    Result of calculating material cost from component mass
    and a MaterialCostProfile.
 
    Parameters
    ----------
    material_key:
        Normalized key identifying the priced material.
 
    mass_kg:
        Component material mass in kilograms.
 
    cost_per_kg:
        Applied material price per kilogram.
 
    amount:
        Calculated material cost in the stated currency.
 
    currency_code:
        Three-letter currency code.
 
    pricing_basis:
        Commercial or engineering basis of the price.
 
    effective_date:
        Date from which the applied price is effective.
    """
 
    material_key: str
 
    mass_kg: float
 
    cost_per_kg: float
 
    amount: float
 
    currency_code: str
 
    pricing_basis: str
 
    effective_date: date
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the immutable material-cost result.
        """
 
        if not self.material_key.strip():
            raise ValueError(
                "'material_key' must not be empty."
            )
 
        numerical_values = {
            "mass_kg": self.mass_kg,
            "cost_per_kg": self.cost_per_kg,
            "amount": self.amount,
        }
 
        for field_name, value in (
            numerical_values.items()
        ):
            if not math.isfinite(value):
                raise ValueError(
                    f"'{field_name}' must be finite."
                )
 
            if value <= 0.0:
                raise ValueError(
                    f"'{field_name}' must be greater "
                    "than zero."
                )
 
        normalized_currency_code = (
            self.currency_code.strip().upper()
        )
 
        if (
            len(normalized_currency_code) != 3
            or not normalized_currency_code.isalpha()
        ):
            raise ValueError(
                "'currency_code' must contain exactly "
                "three alphabetic characters."
            )
 
        normalized_pricing_basis = (
            self.pricing_basis.strip()
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
            self.material_key.strip().lower(),
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
        Return the result currency for reporting.
        """
 
        return self.currency_code