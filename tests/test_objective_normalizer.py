"""
Regression checks for objective normalization.
"""
 
import math
 
from core.objective_normalizer import (
    ObjectiveNormalizationError,
    normalize_objective_reports,
)
from models.objective_result import (
    ObjectiveEvaluationResult,
    ObjectiveResult,
)
from models.optimization_objective import (
    ObjectiveDirection,
    OptimizationObjective,
)
 
 
THERMAL_OBJECTIVE = OptimizationObjective(
    name="Thermal Resistance",
    candidate_attribute="thermal_resistance",
    direction=ObjectiveDirection.MINIMIZE,
    unit="°C/W",
)
 
 
MARGIN_OBJECTIVE = OptimizationObjective(
    name="Thermal Margin",
    candidate_attribute="thermal_margin",
    direction=ObjectiveDirection.MAXIMIZE,
    unit="°C",
)
 
 
CONSTANT_OBJECTIVE = OptimizationObjective(
    name="Constant Objective",
    candidate_attribute="constant_value",
    direction=ObjectiveDirection.MINIMIZE,
    unit="-",
)
 
 
def create_report(
    thermal_resistance: float,
    thermal_margin: float,
    constant_value: float,
) -> ObjectiveEvaluationResult:
    return ObjectiveEvaluationResult(
        results=(
            ObjectiveResult(
                objective=THERMAL_OBJECTIVE,
                value=thermal_resistance,
            ),
            ObjectiveResult(
                objective=MARGIN_OBJECTIVE,
                value=thermal_margin,
            ),
            ObjectiveResult(
                objective=CONSTANT_OBJECTIVE,
                value=constant_value,
            ),
        )
    )
 
 
def main() -> None:
    reports = (
        create_report(
            thermal_resistance=0.5,
            thermal_margin=10.0,
            constant_value=4.0,
        ),
        create_report(
            thermal_resistance=0.7,
            thermal_margin=30.0,
            constant_value=4.0,
        ),
        create_report(
            thermal_resistance=0.9,
            thermal_margin=20.0,
            constant_value=4.0,
        ),
    )
 
    normalized_reports = (
        normalize_objective_reports(
            reports
        )
    )
 
    assert len(normalized_reports) == 3
 
    assert math.isclose(
        normalized_reports[0]
        .get_normalized_value(
            "thermal_resistance"
        ),
        0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        normalized_reports[1]
        .get_normalized_value(
            "thermal_resistance"
        ),
        0.5,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        normalized_reports[2]
        .get_normalized_value(
            "thermal_resistance"
        ),
        1.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        normalized_reports[0]
        .get_normalized_value(
            "thermal_margin"
        ),
        1.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        normalized_reports[1]
        .get_normalized_value(
            "thermal_margin"
        ),
        0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        normalized_reports[2]
        .get_normalized_value(
            "thermal_margin"
        ),
        0.5,
        abs_tol=1e-12,
    )
 
    for report in normalized_reports:
        assert math.isclose(
            report.get_normalized_value(
                "constant_value"
            ),
            0.0,
            abs_tol=1e-12,
        )
 
    assert math.isclose(
        normalized_reports[1]
        .get_raw_value(
            "thermal_resistance"
        ),
        0.7,
        abs_tol=1e-12,
    )
 
    try:
        normalize_objective_reports(
            ()
        )
 
    except ObjectiveNormalizationError:
        pass
 
    else:
        raise AssertionError(
            "Empty reports must raise "
            "ObjectiveNormalizationError."
        )
 
    mismatched_report = (
        ObjectiveEvaluationResult(
            results=(
                ObjectiveResult(
                    objective=THERMAL_OBJECTIVE,
                    value=0.6,
                ),
            )
        )
    )
 
    try:
        normalize_objective_reports(
            (
                reports[0],
                mismatched_report,
            )
        )
 
    except ObjectiveNormalizationError:
        pass
 
    else:
        raise AssertionError(
            "Mismatched report structures must raise "
            "ObjectiveNormalizationError."
        )
 
    print(
        "ALL OBJECTIVE NORMALIZER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()