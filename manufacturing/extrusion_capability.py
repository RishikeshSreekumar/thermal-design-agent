"""
extrusion_capability.py
 
Initial aluminium-extrusion process capability.
 
These limits are conservative generic engineering assumptions.
They are not universal supplier guarantees.
 
Supplier confirmation is required before releasing a design
for manufacture.
"""
 
from materials.material_database import AL6063_T5
from models.process_capability import ProcessCapability
 
 
AL6063_EXTRUSION = ProcessCapability(
    process_name="Extrusion",
 
    material=AL6063_T5,
 
    # Reference-supported conservative boundary.
    minimum_fin_thickness=0.8,
 
    # Initial configurable engineering assumption.
    minimum_fin_spacing=1.6,
 
    # Fin height divided by fin thickness.
    maximum_fin_height_to_thickness_ratio=10.0,
 
    # Fin height divided by clear fin spacing.
    # Initial configurable engineering assumption.
    maximum_fin_height_to_spacing_ratio=5.0,
 
    # Initial configurable engineering assumptions.
    minimum_base_thickness=3.0,
    maximum_base_thickness=10.0,
 
    source_description=(
        "Initial generic aluminium-extrusion capability. "
        "Fin-thickness and height-to-thickness boundaries are "
        "based on published heat-sink extrusion guidance. "
        "Spacing and base-thickness limits are provisional "
        "engineering assumptions pending supplier validation."
    ),
 
    supplier_review_required=True,
)