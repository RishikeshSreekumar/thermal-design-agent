from fan.fan_curve import FanCurve
from fan.fan_curve import FanCurvePoint
 
 
def main() -> None:
    fan_curve = FanCurve(
        points=[
            FanCurvePoint(
                volumetric_flow_rate=0.000,
                static_pressure=120.0,
            ),
            FanCurvePoint(
                volumetric_flow_rate=0.005,
                static_pressure=90.0,
            ),
            FanCurvePoint(
                volumetric_flow_rate=0.010,
                static_pressure=0.0,
            ),
        ]
    )
 
    assert fan_curve.minimum_flow_rate == 0.0
    assert fan_curve.maximum_flow_rate == 0.01
 
    shutoff_pressure = (
        fan_curve.pressure_at_flow_rate(0.0)
    )
 
    intermediate_pressure = (
        fan_curve.pressure_at_flow_rate(0.0025)
    )
 
    free_delivery_pressure = (
        fan_curve.pressure_at_flow_rate(0.01)
    )
 
    assert abs(shutoff_pressure - 120.0) < 1e-9
    assert abs(intermediate_pressure - 105.0) < 1e-9
    assert abs(free_delivery_pressure - 0.0) < 1e-9
 
    try:
        fan_curve.pressure_at_flow_rate(0.011)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Out-of-range airflow must raise ValueError."
        )
 
    print("=" * 70)
    print("ALL FAN CURVE CHECKS PASSED")
    print("=" * 70)
 
 
if __name__ == "__main__":
    main()