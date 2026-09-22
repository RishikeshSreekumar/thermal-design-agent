"""
test_flow_geometry.py
 
Tests flow-area and channel-velocity calculations.
"""
 
import math
 
from core import thermal_equations as eq
 
 
def main() -> None:
    base_width = 50.0
    fin_height = 8.0
    fin_thickness = 0.8
    fin_spacing = 1.6
    approach_velocity = 5.0
 
    fins = eq.fin_count(
        base_width,
        fin_thickness,
        fin_spacing,
    )
 
    channels = eq.channel_count(
        fins
    )
 
    gross_area = eq.gross_frontal_area(
        base_width,
        fin_height,
    )
 
    open_area = eq.open_flow_area(
        fins,
        fin_spacing,
        fin_height,
    )
 
    velocity = eq.channel_velocity(
        approach_velocity,
        gross_area,
        open_area,
    )
 
    blockage = eq.blockage_ratio(
        gross_area,
        open_area,
    )
 
    hydraulic_diameter = eq.hydraulic_diameter(
        fin_spacing,
        fin_height,
    )
 
    print()
    print("=" * 60)
    print("FLOW GEOMETRY TEST")
    print("=" * 60)
 
    print("Fin count:", fins)
    print("Channel count:", channels)
    print("Gross frontal area:", gross_area, "m²")
    print("Open flow area:", open_area, "m²")
    print("Approach velocity:", approach_velocity, "m/s")
    print("Channel velocity:", velocity, "m/s")
    print("Blockage ratio:", blockage)
    print(
        "Hydraulic diameter:",
        hydraulic_diameter * 1000,
        "mm",
    )
 
    assert fins == 21
    assert channels == 20
 
    assert math.isclose(
        gross_area,
        0.0004,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        open_area,
        0.000256,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        velocity,
        7.8125,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        blockage,
        0.36,
        abs_tol=1e-12,
    )
 
    print()
    print("ALL FLOW GEOMETRY CHECKS PASSED")
 
 
if __name__ == "__main__":
    main()