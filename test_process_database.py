"""
test_process_database.py
 
Verifies the material-process capability database.
"""
 
from manufacturing.process_database import (
    PROCESS_CAPABILITY_DATABASE,
    get_capabilities_for_material,
    get_process_capability,
)
 
 
def main() -> None:
    print("Available process capabilities:")
 
    for key, capability in (
        PROCESS_CAPABILITY_DATABASE.items()
    ):
        print()
        print(f"Key: {key}")
        print(
            "Combination:",
            capability.capability_name,
        )
        print(
            "Minimum fin thickness:",
            capability.minimum_fin_thickness,
            "mm",
        )
        print(
            "Minimum fin spacing:",
            capability.minimum_fin_spacing,
            "mm",
        )
        print(
            "Maximum height/thickness ratio:",
            capability
            .maximum_fin_height_to_thickness_ratio,
        )
        print(
            "Supplier review required:",
            capability.supplier_review_required,
        )
 
    selected = get_process_capability(
        "al6063_t5_extrusion"
    )
 
    print()
    print("Selected capability:")
    print(selected)
 
    aluminium_capabilities = (
        get_capabilities_for_material(
            "6063-T5"
        )
    )
 
    print()
    print(
        "Capabilities available for 6063-T5:",
        len(aluminium_capabilities),
    )
 
 
if __name__ == "__main__":
    main()