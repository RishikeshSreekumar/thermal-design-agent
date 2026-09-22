"""
fan_database.py
 
Small fan database used by the thermal optimizer.
 
Initially this contains only a few demonstration fans.
Additional manufacturer data can be added over time.
"""
 
from fan.fan_curve import (
    FanCurve,
    FanCurvePoint,
)
 
# --------------------------------------------------
# Demo Fan Database
# --------------------------------------------------
 
_FAN_DATABASE = {
 
    "demo_120mm": FanCurve(
        points=[
            FanCurvePoint(0.00, 120.0),
            FanCurvePoint(0.02, 108.0),
            FanCurvePoint(0.04, 90.0),
            FanCurvePoint(0.06, 68.0),
            FanCurvePoint(0.08, 42.0),
            FanCurvePoint(0.10, 0.0),
        ]
    ),
 
}
 
 
def get_fan_curve(
    fan_name: str,
) -> FanCurve:
    """
    Return the fan curve corresponding to the
    supplied fan name.
    """
 
    try:
        return _FAN_DATABASE[fan_name]
 
    except KeyError as exc:
 
        raise ValueError(
            f"Unknown fan '{fan_name}'."
        ) from exc