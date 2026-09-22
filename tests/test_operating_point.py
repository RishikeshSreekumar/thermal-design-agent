from fan.fan_curve import FanCurve
from fan.fan_curve import FanCurvePoint
from fan.operating_point import (
    SystemResistance,
    solve_operating_point,
)
 
 
def main():
 
    fan = FanCurve(
        points=[
            FanCurvePoint(0.000, 120.0),
            FanCurvePoint(0.005, 60.0),
            FanCurvePoint(0.010, 0.0),
        ]
    )
 
    system = SystemResistance(
        resistance_coefficient=2_000_000
    )
 
    operating_point = solve_operating_point(
        fan,
        system,
    )
 
    print("=" * 70)
    print("OPERATING POINT")
    print("=" * 70)
    print(operating_point)
 
    assert (
        0.004
        < operating_point.volumetric_flow_rate
        < 0.006
    )
 
    assert (
        40
        < operating_point.pressure
        < 80
    )
 
    print("=" * 70)
    print("OPERATING POINT TEST PASSED")
    print("=" * 70)
 
 
if __name__ == "__main__":
    main()