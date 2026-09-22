"""
fluid_properties.py
 
Fluid property models.
 
Currently supports:
- Air
"""

# ------------------------------------------------------------------
# AIR PROPERTIES
# ------------------------------------------------------------------

def air_properties(temperature_c):
    """
    Air properties at ~30°C.
    Future:
        - Temperature interpolation
        - Property database
    """

    rho = 1.164          # kg/m³
    mu = 1.872e-5        # Pa.s
    k = 0.0263           # W/m.K
    cp = 1007            # J/kg.K
    pr = 0.71

    return rho, mu, k, cp, pr