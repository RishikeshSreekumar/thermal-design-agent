"""
thermal_equations.py
 
Backward-compatible façade for the Thermal AI Engineer
Physics Engine.
 
The engineering equations have been separated into focused
modules inside the physics package.
 
Existing modules may continue importing:
 
    from core import thermal_equations as eq
 
New development should import directly from the appropriate
physics module.
 
This compatibility layer can be removed after all callers
have migrated to the new Physics Engine.
"""
 
# ----------------------------------------------------------
# Fluid Properties
# ----------------------------------------------------------
 
from physics.fluid_properties import air_properties
 
 
# ----------------------------------------------------------
# Flow Model
# ----------------------------------------------------------
 
from physics.flow_model import (
    blockage_ratio,
    channel_count,
    channel_velocity,
    gross_frontal_area,
    open_flow_area,
)
 
 
# ----------------------------------------------------------
# Hydraulic Model
# ----------------------------------------------------------
 
from physics.hydraulic_model import (
    fin_count,
    hydraulic_diameter,
    reynolds_number,
)
 
 
# ----------------------------------------------------------
# Convection
# ----------------------------------------------------------
 
from physics.convection import (
    heat_transfer_coefficient,
    nusselt_number,
)
 
 
# ----------------------------------------------------------
# Fin Model
# ----------------------------------------------------------
 
from physics.fin_model import (
    fin_efficiency,
    total_surface_area,
)
 
 
# ----------------------------------------------------------
# Thermal Resistance
# ----------------------------------------------------------
 
from physics.resistance import thermal_resistance
 
 
# ----------------------------------------------------------
# Public Compatibility Interface
# ----------------------------------------------------------
 
__all__ = [
    "air_properties",
    "fin_count",
    "channel_count",
    "gross_frontal_area",
    "open_flow_area",
    "channel_velocity",
    "blockage_ratio",
    "hydraulic_diameter",
    "reynolds_number",
    "nusselt_number",
    "heat_transfer_coefficient",
    "total_surface_area",
    "fin_efficiency",
    "thermal_resistance",
]