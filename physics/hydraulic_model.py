"""
hydraulic_model.py
 
Hydraulic calculations.
 
Responsible for:
 
- fin count
- hydraulic diameter
- Reynolds number
"""

def fin_count(
    base_width_mm,
    fin_thickness_mm,
    fin_spacing_mm
):

    return int(
        (base_width_mm + fin_spacing_mm)
        /
        (fin_thickness_mm + fin_spacing_mm)
    )


def hydraulic_diameter(
    spacing_mm,
    fin_height_mm
):

    s = spacing_mm / 1000
    h = fin_height_mm / 1000

    return (2 * s * h) / (s + h)


def reynolds_number(
    rho,
    velocity,
    hydraulic_diameter,
    mu
):

    return (
        rho
        * velocity
        * hydraulic_diameter
        / mu
    )
