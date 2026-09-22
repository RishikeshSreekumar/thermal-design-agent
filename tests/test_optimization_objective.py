"""
Regression checks for optimization-objective models.
"""
 
from dataclasses import FrozenInstanceError
 
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
        description=(
            "Overall thermal resistance from the heat-sink "
            "base to ambient air."
        ),
    )
 
    pressure_drop_objective = OptimizationObjective(
        name="Pressure Drop",
        candidate_attribute="pressure_drop",
        direction=ObjectiveDirection.MINIMIZE,
        unit="Pa",
        description=(
            "Static-pressure loss across the heat-sink "
            "flow passages."
        ),
    )
 
    assert (
        thermal_objective.name
        == "Thermal Resistance"
    )
 
    assert (
        thermal_objective.candidate_attribute
        == "thermal_resistance"
    )
 
    assert (
        thermal_objective.direction
        is ObjectiveDirection.MINIMIZE
    )
 
    assert thermal_objective.unit == "°C/W"
 
    assert (
        pressure_drop_objective.candidate_attribute
        == "pressure_drop"
    )
 
    assert (
        pressure_drop_objective.direction
        is ObjectiveDirection.MINIMIZE
    )
 
    try:
        thermal_objective.name = "Changed Name"
 
    except FrozenInstanceError:
        pass
 
    else:
        raise AssertionError(
            "OptimizationObjective must be immutable."
        )
 
    print(
        "ALL OPTIMIZATION OBJECTIVE MODEL CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()