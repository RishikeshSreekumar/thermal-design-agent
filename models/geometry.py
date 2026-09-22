"""
geometry.py
 
Geometry model passed to the CAD generator.
"""
 
from dataclasses import dataclass
 
 
@dataclass
class GeometryParameters:
    """
    Complete heat-sink geometry used for CAD generation.
    """
 
    base_length: float
    base_width: float
    base_thickness: float
 
    fin_count: int
    fin_height: float
    fin_thickness: float
    fin_spacing: float
 
    material: str
 
    @property
    def total_height(self) -> float:
        """
        Return the complete heat-sink height.
 
        Total height includes the base and fins.
        """
 
        return self.base_thickness + self.fin_height