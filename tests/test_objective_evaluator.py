"""
Regression checks for the objective evaluator.
"""
 
import math
 
from core.objective_evaluator import (
    ObjectiveEvaluationError,
    evaluate_objective,
)
from models.design_candidate import DesignCandidate
from models.optimization_objective import (
    ObjectiveDirection,
    OptimizationObjective,
)
 
 
def create_candidate() -> DesignCandidate:
    return DesignCandidate(
        base_thickness=3.0,
        fin_thickness=0.8,
        fin_height=8.0,
        fin_spacing=1.6,
        fin_count=21,
        total_height=11.0,
 
        gross_frontal_area=0.0004,
        open_flow_area=0.000256,
        blockage_ratio=0.36,
        approach_velocity=5.0,
        channel_velocity=7.8125,
 
        reynolds_number=1295.405982905983,
        nusselt_number=7.54,
        heat_transfer_coefficient=74.36325,
 
        friction_factor=0.049405,
        pressure_drop=86.189941,
        pumping_power=0.172379882,
 
        thermal_resistance=0.680824,
        estimated_base_temperature=142.336,
    )
 
 
def assert_raises_evaluation_error(
    candidate: DesignCandidate,
    objective: OptimizationObjective,
) -> None:
    try:
        evaluate_objective(
            candidate,
            objective,
        )
 
    except ObjectiveEvaluationError:
        return
 
    raise AssertionError(
        "Expected ObjectiveEvaluationError."
    )
 
 
def main() -> None:
    candidate = create_candidate()
 
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
 
    thermal_value = evaluate_objective(
        candidate,
        thermal_objective,
    )
 
    pressure_drop_value = evaluate_objective(
        candidate,
        pressure_drop_objective,
    )
 
    assert math.isclose(
        thermal_value,
        0.680824,
        rel_tol=1e-9,
    )
 
    assert math.isclose(
        pressure_drop_value,
        86.189941,
        rel_tol=1e-9,
    )
 
    invalid_attribute_objective = (
        OptimizationObjective(
            name="Invalid Objective",
            candidate_attribute=(
                "attribute_that_does_not_exist"
            ),
            direction=ObjectiveDirection.MINIMIZE,
            unit="-",
        )
    )
 
    assert_raises_evaluation_error(
        candidate,
        invalid_attribute_objective,
    )
 
    candidate.thermal_resistance = float("nan")
 
    assert_raises_evaluation_error(
        candidate,
        thermal_objective,
    )
 
    print(
        "ALL OBJECTIVE EVALUATOR CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()