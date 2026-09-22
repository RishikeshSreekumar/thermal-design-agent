"""
Regression checks for objective-weight configuration.
"""
 
import math
 
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def assert_value_error(
    callback,
) -> None:
    try:
        callback()
 
    except ValueError:
        return
 
    raise AssertionError(
        "Expected ValueError."
    )
 
 
def main() -> None:
    configuration = ScoringConfiguration(
        objective_weights=(
            ObjectiveWeight(
                objective_key=(
                    " THERMAL_RESISTANCE "
                ),
                weight=60,
            ),
            ObjectiveWeight(
                objective_key="pressure_drop",
                weight=25,
            ),
            ObjectiveWeight(
                objective_key="pumping_power",
                weight=15,
            ),
        )
    )
 
    assert math.isclose(
        configuration.total_weight,
        100.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        configuration.get_weight(
            "thermal_resistance"
        ),
        60.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        configuration.get_weight(
            " PRESSURE_DROP "
        ),
        25.0,
        abs_tol=1e-12,
    )
 
    try:
        configuration.get_weight(
            "unknown_objective"
        )
 
    except KeyError:
        pass
 
    else:
        raise AssertionError(
            "Unknown objective key must raise KeyError."
        )
 
    assert_value_error(
        lambda: ObjectiveWeight(
            objective_key="",
            weight=1.0,
        )
    )
 
    assert_value_error(
        lambda: ObjectiveWeight(
            objective_key="pressure_drop",
            weight=-1.0,
        )
    )
 
    assert_value_error(
        lambda: ObjectiveWeight(
            objective_key="pressure_drop",
            weight=float("nan"),
        )
    )
 
    assert_value_error(
        lambda: ScoringConfiguration(
            objective_weights=()
        )
    )
 
    assert_value_error(
        lambda: ScoringConfiguration(
            objective_weights=(
                ObjectiveWeight(
                    objective_key=(
                        "thermal_resistance"
                    ),
                    weight=1.0,
                ),
                ObjectiveWeight(
                    objective_key=(
                        "THERMAL_RESISTANCE"
                    ),
                    weight=2.0,
                ),
            )
        )
    )
 
    assert_value_error(
        lambda: ScoringConfiguration(
            objective_weights=(
                ObjectiveWeight(
                    objective_key=(
                        "thermal_resistance"
                    ),
                    weight=0.0,
                ),
                ObjectiveWeight(
                    objective_key=(
                        "pressure_drop"
                    ),
                    weight=0.0,
                ),
            )
        )
    )
 
    print(
        "ALL SCORING CONFIGURATION CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()