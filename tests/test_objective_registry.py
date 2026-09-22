"""
Regression checks for the optimization-objective registry.
"""
 
from core.objective_registry import (
    DEFAULT_OPTIMIZATION_OBJECTIVES,
    MASS_OBJECTIVE,
    OBJECTIVE_REGISTRY,
    get_optimization_objective,
    list_optimization_objectives,
)
from models.optimization_objective import (
    ObjectiveDirection,
    OptimizationObjective,
)
 
 
def main() -> None:
    assert set(OBJECTIVE_REGISTRY) == {
        "thermal_resistance",
        "pressure_drop",
        "pumping_power",
        "mass",
    }
 
    thermal_objective = (
        get_optimization_objective(
            "thermal_resistance"
        )
    )
 
    pressure_drop_objective = (
        get_optimization_objective(
            " PRESSURE_DROP "
        )
    )
 
    pumping_power_objective = (
        get_optimization_objective(
            "Pumping_Power"
        )
    )

    mass_objective = (
        get_optimization_objective(
            " MASS "
        )
    )
 
    assert isinstance(
        thermal_objective,
        OptimizationObjective,
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
        pressure_drop_objective
        .candidate_attribute
        == "pressure_drop"
    )
 
    assert pressure_drop_objective.unit == "Pa"
 
    assert (
        pumping_power_objective
        .candidate_attribute
        == "pumping_power"
    )
 
    assert pumping_power_objective.unit == "W"

    assert mass_objective is MASS_OBJECTIVE
 
    assert (
        mass_objective.candidate_attribute
        == "mass"
    )
 
    assert (
        mass_objective.direction
        is ObjectiveDirection.MINIMIZE
    )
 
    assert mass_objective.unit == "kg"
 
    available_objectives = (
        list_optimization_objectives()
    )
 
    assert isinstance(
        available_objectives,
        tuple,
    )
 
    assert len(available_objectives) == 4
 
    assert (
        DEFAULT_OPTIMIZATION_OBJECTIVES
        == (
            OBJECTIVE_REGISTRY[
                "thermal_resistance"
            ],
            OBJECTIVE_REGISTRY[
                "pressure_drop"
            ],
            OBJECTIVE_REGISTRY[
                "pumping_power"
            ],
        )
    )
 
    assert (
        MASS_OBJECTIVE
        not in DEFAULT_OPTIMIZATION_OBJECTIVES
    )
 
    try:
        get_optimization_objective(
            "invalid_objective"
        )
 
    except ValueError as exc:
        message = str(exc)
 
        assert "invalid_objective" in message
        assert "thermal_resistance" in message
        assert "pressure_drop" in message
        assert "pumping_power" in message
        assert "mass" in message
 
    else:
        raise AssertionError(
            "Unknown objective key must raise ValueError."
        )
 
    print(
        "ALL OBJECTIVE REGISTRY CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()