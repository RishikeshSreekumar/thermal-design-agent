"""
Regression tests for the coupled fan-system solver.
"""
 
from fan.coupled_solver import solve_coupled_flow
from fan.fan_database import get_fan_curve
 
 
def test_quadratic_system_converges() -> None:
    """
    A purely quadratic pressure-drop model should
    converge to the fan/system operating point.
    """
 
    fan_curve = get_fan_curve(
        "demo_120mm"
    )
 
    resistance_coefficient = 10000.0
 
    def pressure_drop_function(
        volumetric_flow_rate: float,
    ) -> float:
        return (
            resistance_coefficient
            * volumetric_flow_rate ** 2
        )
 
    result = solve_coupled_flow(
        fan_curve=fan_curve,
        pressure_drop_function=(
            pressure_drop_function
        ),
    )
 
    assert result.volumetric_flow_rate > 0.0
    assert result.fan_pressure >= 0.0
    assert result.system_pressure_drop >= 0.0
 
    pressure_difference = abs(
        result.fan_pressure
        - result.system_pressure_drop
    )
 
    assert pressure_difference < 1.0
 
    assert (
        abs(
            result.resistance_coefficient
            - resistance_coefficient
        )
        < 1e-6
    )
 
 
def test_nonlinear_system_converges() -> None:
    """
    The solver should also converge when the effective
    resistance changes with flow rate.
    """
 
    fan_curve = get_fan_curve(
        "demo_120mm"
    )
 
    def pressure_drop_function(
        volumetric_flow_rate: float,
    ) -> float:
        effective_resistance = (
            8000.0
            + 20000.0
            * volumetric_flow_rate
        )
 
        return (
            effective_resistance
            * volumetric_flow_rate ** 2
        )
 
    result = solve_coupled_flow(
        fan_curve=fan_curve,
        pressure_drop_function=(
            pressure_drop_function
        ),
    )
 
    assert result.volumetric_flow_rate > 0.0
    assert result.iteration_count >= 1
    assert result.flow_rate_error <= 1e-6
 
    pressure_difference = abs(
        result.fan_pressure
        - result.system_pressure_drop
    )
 
    assert pressure_difference < 1.0
 
 
def test_negative_pressure_drop_is_rejected() -> None:
    """
    The system-pressure function must not return a
    negative pressure drop.
    """
 
    fan_curve = get_fan_curve(
        "demo_120mm"
    )
 
    def invalid_pressure_drop_function(
        volumetric_flow_rate: float,
    ) -> float:
        return -10.0
 
    try:
        solve_coupled_flow(
            fan_curve=fan_curve,
            pressure_drop_function=(
                invalid_pressure_drop_function
            ),
        )
 
    except ValueError as exc:
        assert (
            "pressure drop cannot be negative"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Negative pressure drop was not rejected."
        )
 
 
def test_invalid_relaxation_factor_is_rejected() -> None:
    """
    Relaxation must remain within the interval
    greater than 0 and no greater than 1.
    """
 
    fan_curve = get_fan_curve(
        "demo_120mm"
    )
 
    def pressure_drop_function(
        volumetric_flow_rate: float,
    ) -> float:
        return 10000.0 * volumetric_flow_rate ** 2
 
    try:
        solve_coupled_flow(
            fan_curve=fan_curve,
            pressure_drop_function=(
                pressure_drop_function
            ),
            relaxation_factor=1.5,
        )
 
    except ValueError as exc:
        assert (
            "Relaxation factor"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Invalid relaxation factor was not rejected."
        )
 
 
if __name__ == "__main__":
    test_quadratic_system_converges()
    test_nonlinear_system_converges()
    test_negative_pressure_drop_is_rejected()
    test_invalid_relaxation_factor_is_rejected()
 
    print("ALL COUPLED SOLVER CHECKS PASSED")