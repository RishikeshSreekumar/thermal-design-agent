"""
resistance.py
 
Thermal resistance calculations.
"""

def thermal_resistance(
    h,
    area,
    fin_efficiency
):

    effective_area = area * fin_efficiency

    return 1 / (
        h
        * effective_area
    )