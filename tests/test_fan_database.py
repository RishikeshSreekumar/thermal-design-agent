"""
Regression tests for the fan database.
"""
 
from fan.fan_database import get_fan_curve
 
 
def test_known_fan_can_be_retrieved() -> None:
    """
    A registered fan should return its performance curve.
    """
 
    fan_curve = get_fan_curve("demo_120mm")
 
    assert fan_curve.minimum_flow_rate == 0.0
    assert fan_curve.maximum_flow_rate == 0.10
 
    assert fan_curve.pressure_at_flow_rate(0.00) == 120.0
    assert fan_curve.pressure_at_flow_rate(0.10) == 0.0
 
 
def test_retrieved_curve_interpolates_pressure() -> None:
    """
    The retrieved fan curve should retain interpolation
    behaviour.
    """
 
    fan_curve = get_fan_curve("demo_120mm")
 
    interpolated_pressure = (
        fan_curve.pressure_at_flow_rate(0.05)
    )
 
    assert abs(interpolated_pressure - 79.0) < 1e-9
 
 
def test_unknown_fan_is_rejected() -> None:
    """
    An unregistered fan name should produce a clear error.
    """
 
    try:
        get_fan_curve("unknown_fan")
 
    except ValueError as exc:
        assert "Unknown fan 'unknown_fan'." in str(exc)
 
    else:
        raise AssertionError(
            "Unknown fan name did not raise ValueError."
        )
 
 
if __name__ == "__main__":
    test_known_fan_can_be_retrieved()
    test_retrieved_curve_interpolates_pressure()
    test_unknown_fan_is_rejected()
 
    print("ALL FAN DATABASE CHECKS PASSED")