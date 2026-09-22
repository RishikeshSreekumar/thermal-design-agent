"""
test_optimizer.py
 
Smoke test for the ThermalOptimizer.
"""
 
import logging
 
from core.thermal_optimizer import ThermalOptimizer
 
from models.requirements import (
    EngineeringRequirements,
    Requirements,
    Constraints,
)
 
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s",
)
 
 
requirements = EngineeringRequirements(
 
    component_type="heat_sink",
 
    convection_mode="forced",
 
    requirements=Requirements(
 
        heat_load=165,
 
        ambient_temperature=30,
 
        air_velocity=5,
 
    ),
 
    constraints=Constraints(
 
        base_length=50,
 
        base_width=50,
 
        max_height=30,
 
    ),
 
)
 
 
optimizer = ThermalOptimizer()
 
result = optimizer.optimize(requirements)
 
print()
print("=" * 60)
print("BEST DESIGN")
print("=" * 60)
print(result)