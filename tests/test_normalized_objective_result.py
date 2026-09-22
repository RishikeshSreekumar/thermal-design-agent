"""
Regression checks for normalized objective-result models.
"""
 
import math
 
from models.objective_result import (
    NormalizedObjectiveEvaluationResult,
    NormalizedObjectiveResult,
)
from models.optimization_objective import (
    ObjectiveDirection,
    OptimizationObjective,
)
 
 
def main() -> None:
    thermal_objective = OptimizationObjective(
        name="Thermal Resistance",
        candidate_attribute="thermal_resistance",
        direction=ObjectiveDirection.MINIMIZE,
        unit="°C/W",
    )
 
    pressure_drop_objective = OptimizationObjective(
        name="Pressure Drop",
        candidate_attribute="pressure_drop",
        direction=ObjectiveDirection.MINIMIZE,
        unit="Pa",
    )
 
    report = NormalizedObjectiveEvaluationResult(
        results=(
            NormalizedObjectiveResult(
                objective=thermal_objective,
                raw_value=0.680824,
                normalized_value=0.25,
            ),
            NormalizedObjectiveResult(
                objective=pressure_drop_objective,
                raw_value=86.189941,
                normalized_value=0.75,
            ),
        )
    )
 
    assert len(report.results) == 2
 
    assert math.isclose(
        report.get_raw_value(
            "thermal_resistance"
        ),
        0.680824,
        rel_tol=1e-9,
    )
 
    assert math.isclose(
        report.get_normalized_value(
            "thermal_resistance"
        ),
        0.25,
        rel_tol=1e-9,
    )
 
    assert math.isclose(
        report.get_raw_value(
            "pressure_drop"
        ),
        86.189941,
        rel_tol=1e-9,
    )
 
    assert math.isclose(
        report.get_normalized_value(
            "pressure_drop"
        ),
        0.75,
        rel_tol=1e-9,
    )
 
    try:
        report.get_normalized_value(
            "unknown_objective"
        )
 
    except KeyError:
        pass
 
    else:
        raise AssertionError(
            "Unknown normalized objective must "
            "raise KeyError."
        )
 
    print(
        "ALL NORMALIZED OBJECTIVE RESULT "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()