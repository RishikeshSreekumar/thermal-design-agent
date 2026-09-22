"""
Regression checks for the material-cost profile database.
 
The regression verifies that:
 
- Every profile references a known material.
- Database keys match profile material keys.
- Current Havells demonstration profiles use INR.
- Explicit profile currencies are preserved.
- Different currencies may coexist in the database.
- Lookups normalize case and surrounding whitespace.
- Unknown, empty, and invalid key inputs are rejected.
- Profile listing preserves database insertion order.
- Database consistency validation detects invalid
  material/profile configurations.
"""
 
from unittest.mock import patch
 
from materials.material_cost_database import (
    AL6061_T6_COST,
    AL6063_T5_COST,
    COPPER_C110_COST,
    MATERIAL_COST_DATABASE,
    get_material_cost_profile,
    list_material_cost_profiles,
    validate_material_cost_database,
    get_material_cost_profile_for_material,
 
)
from materials.material_database import (
    AL6061_T6,
    AL6063_T5,
    COPPER_C110,
    MATERIAL_DATABASE,
)
from models.material_cost import (
    MaterialCostProfile,
)
 
 
def main() -> None:
    # --------------------------------------------------
    # Database contents
    # --------------------------------------------------
 
    assert set(
        MATERIAL_COST_DATABASE
    ) == {
        "al6063_t5",
        "al6061_t6",
        "copper_c110",
    }
 
    assert (
        MATERIAL_COST_DATABASE[
            "al6063_t5"
        ]
        is AL6063_T5_COST
    )
 
    assert (
        MATERIAL_COST_DATABASE[
            "al6061_t6"
        ]
        is AL6061_T6_COST
    )
 
    assert (
        MATERIAL_COST_DATABASE[
            "copper_c110"
        ]
        is COPPER_C110_COST
    )
 
    # --------------------------------------------------
    # Material-database consistency
    # --------------------------------------------------
 
    assert (
        validate_material_cost_database()
        is None
    )
 
    for database_key, profile in (
        MATERIAL_COST_DATABASE.items()
    ):
        assert database_key in MATERIAL_DATABASE
 
        assert (
            profile.material_key
            == database_key
        )
 
    currencies = {
        profile.currency_code
        for profile in (
            MATERIAL_COST_DATABASE.values()
        )
    }
 
    assert currencies == {"INR"}
 
    # --------------------------------------------------
    # Profile lookup
    # --------------------------------------------------
 
    assert (
        get_material_cost_profile(
            "al6063_t5"
        )
        is AL6063_T5_COST
    )
 
    assert (
        get_material_cost_profile(
            "  AL6061_T6  "
        )
        is AL6061_T6_COST
    )
 
    assert (
        get_material_cost_profile(
            "Copper_C110"
        )
        is COPPER_C110_COST
    )

    assert (
        get_material_cost_profile_for_material(
            AL6063_T5
        )
        is AL6063_T5_COST
    )
 
    assert (
        get_material_cost_profile_for_material(
            AL6061_T6
        )
        is AL6061_T6_COST
    )
 
    assert (
        get_material_cost_profile_for_material(
            COPPER_C110
        )
        is COPPER_C110_COST
    )

    try:
        get_material_cost_profile_for_material(
            None
        )
 
    except TypeError as exc:
        assert (
            "'material' must be a Material instance"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid material object was accepted."
        )
 
    # --------------------------------------------------
    # Profile listing
    # --------------------------------------------------
 
    available_profiles = (
        list_material_cost_profiles()
    )
 
    assert isinstance(
        available_profiles,
        tuple,
    )
 
    assert available_profiles == tuple(
        MATERIAL_COST_DATABASE.values()
    )
 
    assert len(available_profiles) == 3
 
    # --------------------------------------------------
    # Illustrative prices remain distinguishable
    # --------------------------------------------------
 
    assert (
        AL6063_T5_COST.cost_per_kg
        < AL6061_T6_COST.cost_per_kg
    )
 
    assert (
        AL6061_T6_COST.cost_per_kg
        < COPPER_C110_COST.cost_per_kg
    )
 
    # --------------------------------------------------
    # Unknown profile
    # --------------------------------------------------
 
    try:
        get_material_cost_profile(
            "unknown_material"
        )
 
    except KeyError as exc:
        message = str(exc)
 
        assert "unknown_material" in message
        assert "al6063_t5" in message
        assert "al6061_t6" in message
        assert "copper_c110" in message
 
    else:
        raise AssertionError(
            "Unknown material cost profile was accepted."
        )
 
    # --------------------------------------------------
    # Invalid lookup key
    # --------------------------------------------------
 
    try:
        get_material_cost_profile(
            "   "
        )
 
    except ValueError as exc:
        assert (
            "'material_key' must not be empty"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Empty material cost-profile key was "
            "accepted."
        )
 
    try:
        get_material_cost_profile(
            None
        )
 
    except TypeError as exc:
        assert (
            "'material_key' must be a string"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid material cost-profile key type "
            "was accepted."
        )
 
    # --------------------------------------------------
    # Invalid database key/profile mismatch
    # --------------------------------------------------
 
    mismatched_profile = MaterialCostProfile(
        material_key="al6061_t6",
        cost_per_kg=4.5,
        currency_code="USD",
        pricing_basis=(
            "Illustrative mismatch fixture"
        ),
        effective_date=(
            AL6061_T6_COST.effective_date
        ),
    )
 
    with patch.dict(
        MATERIAL_COST_DATABASE,
        {
            "al6063_t5": mismatched_profile,
        },
        clear=True,
    ):
        try:
            validate_material_cost_database()
 
        except ValueError as exc:
            assert (
                "does not match profile material key"
                in str(exc)
            )
 
        else:
            raise AssertionError(
                "Mismatched material cost database "
                "entry was accepted."
            )
 
    # --------------------------------------------------
    # Unknown material reference
    # --------------------------------------------------
 
    unknown_material_profile = (
        MaterialCostProfile(
            material_key="unknown_material",
            cost_per_kg=5.0,
            currency_code="USD",
            pricing_basis=(
                "Illustrative unknown-material fixture"
            ),
            effective_date=(
                AL6063_T5_COST.effective_date
            ),
        )
    )
 
    with patch.dict(
        MATERIAL_COST_DATABASE,
        {
            "unknown_material": (
                unknown_material_profile
            ),
        },
        clear=True,
    ):
        try:
            validate_material_cost_database()
 
        except ValueError as exc:
            assert (
                "references unknown material key"
                in str(exc)
            )
 
        else:
            raise AssertionError(
                "Unknown material reference was "
                "accepted."
            )
 
        # --------------------------------------------------
    # Different explicit currencies are permitted
    # --------------------------------------------------
 
    usd_profile = MaterialCostProfile(
        material_key="al6061_t6",
        cost_per_kg=4.0,
        currency_code="USD",
        pricing_basis=(
            "Illustrative foreign-currency fixture"
        ),
        effective_date=(
            AL6061_T6_COST.effective_date
        ),
    )
 
    with patch.dict(
        MATERIAL_COST_DATABASE,
        {
            "al6063_t5": AL6063_T5_COST,
            "al6061_t6": usd_profile,
        },
        clear=True,
    ):
        assert (
            validate_material_cost_database()
            is None
        )
 
        assert (
            MATERIAL_COST_DATABASE[
                "al6063_t5"
            ].currency_code
            == "INR"
        )
 
        assert (
            MATERIAL_COST_DATABASE[
                "al6061_t6"
            ].currency_code
            == "USD"
        )
 
    # --------------------------------------------------
    # Different explicit currencies are permitted
    # --------------------------------------------------
 
    usd_profile = MaterialCostProfile(
        material_key="al6061_t6",
        cost_per_kg=4.0,
        currency_code="USD",
        pricing_basis=(
            "Illustrative foreign-currency fixture"
        ),
        effective_date=(
            AL6061_T6_COST.effective_date
        ),
    )
 
    with patch.dict(
        MATERIAL_COST_DATABASE,
        {
            "al6063_t5": AL6063_T5_COST,
            "al6061_t6": usd_profile,
        },
        clear=True,
    ):
        assert (
            validate_material_cost_database()
            is None
        )
 
        assert (
            MATERIAL_COST_DATABASE[
                "al6063_t5"
            ].currency_code
            == "INR"
        )
 
        assert (
            MATERIAL_COST_DATABASE[
                "al6061_t6"
            ].currency_code
            == "USD"
        )
 
 
    # --------------------------------------------------
    # Empty database
    # --------------------------------------------------
 
    with patch.dict(
        MATERIAL_COST_DATABASE,
        {},
        clear=True,
    ):
        try:
            validate_material_cost_database()
 
        except ValueError as exc:
            assert (
                "database must not be empty"
                in str(exc)
            )
 
        else:
            raise AssertionError(
                "Empty material cost database was "
                "accepted."
            )
 
    # patch.dict restores the original database.
    assert (
        validate_material_cost_database()
        is None
    )
 
    print(
        "ALL MATERIAL COST DATABASE CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()