"""
Regression checks for deterministic plate-fin heat-sink
solid-volume calculations.
"""
 
import math
 
from physics.solid_geometry import (
    plate_fin_heat_sink_volume,
)
 
 
def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-15,
) -> None:
    """
    Assert that two floating-point values are sufficiently
    close.
    """
 
    if not math.isclose(
        actual,
        expected,
        rel_tol=0.0,
        abs_tol=tolerance,
    ):
        raise AssertionError(
            f"Expected {expected}, received {actual}."
        )
 
 
def assert_invalid(
    expected_message: str,
    **geometry,
) -> None:
    """
    Verify that invalid geometry is rejected with an
    informative error.
    """
 
    try:
        plate_fin_heat_sink_volume(
            **geometry
        )
 
    except ValueError as exc:
        assert expected_message in str(exc)
 
    else:
        raise AssertionError(
            "Invalid plate-fin geometry was accepted."
        )
 
 
def main() -> None:
    # --------------------------------------------------
    # Reference case based on the current optimizer's
    # established plate-fin geometry.
    # --------------------------------------------------
 
    volume = plate_fin_heat_sink_volume(
        base_length_mm=50.0,
        base_width_mm=50.0,
        base_thickness_mm=3.0,
        fin_height_mm=8.0,
        fin_thickness_mm=0.8,
        fin_count=21,
    )
 
    expected_base_volume_mm3 = (
        50.0
        * 50.0
        * 3.0
    )
 
    expected_fin_volume_mm3 = (
        21
        * 50.0
        * 0.8
        * 8.0
    )
 
    expected_total_volume_mm3 = (
        expected_base_volume_mm3
        + expected_fin_volume_mm3
    )
 
    expected_volume_m3 = (
        expected_total_volume_mm3
        * 1e-9
    )
 
    assert_close(
        volume,
        expected_volume_m3,
    )
 
    assert_close(
        volume,
        1.422e-5,
    )
 
    # --------------------------------------------------
    # Base and fin contributions remain additive.
    # --------------------------------------------------
 
    single_fin_volume = (
        plate_fin_heat_sink_volume(
            base_length_mm=100.0,
            base_width_mm=40.0,
            base_thickness_mm=4.0,
            fin_height_mm=20.0,
            fin_thickness_mm=1.0,
            fin_count=1,
        )
    )
 
    expected_single_fin_volume = (
        (
            100.0
            * 40.0
            * 4.0
        )
        + (
            100.0
            * 1.0
            * 20.0
        )
    ) * 1e-9
 
    assert_close(
        single_fin_volume,
        expected_single_fin_volume,
    )
 
    # --------------------------------------------------
    # Increasing fin count increases volume by exactly
    # one additional fin volume per added fin.
    # --------------------------------------------------
 
    ten_fin_volume = (
        plate_fin_heat_sink_volume(
            base_length_mm=50.0,
            base_width_mm=50.0,
            base_thickness_mm=3.0,
            fin_height_mm=8.0,
            fin_thickness_mm=0.8,
            fin_count=10,
        )
    )
 
    eleven_fin_volume = (
        plate_fin_heat_sink_volume(
            base_length_mm=50.0,
            base_width_mm=50.0,
            base_thickness_mm=3.0,
            fin_height_mm=8.0,
            fin_thickness_mm=0.8,
            fin_count=11,
        )
    )
 
    one_fin_volume_m3 = (
        50.0
        * 0.8
        * 8.0
        * 1e-9
    )
 
    assert_close(
        (
            eleven_fin_volume
            - ten_fin_volume
        ),
        one_fin_volume_m3,
    )
 
    # --------------------------------------------------
    # Invalid dimensions
    # --------------------------------------------------
 
    valid_geometry = {
        "base_length_mm": 50.0,
        "base_width_mm": 50.0,
        "base_thickness_mm": 3.0,
        "fin_height_mm": 8.0,
        "fin_thickness_mm": 0.8,
        "fin_count": 21,
    }
 
    assert_invalid(
        "'base_length_mm' must be greater",
        **{
            **valid_geometry,
            "base_length_mm": 0.0,
        },
    )
 
    assert_invalid(
        "'base_width_mm' must be greater",
        **{
            **valid_geometry,
            "base_width_mm": -1.0,
        },
    )
 
    assert_invalid(
        "'base_thickness_mm' must be greater",
        **{
            **valid_geometry,
            "base_thickness_mm": 0.0,
        },
    )
 
    assert_invalid(
        "'fin_height_mm' must be greater",
        **{
            **valid_geometry,
            "fin_height_mm": 0.0,
        },
    )
 
    assert_invalid(
        "'fin_thickness_mm' must be greater",
        **{
            **valid_geometry,
            "fin_thickness_mm": -0.8,
        },
    )
 
    # --------------------------------------------------
    # Invalid fin count
    # --------------------------------------------------
 
    assert_invalid(
        "'fin_count' must be at least 1",
        **{
            **valid_geometry,
            "fin_count": 0,
        },
    )
 
    assert_invalid(
        "'fin_count' must be an integer",
        **{
            **valid_geometry,
            "fin_count": 21.5,
        },
    )
 
    assert_invalid(
        "'fin_count' must be an integer",
        **{
            **valid_geometry,
            "fin_count": True,
        },
    )
 
    print(
        "ALL SOLID GEOMETRY CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()