"""
objective_registry.py
 
Central registry of optimization objectives currently
supported by the Thermal AI Engineer.
"""
 
from models.optimization_objective import (
    ObjectiveDirection,
    OptimizationObjective,
)
 
 
THERMAL_RESISTANCE_OBJECTIVE = OptimizationObjective(
    name="Thermal Resistance",
    candidate_attribute="thermal_resistance",
    direction=ObjectiveDirection.MINIMIZE,
    unit="°C/W",
    description=(
        "Overall thermal resistance from the heat-sink "
        "base to ambient air."
    ),
)
 
 
PRESSURE_DROP_OBJECTIVE = OptimizationObjective(
    name="Pressure Drop",
    candidate_attribute="pressure_drop",
    direction=ObjectiveDirection.MINIMIZE,
    unit="Pa",
    description=(
        "Static-pressure loss across the heat-sink "
        "flow passages."
    ),
)
 
 
PUMPING_POWER_OBJECTIVE = OptimizationObjective(
    name="Pumping Power",
    candidate_attribute="pumping_power",
    direction=ObjectiveDirection.MINIMIZE,
    unit="W",
    description=(
        "Fluid power required to overcome the calculated "
        "pressure drop at the operating flow rate."
    ),
)


MASS_OBJECTIVE = OptimizationObjective(
    name="Mass",
    candidate_attribute="mass",
    direction=ObjectiveDirection.MINIMIZE,
    unit="kg",
    description=(
        "Total solid material mass of the evaluated "
        "heat-sink candidate."
    ),
)
 
OBJECTIVE_REGISTRY: dict[
    str,
    OptimizationObjective,
] = {
    "thermal_resistance": (
        THERMAL_RESISTANCE_OBJECTIVE
    ),
    "pressure_drop": PRESSURE_DROP_OBJECTIVE,
    "pumping_power": PUMPING_POWER_OBJECTIVE,
    "mass": MASS_OBJECTIVE,
}
 
 
DEFAULT_OPTIMIZATION_OBJECTIVES: tuple[
    OptimizationObjective,
    ...,
] = (
    THERMAL_RESISTANCE_OBJECTIVE,
    PRESSURE_DROP_OBJECTIVE,
    PUMPING_POWER_OBJECTIVE,
)
 
 
def get_optimization_objective(
    objective_key: str,
) -> OptimizationObjective:
    """
    Return one registered optimization objective.
    """
 
    normalized_key = objective_key.strip().lower()
 
    try:
        return OBJECTIVE_REGISTRY[normalized_key]
 
    except KeyError as exc:
        available_keys = ", ".join(
            sorted(OBJECTIVE_REGISTRY)
        )
 
        raise ValueError(
            (
                f"Unknown optimization objective "
                f"'{objective_key}'. Available objectives: "
                f"{available_keys}."
            )
        ) from exc
 
 
def list_optimization_objectives(
) -> tuple[OptimizationObjective, ...]:
    """
    Return all currently supported objectives.
    """
 
    return tuple(
        OBJECTIVE_REGISTRY.values()
    )