"""
Regression checks for deterministic material-cost
calculations.
 
The regression verifies that:
 
- Material cost equals mass multiplied by cost per kg.
- Currency and commercial metadata are preserved.
- Cost scales linearly with mass.
- Invalid mass and profile inputs are rejected.
- The returned result remains immutable.
"""
 
import math
from dataclasses import FrozenInstanceError
from datetime import date
 
from models.material_cost import (
    MaterialCostProfile,
)
from models.material_cost_result import (
    MaterialCostResult,
)
from physics.material_cost_model import (
    calculate_material_cost,
)
 
 
def create_cost_profile(
) -> MaterialCostProfile:
    """
    Create an illustrative deterministic test profile.
 
    The price is a software fixture and not a current
    supplier or market value.
    """
 
    return MaterialCostProfile(
        material_key="al6063_t5",
        cost_per_kg=4.0,
        currency_code="USD",
        pricing_basis=(
            "Illustrative engineering test value"
        ),
        effective_date=date(
            2026,
            1,
            1,
        ),
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
 
 
def assert_invalid_mass(
    mass_kg: float,
    expected_message: str,
) -> None:
    """
    Verify that invalid mass inputs are rejected.
    """
 
    try:
        calculate_material_cost(
            mass_kg=mass_kg,
            cost_profile=create_cost_profile(),
        )
 
    except ValueError as exc:
        assert expected_message in str(exc)
 
    else:
        raise AssertionError(
            "Invalid material-cost mass was accepted."
        )
 
 
def main() -> None:
    cost_profile = create_cost_profile()
 
    # --------------------------------------------------
    # Reference calculation
    # --------------------------------------------------
 
    result = calculate_material_cost(
        mass_kg=0.038394,
        cost_profile=cost_profile,
    )
 
    assert isinstance(
        result,
        MaterialCostResult,
    )
 
    assert_close(
        result.mass_kg,
        0.038394,
    )
 
    assert_close(
        result.cost_per_kg,
        4.0,
    )
 
    assert_close(
        result.amount,
        0.153576,
    )
 
    # --------------------------------------------------
    # Commercial context is preserved
    # --------------------------------------------------
 
    assert (
        result.material_key
        == "al6063_t5"
    )
 
    assert result.currency_code == "USD"
 
    assert result.display_unit == "USD"
 
    assert (
        result.pricing_basis
        == "Illustrative engineering test value"
    )
 
    assert (
        result.effective_date
        == date(
            2026,
            1,
            1,
        )
    )
 
    # --------------------------------------------------
    # Linear mass-to-cost behaviour
    # --------------------------------------------------
 
    doubled_mass_result = (
        calculate_material_cost(
            mass_kg=0.038394 * 2.0,
            cost_profile=cost_profile,
        )
    )
 
    assert_close(
        doubled_mass_result.amount,
        result.amount * 2.0,
    )
 
    one_kilogram_result = (
        calculate_material_cost(
            mass_kg=1.0,
            cost_profile=cost_profile,
        )
    )
 
    assert_close(
        one_kilogram_result.amount,
        cost_profile.cost_per_kg,
    )
 
    # --------------------------------------------------
    # Different currency is preserved without conversion
    # --------------------------------------------------
 
    eur_profile = MaterialCostProfile(
        material_key="al6063_t5",
        cost_per_kg=3.5,
        currency_code="EUR",
        pricing_basis=(
            "Illustrative alternate currency fixture"
        ),
        effective_date=date(
            2026,
            1,
            1,
        ),
    )
 
    eur_result = calculate_material_cost(
        mass_kg=2.0,
        cost_profile=eur_profile,
    )
 
    assert_close(
        eur_result.amount,
        7.0,
    )
 
    assert eur_result.currency_code == "EUR"
 
    # No conversion between USD and EUR is performed.
    assert (
        eur_result.currency_code
        != result.currency_code
    )
 
    # --------------------------------------------------
    # Invalid mass
    # --------------------------------------------------
 
    assert_invalid_mass(
        mass_kg=0.0,
        expected_message=(
            "'mass_kg' must be greater than zero"
        ),
    )
 
    assert_invalid_mass(
        mass_kg=-1.0,
        expected_message=(
            "'mass_kg' must be greater than zero"
        ),
    )
 
    assert_invalid_mass(
        mass_kg=float("inf"),
        expected_message=(
            "'mass_kg' must be finite"
        ),
    )
 
    assert_invalid_mass(
        mass_kg=float("-inf"),
        expected_message=(
            "'mass_kg' must be finite"
        ),
    )
 
    assert_invalid_mass(
        mass_kg=float("nan"),
        expected_message=(
            "'mass_kg' must be finite"
        ),
    )
 
    # --------------------------------------------------
    # Invalid cost-profile type
    # --------------------------------------------------
 
    try:
        calculate_material_cost(
            mass_kg=0.038394,
            cost_profile=None,
        )
 
    except TypeError as exc:
        assert (
            "'cost_profile' must be a "
            "MaterialCostProfile instance"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid material cost-profile type was "
            "accepted."
        )
 
    # --------------------------------------------------
    # Result immutability
    # --------------------------------------------------
 
    try:
        result.amount = 1.0
 
    except FrozenInstanceError:
        pass
 
    else:
        raise AssertionError(
            "MaterialCostResult must remain immutable."
        )
 
    print(
        "ALL MATERIAL COST MODEL CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()