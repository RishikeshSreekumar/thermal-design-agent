"""
Regression tests for fan-selection logic.
"""
 
from fan.fan_selection import select_fan
from fan.operating_point import SystemResistance
 
 
def test_feasible_fan_is_selected() -> None:
    """
    A fan meeting the required operating airflow
    should be selected.
    """
 
    system = SystemResistance(
        resistance_coefficient=10000.0
    )
 
    selection = select_fan(
        fan_names=["demo_120mm"],
        system=system,
        minimum_flow_rate=0.05,
    )
 
    assert selection.fan_name == "demo_120mm"
 
    assert (
        selection.operating_point.volumetric_flow_rate
        >= 0.05
    )
 
    assert selection.operating_point.pressure >= 0.0
    assert selection.excess_flow_rate >= 0.0
 
 
def test_inadequate_fan_is_rejected() -> None:
    """
    Selection should fail clearly when no fan meets
    the minimum required airflow.
    """
 
    system = SystemResistance(
        resistance_coefficient=10000.0
    )
 
    try:
        select_fan(
            fan_names=["demo_120mm"],
            system=system,
            minimum_flow_rate=0.09,
        )
 
    except ValueError as exc:
        assert (
            "No supplied fan can satisfy"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "An inadequate fan was incorrectly selected."
        )
 
 
def test_empty_fan_list_is_rejected() -> None:
    """
    At least one fan candidate must be supplied.
    """
 
    system = SystemResistance(
        resistance_coefficient=10000.0
    )
 
    try:
        select_fan(
            fan_names=[],
            system=system,
            minimum_flow_rate=0.01,
        )
 
    except ValueError as exc:
        assert (
            "At least one fan name"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Empty fan list did not raise ValueError."
        )
 
 
if __name__ == "__main__":
    test_feasible_fan_is_selected()
    test_inadequate_fan_is_rejected()
    test_empty_fan_list_is_rejected()
 
    print("ALL FAN SELECTION CHECKS PASSED")