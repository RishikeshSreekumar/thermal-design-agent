"""
Regression checks for MaterialCostProfile.
 
The regression verifies that:
 
- Valid commercial cost data is accepted.
- Identifiers are normalized.
- Cost per kilogram must be positive and finite.
- Currency codes must contain three letters.
- Pricing basis and material key cannot be empty.
- Effective date must use datetime.date.
- The model remains immutable.
"""
 
import math
from dataclasses import FrozenInstanceError
from datetime import date
 
from models.material_cost import (
    MaterialCostProfile,
)
 
 
def assert_value_error(
    expected_message: str,
    **profile_arguments,
) -> None:
    """
    Verify that invalid profile arguments produce the
    expected ValueError.
    """
 
    try:
        MaterialCostProfile(
            **profile_arguments
        )
 
    except ValueError as exc:
        assert expected_message in str(exc)
 
    else:
        raise AssertionError(
            "Invalid material-cost profile was accepted."
        )
 
 
def create_valid_arguments(
) -> dict:
    """
    Return a fresh valid argument dictionary.
 
    The numerical price is an illustrative test fixture,
    not a current supplier or market price.
    """
 
    return {
        "material_key": "al6063_t5",
        "cost_per_kg": 4.0,
        "currency_code": "USD",
        "pricing_basis": (
            "Illustrative engineering test value"
        ),
        "effective_date": date(
            2026,
            1,
            1,
        ),
    }
 
 
def main() -> None:
    # --------------------------------------------------
    # Valid profile
    # --------------------------------------------------
 
    profile = MaterialCostProfile(
        material_key="  AL6063_T5  ",
        cost_per_kg=4.0,
        currency_code=" usd ",
        pricing_basis=(
            "  Illustrative engineering test value  "
        ),
        effective_date=date(
            2026,
            1,
            1,
        ),
    )
 
    assert (
        profile.material_key
        == "al6063_t5"
    )
 
    assert math.isclose(
        profile.cost_per_kg,
        4.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert profile.currency_code == "USD"
 
    assert (
        profile.pricing_basis
        == "Illustrative engineering test value"
    )
 
    assert (
        profile.effective_date
        == date(
            2026,
            1,
            1,
        )
    )
 
    assert profile.display_unit == "USD/kg"
 
    # --------------------------------------------------
    # Empty material key
    # --------------------------------------------------
 
    arguments = create_valid_arguments()
 
    arguments["material_key"] = "   "
 
    assert_value_error(
        "'material_key' must not be empty",
        **arguments,
    )
 
    # --------------------------------------------------
    # Invalid cost per kilogram
    # --------------------------------------------------
 
    for invalid_cost in (
        0.0,
        -1.0,
    ):
        arguments = create_valid_arguments()
 
        arguments["cost_per_kg"] = (
            invalid_cost
        )
 
        assert_value_error(
            "'cost_per_kg' must be greater than zero",
            **arguments,
        )
 
    for invalid_cost in (
        float("inf"),
        float("-inf"),
        float("nan"),
    ):
        arguments = create_valid_arguments()
 
        arguments["cost_per_kg"] = (
            invalid_cost
        )
 
        assert_value_error(
            "'cost_per_kg' must be finite",
            **arguments,
        )
 
    # --------------------------------------------------
    # Invalid currency code
    # --------------------------------------------------
 
    for invalid_currency_code in (
        "",
        "US",
        "USDD",
        "U1D",
        "$$$",
    ):
        arguments = create_valid_arguments()
 
        arguments["currency_code"] = (
            invalid_currency_code
        )
 
        assert_value_error(
            "'currency_code' must contain exactly "
            "three alphabetic characters",
            **arguments,
        )
 
    # --------------------------------------------------
    # Empty pricing basis
    # --------------------------------------------------
 
    arguments = create_valid_arguments()
 
    arguments["pricing_basis"] = "   "
 
    assert_value_error(
        "'pricing_basis' must not be empty",
        **arguments,
    )
 
    # --------------------------------------------------
    # Invalid effective date
    # --------------------------------------------------
 
    arguments = create_valid_arguments()
 
    arguments["effective_date"] = (
        "2026-01-01"
    )
 
    try:
        MaterialCostProfile(
            **arguments
        )
 
    except TypeError as exc:
        assert (
            "'effective_date' must be a "
            "datetime.date instance"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid effective-date type was accepted."
        )
 
    # --------------------------------------------------
    # Frozen model
    # --------------------------------------------------
 
    try:
        profile.cost_per_kg = 5.0
 
    except FrozenInstanceError:
        pass
 
    else:
        raise AssertionError(
            "MaterialCostProfile must remain immutable."
        )
 
    print(
        "ALL MATERIAL COST PROFILE CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()