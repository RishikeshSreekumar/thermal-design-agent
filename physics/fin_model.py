"""
fin_model.py
 
Fin thermal calculations.
"""
import math

def total_surface_area(
    base_length_mm,
    base_width_mm,
    fin_height_mm,
    fin_thickness_mm,
    fin_count
):
    """
    Approximate total exposed area.
    """

    L = base_length_mm / 1000
    W = base_width_mm / 1000
    H = fin_height_mm / 1000
    T = fin_thickness_mm / 1000

    base_area = L * W

    fin_side_area = fin_count * 2 * H * L

    fin_tip_area = fin_count * T * L

    return (
        base_area
        + fin_side_area
        + fin_tip_area
    )


def fin_efficiency(
    h,
    fin_thickness_mm,
    fin_height_mm,
    conductivity=200
):
    """
    Straight rectangular fin.

    Default conductivity:
    Aluminium ≈200 W/m.K
    """

    t = fin_thickness_mm / 1000
    L = fin_height_mm / 1000

    m = math.sqrt(
        2 * h /
        (conductivity * t)
    )

    if m * L == 0:

        return 1.0

    return math.tanh(
        m * L
    ) / (m * L)
