"""
test_material_database.py
 
Verifies the Thermal AI Engineer material database.
"""
 
from materials.material_database import (
    MATERIAL_DATABASE,
    get_material,
)
 
 
def main() -> None:
    print("Available materials:")
 
    for key, material in MATERIAL_DATABASE.items():
        print(
            f"- {key}: "
            f"{material.display_name} | "
            f"k={material.thermal_conductivity} W/mK | "
            f"density={material.density} kg/m³"
        )
 
    print()
    selected = get_material("al6063_t5")
 
    print("Selected material:")
    print(selected)
 
 
if __name__ == "__main__":
    main()