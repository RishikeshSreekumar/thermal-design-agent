"""
Regression checks for currency-aware material-cost budgets.
"""
 
from models.requirements import (
    MaterialCostBudget,
)
 
 
def test_default_currency_is_inr() -> None:
    budget = MaterialCostBudget(
        maximum_amount=500.0,
    )
 
    assert budget.maximum_amount == 500.0
    assert budget.currency_code == "INR"
 
 
def test_currency_code_is_normalized() -> None:
    budget = MaterialCostBudget(
        maximum_amount=500.0,
        currency_code=" inr ",
    )
 
    assert budget.currency_code == "INR"
 
 
def test_explicit_usd_budget_is_supported() -> None:
    budget = MaterialCostBudget(
        maximum_amount=25.0,
        currency_code="usd",
    )
 
    assert budget.maximum_amount == 25.0
    assert budget.currency_code == "USD"
 
 
def test_zero_budget_is_rejected() -> None:
    try:
        MaterialCostBudget(
            maximum_amount=0.0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Zero material-cost budget should be rejected."
        )
 
 
def test_negative_budget_is_rejected() -> None:
    try:
        MaterialCostBudget(
            maximum_amount=-1.0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Negative material-cost budget should be rejected."
        )
 
 
def test_invalid_currency_code_is_rejected() -> None:
    invalid_currency_codes = (
        "",
        "IN",
        "INRR",
        "12R",
    )
 
    for currency_code in invalid_currency_codes:
        try:
            MaterialCostBudget(
                maximum_amount=500.0,
                currency_code=currency_code,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Invalid currency code should be rejected: "
                f"{currency_code!r}"
            )
 
 
def main() -> None:
    test_default_currency_is_inr()
    test_currency_code_is_normalized()
    test_explicit_usd_budget_is_supported()
    test_zero_budget_is_rejected()
    test_negative_budget_is_rejected()
    test_invalid_currency_code_is_rejected()
 
    print(
        "ALL MATERIAL COST BUDGET CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()