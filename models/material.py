"""
material.py
 
Thermal and physical material-property model.
 
Material properties are kept separate from manufacturing
process capabilities because the same material may be used
with multiple manufacturing processes.
"""
 
from dataclasses import dataclass
 
 
@dataclass(frozen=True)
class Material:
    """
    Material properties used by the thermal and mechanical models.
    """
 
    name: str
    grade: str
 
    thermal_conductivity: float
    density: float
 
    # Future properties:
    # specific_heat
    # elastic_modulus
    # yield_strength
    # cost_factor
    # corrosion_rating
 
    @property
    def display_name(self) -> str:
        """
        Return a readable material name.
        """
 
        return f"{self.name} {self.grade}"