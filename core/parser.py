"""
parser.py
 
Converts raw LLM output into structured engineering models.
 
Missing values are preserved as None so that the clarification
workflow can identify which engineering inputs must be requested
from the user.
"""
 
from typing import Any
 
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    NaturalConvectionSpecification,
    Requirements,
)
 
 
def _optional_float(value: Any) -> float | None:
    """
    Convert a supplied value to float.
 
    Missing, empty, invalid, or zero placeholder values are
    represented as None.
    """
 
    if value is None:
        return None
 
    if isinstance(value, str):
        value = value.strip()
 
        if not value:
            return None
 
        if value.lower() in {
            "none",
            "null",
            "unknown",
            "not specified",
            "not provided",
        }:
            return None
 
    try:
        numeric_value = float(value)
 
    except (TypeError, ValueError):
        return None
 
    if numeric_value == 0:
        return None
 
    return numeric_value
 
 
def _optional_string(value: Any) -> str | None:
    """
    Convert a supplied value to a normalized optional string.
    """
 
    if value is None:
        return None
 
    text = str(value).strip()
 
    if not text:
        return None
 
    if text.lower() in {
        "none",
        "null",
        "unknown",
        "not specified",
        "not provided",
    }:
        return None
 
    return text

def _optional_float_preserve_zero(
    value: Any,
) -> float | None:
    """
    Convert an optional numerical value to float while
    preserving zero as a valid supplied value.
 
    This is required for values such as surroundings
    temperature, where 0 °C is physically valid.
    """
 
    if value is None:
        return None
 
    if isinstance(value, str):
        value = value.strip()
 
        if not value:
            return None
 
        if value.lower() in {
            "none",
            "null",
            "unknown",
            "not specified",
            "not provided",
        }:
            return None
 
    try:
        return float(value)
 
    except (TypeError, ValueError):
        return None
 
 
def _optional_bool(
    value: Any,
    default: bool = False,
) -> bool:
    """
    Convert common boolean representations into bool.
 
    Missing or unrecognized values use the supplied
    deterministic default.
    """
 
    if value is None:
        return default
 
    if isinstance(value, bool):
        return value
 
    if isinstance(value, str):
        normalized = value.strip().lower()
 
        if normalized in {
            "true",
            "yes",
            "1",
            "on",
        }:
            return True
 
        if normalized in {
            "false",
            "no",
            "0",
            "off",
        }:
            return False
 
    if isinstance(value, (int, float)):
        if value == 1:
            return True
 
        if value == 0:
            return False
 
    return default

def _optional_string_tuple(
    value: Any,
) -> tuple[
    str,
    ...,
]:
    """
    Convert a supplied material collection into a
    normalized tuple of non-empty strings.
    """
 
    if value is None:
        return ()
 
    if isinstance(
        value,
        str,
    ):
        raw_values = (
            item.strip()
            for item in value.split(",")
        )
 
    elif isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        raw_values = (
            str(item).strip()
            for item in value
        )
 
    else:
        return ()
 
    normalized_values: list[
        str
    ] = []
 
    for item in raw_values:
        if not item:
            continue
 
        if item.lower() in {
            "none",
            "null",
            "unknown",
            "not specified",
            "not provided",
        }:
            continue
 
        if item not in normalized_values:
            normalized_values.append(
                item
            )
 
    return tuple(
        normalized_values
    ) 
 
def parse_requirements(
    data: dict[str, Any],
) -> EngineeringRequirements:
    """
    Convert an LLM requirements dictionary into an
    EngineeringRequirements object.
 
    This function performs structural parsing only.
    Clarification and engineering validation are handled
    separately.
    """
 
    requirements_data = data.get("requirements") or {}
    constraints_data = data.get("constraints") or {}
 
    natural_convection_data = data.get(
        "natural_convection"
    )
 
    if isinstance(
        natural_convection_data,
        dict,
    ):
        natural_convection = (
            NaturalConvectionSpecification(
                orientation=_optional_string(
                    natural_convection_data.get(
                        "orientation"
                    )
                ),
                include_radiation=_optional_bool(
                    natural_convection_data.get(
                        "include_radiation"
                    ),
                    default=False,
                ),
                surface_emissivity=(
                    _optional_float_preserve_zero(
                        natural_convection_data.get(
                            "surface_emissivity"
                        )
                    )
                ),
                surroundings_temperature=(
                    _optional_float_preserve_zero(
                        natural_convection_data.get(
                            "surroundings_temperature"
                        )
                    )
                ),
            )
        )
 
    else:
        natural_convection = None
 
    return EngineeringRequirements(
        component_type=_optional_string(
            data.get("component_type")
        ),
 
        convection_mode=_optional_string(
            data.get("convection_mode")
        ),
        
        allowed_materials=(
            _optional_string_tuple(
                data.get("allowed_materials")
            )
        ),
        
        requirements=Requirements(
            heat_load=_optional_float(
                requirements_data.get("heat_load")
            ),
        
            ambient_temperature=_optional_float(
                requirements_data.get(
                    "ambient_temperature"
                )
            ),
        
            maximum_base_temperature=(
                _optional_float(
                    requirements_data.get(
                        "maximum_base_temperature"
                    )
                )
            ),
            
            maximum_pressure_drop=(
                _optional_float(
                    requirements_data.get(
                        "maximum_pressure_drop"
                    )
                )
            ),
            
            maximum_pumping_power=(
                _optional_float(
                    requirements_data.get(
                        "maximum_pumping_power"
                    )
                )
            ),
            
            air_velocity=_optional_float(
                requirements_data.get("air_velocity")
            ),
        ),
 
        constraints=Constraints(
            base_length=_optional_float(
                constraints_data.get("base_length")
            ),
 
            base_width=_optional_float(
                constraints_data.get("base_width")
            ),
 
            max_height=_optional_float(
                constraints_data.get("max_height")
            ),
        ),
        natural_convection=(
            natural_convection
        ),
    )