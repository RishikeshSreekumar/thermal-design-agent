"""
Regression tests for the plate-fin flow-network evaluator.
"""
 
from physics.flow_network import evaluate_flow_network
 
 
def test_flow_network_returns_valid_state() -> None:
    """
    A valid plate-fin geometry should produce a complete
    positive hydraulic state.
    """
 
    result = evaluate_flow_network(
        volumetric_flow_rate=0.010,
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    assert result.volumetric_flow_rate == 0.010
 
    assert result.approach_velocity > 0.0
    assert result.channel_velocity > 0.0
 
    assert result.gross_flow_area > 0.0
    assert result.open_flow_area > 0.0
 
    assert (
        result.open_flow_area
        <= result.gross_flow_area
    )
 
    assert (
        0.0
        <= result.blockage_ratio
        <= 1.0
    )
 
    assert result.hydraulic_diameter > 0.0
    assert result.reynolds_number > 0.0
    assert result.friction_factor > 0.0
    assert result.pressure_drop > 0.0
    assert result.pumping_power > 0.0
 
 
def test_flow_continuity_is_preserved() -> None:
    """
    Volumetric flow calculated using either gross-area
    approach velocity or open-area channel velocity should
    equal the specified flow rate.
    """
 
    specified_flow_rate = 0.010
 
    result = evaluate_flow_network(
        volumetric_flow_rate=specified_flow_rate,
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    approach_flow_rate = (
        result.approach_velocity
        * result.gross_flow_area
    )
 
    channel_flow_rate = (
        result.channel_velocity
        * result.open_flow_area
    )
 
    assert (
        abs(
            approach_flow_rate
            - specified_flow_rate
        )
        < 1e-12
    )
 
    assert (
        abs(
            channel_flow_rate
            - specified_flow_rate
        )
        < 1e-12
    )
 
 
def test_pumping_power_relationship() -> None:
    """
    Pumping power must equal pressure drop multiplied by
    volumetric flow rate.
    """
 
    result = evaluate_flow_network(
        volumetric_flow_rate=0.010,
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    expected_pumping_power = (
        result.pressure_drop
        * result.volumetric_flow_rate
    )
 
    assert (
        abs(
            result.pumping_power
            - expected_pumping_power
        )
        < 1e-12
    )
 
 
def test_pressure_drop_increases_with_flow_rate() -> None:
    """
    For the same geometry, increasing airflow should
    increase the calculated pressure drop.
    """
 
    low_flow_result = evaluate_flow_network(
        volumetric_flow_rate=0.005,
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    high_flow_result = evaluate_flow_network(
        volumetric_flow_rate=0.015,
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    assert (
        high_flow_result.channel_velocity
        > low_flow_result.channel_velocity
    )
 
    assert (
        high_flow_result.reynolds_number
        > low_flow_result.reynolds_number
    )
 
    assert (
        high_flow_result.pressure_drop
        > low_flow_result.pressure_drop
    )
 
 
def test_zero_flow_rate_is_rejected() -> None:
    """
    A zero volumetric flow rate is outside the forced-flow
    evaluator's valid operating domain.
    """
 
    try:
        evaluate_flow_network(
            volumetric_flow_rate=0.0,
            base_width_mm=100.0,
            fin_height_mm=30.0,
            fin_count_value=20,
            fin_spacing_mm=4.0,
            channel_length_mm=100.0,
            air_temperature_c=30.0,
        )
 
    except ValueError as exc:
        assert (
            "Volumetric flow rate"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Zero volumetric flow rate was not rejected."
        )
 
 
def test_impossible_open_area_is_rejected() -> None:
    """
    A fin arrangement whose calculated open area exceeds
    its gross frontal area is geometrically inconsistent.
    """
 
    try:
        evaluate_flow_network(
            volumetric_flow_rate=0.010,
            base_width_mm=50.0,
            fin_height_mm=30.0,
            fin_count_value=20,
            fin_spacing_mm=4.0,
            channel_length_mm=100.0,
            air_temperature_c=30.0,
        )
 
    except ValueError as exc:
        assert (
            "Open flow area cannot exceed"
            in str(exc)
        )
 
    else:
        raise AssertionError(
            "Impossible open flow area was not rejected."
        )
 
def test_pressure_drop_callback() -> None:
    """
    The generated pressure-drop callback should return
    exactly the same pressure drop as a direct flow-network
    evaluation.
    """
 
    from physics.flow_network import (
        create_pressure_drop_function,
    )
 
    callback = create_pressure_drop_function(
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    direct_result = evaluate_flow_network(
        volumetric_flow_rate=0.010,
        base_width_mm=100.0,
        fin_height_mm=30.0,
        fin_count_value=20,
        fin_spacing_mm=4.0,
        channel_length_mm=100.0,
        air_temperature_c=30.0,
    )
 
    callback_result = callback(0.010)
 
    assert (
        abs(
            callback_result
            - direct_result.pressure_drop
        )
        < 1e-12
    )

if __name__ == "__main__":
    test_flow_network_returns_valid_state()
    test_flow_continuity_is_preserved()
    test_pumping_power_relationship()
    test_pressure_drop_increases_with_flow_rate()
    test_zero_flow_rate_is_rejected()
    test_impossible_open_area_is_rejected()
    test_pressure_drop_callback()
 
    print("ALL FLOW NETWORK CHECKS PASSED")
 