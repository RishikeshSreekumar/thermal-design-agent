"""
process_capability.py
 
Manufacturing process capability models.
 
A process capability represents one valid combination of:
 
- Manufacturing process
- Material
- Geometric manufacturing limits
 
Limits are process–material-specific rather than universal.
"""
 
from dataclasses import dataclass
 
from models.material import Material
 
 
@dataclass(frozen=True)
class ProcessCapability:
    """
    Manufacturing capability for one material–process combination.
    """
 
    process_name: str
 
    material: Material
 
    minimum_fin_thickness: float
 
    minimum_fin_spacing: float
 
    maximum_fin_height_to_thickness_ratio: float
 
    maximum_fin_height_to_spacing_ratio: float
 
    minimum_base_thickness: float
 
    maximum_base_thickness: float
 
    # Used when the capability is approximate and
    # supplier confirmation may be required.
    source_description: str
 
    supplier_review_required: bool = False
 
    @property
    def capability_name(self) -> str:
        """
        Return a readable material–process combination.
        """
 
        return (
            f"{self.material.display_name} — "
            f"{self.process_name}"
        )