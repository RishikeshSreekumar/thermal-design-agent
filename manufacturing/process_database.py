"""
process_database.py
 
Database of supported material-manufacturing process
combinations for the Thermal AI Engineer.
 
Only combinations with sufficiently defined capability
data should be added here.
"""
 
from models.process_capability import ProcessCapability
 
from manufacturing.extrusion_capability import (
    AL6063_EXTRUSION,
)
 
 
PROCESS_CAPABILITY_DATABASE: dict[
    str,
    ProcessCapability,
] = {
    "al6063_t5_extrusion": AL6063_EXTRUSION,
}
 
 
def get_process_capability(
    capability_key: str,
) -> ProcessCapability:
    """
    Return one material-process capability.
 
    Parameters
    ----------
    capability_key:
        Database key such as 'al6063_t5_extrusion'.
 
    Raises
    ------
    KeyError
        If the requested capability does not exist.
    """
 
    normalized_key = capability_key.strip().lower()
 
    if normalized_key not in PROCESS_CAPABILITY_DATABASE:
        available = ", ".join(
            PROCESS_CAPABILITY_DATABASE.keys()
        )
 
        raise KeyError(
            f"Unknown process capability '{capability_key}'. "
            f"Available capabilities: {available}"
        )
 
    return PROCESS_CAPABILITY_DATABASE[
        normalized_key
    ]
 
 
def get_capabilities_for_material(
    material_grade: str,
) -> list[ProcessCapability]:
    """
    Return all manufacturing capabilities available
    for a specified material grade.
    """
 
    normalized_grade = (
        material_grade
        .strip()
        .lower()
        .replace("-", "")
        .replace("_", "")
    )
 
    matches: list[ProcessCapability] = []
 
    for capability in (
        PROCESS_CAPABILITY_DATABASE.values()
    ):
        capability_grade = (
            capability.material.grade
            .strip()
            .lower()
            .replace("-", "")
            .replace("_", "")
        )
 
        if capability_grade == normalized_grade:
            matches.append(capability)
 
    return matches