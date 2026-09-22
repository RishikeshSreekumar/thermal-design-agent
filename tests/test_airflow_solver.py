"""
Regression tests for the airflow solver.
"""
 
from core.airflow_solver import solve_candidate_airflow
from fan.fan_database import get_fan_curve
 
 
def test_airflow_solver_returns_valid_state() -> None:
 
    fan_curve = get_fan_curve(
        "demo_120mm"
    )
 
    result = solve_candidate_airflow(
        fan_curve=fan_curve,
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    assert result.volumetric_flow_rate > 0.0
    assert result.approach_velocity > 0.0
    assert result.channel_velocity > 0.0
 
    assert result.reynolds_number > 0.0
    assert result.pressure_drop > 0.0
    assert result.pumping_power > 0.0
 
 
if __name__ == "__main__":
 
    test_airflow_solver_returns_valid_state()
 
    print(
        "ALL AIRFLOW SOLVER CHECKS PASSED"
    )
 