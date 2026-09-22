"""
Regression checks for the objective report builder.
"""
 
import math
 
from core.objective_report import evaluate_objectives
from core.objective_registry import (
    DEFAULT_OPTIMIZATION_OBJECTIVES,
)
from models.design_candidate import DesignCandidate
 
 
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
 
 
def main() -> None:
 
    candidate = create_candidate()
 
    report = evaluate_objectives(
        candidate,
        DEFAULT_OPTIMIZATION_OBJECTIVES,
    )
 
    assert len(report.results) == 3
 
    assert math.isclose(
        report.get_value(
            "thermal_resistance"
        ),
        0.680824,
        rel_tol=1e-9,
    )
 
    assert math.isclose(
        report.get_value(
            "pressure_drop"
        ),
        86.189941,
        rel_tol=1e-9,
    )
 
    assert math.isclose(
        report.get_value(
            "pumping_power"
        ),
        0.172379882,
        rel_tol=1e-9,
    )
 
    try:
        report.get_value(
            "weight"
        )
 
    except KeyError:
        pass
 
    else:
        raise AssertionError(
            "Unknown objective should raise KeyError."
        )
 
    print(
        "ALL OBJECTIVE REPORT CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()