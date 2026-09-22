"""
validator.py
 
Engineering requirement review and validation.
 
This module distinguishes between:
 
1. Missing information that requires clarification
2. Supplied information that is physically invalid
3. Optional information for which a documented assumption can be used
4. Complete requirements that are ready for engineering analysis
"""

import math

from models.clarification import (
    ClarificationQuestion,
    RequirementsReview,
)
from models.requirements import (
    EngineeringRequirements,
    NATURAL_CONVECTION_ORIENTATIONS,
    NaturalConvectionSpecification,
)
 
 
class RequirementsValidationError(ValueError):
    """
    Backward-compatible exception used when a caller requires
    immediate validation instead of the clarification workflow.
    """
 
 
def _normalize_component_type(
    value: str | None,
) -> str | None:
    """
    Normalize supported component-type descriptions.
    """
 
    if value is None:
        return None
 
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
 
    aliases = {
        "heat_sink": "heat_sink",
        "heatsink": "heat_sink",
        "plate_fin_heat_sink": "heat_sink",
        "plate_fin_heatsink": "heat_sink",
    }
 
    return aliases.get(normalized, normalized)
 
 
def _normalize_convection_mode(
    value: str | None,
) -> str | None:
    """
    Normalize natural- and forced-convection descriptions.
    """
 
    if value is None:
        return None
 
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
 
    natural_aliases = {
        "natural",
        "natural_convection",
        "passive",
        "passive_cooling",
        "free_convection",
    }
 
    forced_aliases = {
        "forced",
        "forced_convection",
        "active",
        "active_cooling",
        "fan",
        "fan_cooled",
        "airflow",
    }
 
    if normalized in natural_aliases:
        return "natural"
 
    if normalized in forced_aliases:
        return "forced"
 
    return normalized

def _normalize_natural_convection_orientation(
    value: str | None,
) -> str | None:
    """
    Normalize supported natural-convection orientation
    descriptions into the canonical plate-fin values.
    """
 
    if value is None:
        return None
 
    normalized = (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )
 
    vertical_aliases = {
        "vertical",
        "vertical_fins",
        "fins_vertical",
        "vertical_channels",
        "vertically_oriented",
    }
 
    horizontal_up_aliases = {
        "horizontal_fins_up",
        "horizontal_fins_upward",
        "horizontal_up",
        "horizontal_upward",
        "fins_up",
        "fins_upward",
        "upward_facing",
        "upward_facing_fins",
    }
 
    horizontal_down_aliases = {
        "horizontal_fins_down",
        "horizontal_fins_downward",
        "horizontal_down",
        "horizontal_downward",
        "fins_down",
        "fins_downward",
        "downward_facing",
        "downward_facing_fins",
    }

    horizontal_unspecified_aliases = {
        "horizontal",
        "horizontal_fins",
        "fins_horizontal",
        "horizontally_oriented",
    }
 
    if normalized in vertical_aliases:
        return "vertical"
 
    if normalized in horizontal_up_aliases:
        return "horizontal_fins_up"
 
    if normalized in horizontal_down_aliases:
        return "horizontal_fins_down"

    if normalized in horizontal_unspecified_aliases:
        return "horizontal"
 
    return normalized 
 
def review_requirements(
    engineering: EngineeringRequirements,
) -> RequirementsReview:
    """
    Review parsed engineering requirements.
 
    Missing critical values generate clarification questions.
    Invalid supplied values generate validation errors.
    Optional missing values generate documented assumptions.
    """
 
    review = RequirementsReview(
        engineering_requirements=engineering
    )
 
    requirements = engineering.requirements
    constraints = engineering.constraints
 
    if requirements is None:
        raise ValueError(
            "EngineeringRequirements.requirements is missing."
        )
 
    if constraints is None:
        raise ValueError(
            "EngineeringRequirements.constraints is missing."
        )
 
    # --------------------------------------------------
    # Component type
    # --------------------------------------------------
 
    component_type = _normalize_component_type(
        engineering.component_type
    )
 
    if component_type is None:
        component_type = "heat_sink"
 
        review.assumptions.append(
            "The requested component is assumed to be a heat sink."
        )
 
    if component_type != "heat_sink":
        review.validation_errors.append(
            "The current version supports only heat-sink design."
        )
 
    engineering.component_type = component_type
 
    # --------------------------------------------------
    # Convection mode
    # --------------------------------------------------
 
    convection_mode = _normalize_convection_mode(
        engineering.convection_mode
    )
 
    if convection_mode is None:
        review.clarification_questions.append(
            ClarificationQuestion(
                field_name="convection_mode",
                question=(
                    "Should the heat sink operate under natural "
                    "convection or forced convection?"
                ),
                reason=(
                    "Natural and forced convection require different "
                    "thermal correlations, geometry rules, and "
                    "optimization methods."
                ),
            )
        )
 
    elif convection_mode not in {
        "natural",
        "forced",
    }:
        review.validation_errors.append(
            "Convection mode must be either natural or forced."
        )
 
    engineering.convection_mode = convection_mode

    # --------------------------------------------------
    # Allowed materials
    # --------------------------------------------------
    material_names_are_valid = True
    if not isinstance(
        engineering.allowed_materials,
        tuple,
    ):
        review.validation_errors.append(
            "'allowed_materials' must be a tuple."
        )
        material_names_are_valid = False
    else:
        for material in (
            engineering.allowed_materials
        ):
            if not isinstance(
                material,
                str,
            ):
                review.validation_errors.append(
                    "Every allowed material must be a "
                    "string."
                )
                material_names_are_valid = False
                continue
            if not material.strip():
                review.validation_errors.append(
                    "Allowed material names must not be "
                    "empty."
                )
                material_names_are_valid = False
    if (
        material_names_are_valid
        and engineering.allowed_materials
    ):
        supported_material_aliases = {
            "6063",
            "6063t5",
            "al6063",
            "al6063t5",
            "aluminium6063",
            "aluminium6063t5",
            "aluminum6063",
            "aluminum6063t5",
        }
        normalized_allowed_materials = {
            "".join(
                character
                for character in material.lower()
                if character.isalnum()
            )
            for material
            in engineering.allowed_materials
        }
        if not (
            normalized_allowed_materials
            & supported_material_aliases
        ):
            review.validation_errors.append(
                "The current V2 optimizer supports "
                "Aluminium 6063-T5 only. The supplied "
                "allowed materials exclude the currently "
                "supported design material."
            )
 
    # --------------------------------------------------
    # Heat load
    # --------------------------------------------------
 
    if requirements.heat_load is None:
        review.clarification_questions.append(
            ClarificationQuestion(
                field_name="heat_load",
                question=(
                    "What heat load must the heat sink dissipate, "
                    "in watts?"
                ),
                reason=(
                    "Heat load is required to calculate thermal "
                    "resistance and operating temperature."
                ),
            )
        )
 
    elif requirements.heat_load <= 0:
        review.validation_errors.append(
            "Heat load must be greater than 0 W."
        )
 
    # --------------------------------------------------
    # Ambient temperature
    # --------------------------------------------------
 
    if requirements.ambient_temperature is None:
        requirements.ambient_temperature = 25.0
 
        review.assumptions.append(
            "Ambient temperature was not specified and is assumed "
            "to be 25 °C."
        )
 
    elif requirements.ambient_temperature < -50:
        review.validation_errors.append(
            "Ambient temperature is below the currently supported "
            "range of -50 °C."
        )
 
    elif requirements.ambient_temperature > 100:
        review.validation_errors.append(
            "Ambient temperature is above the currently supported "
            "range of 100 °C."
        )

    # --------------------------------------------------
    # Maximum allowable base temperature
    # --------------------------------------------------
    
    if (
        requirements.maximum_base_temperature
        is not None
    ):
        if (
            requirements.maximum_base_temperature
            <= -273.15
        ):
            review.validation_errors.append(
                "Maximum base temperature must be above "
                "absolute zero."
            )
    
        elif (
            requirements.ambient_temperature
            is not None
            and (
                requirements
                .maximum_base_temperature
                <= requirements.ambient_temperature
            )
        ):
            review.validation_errors.append(
                "Maximum base temperature must be greater "
                "than ambient temperature."
            )    

    # --------------------------------------------------
    # Airflow performance limits
    # --------------------------------------------------
    
    if (
        requirements.maximum_pressure_drop
        is not None
        and requirements.maximum_pressure_drop <= 0.0
    ):
        review.validation_errors.append(
            "Maximum pressure drop must be greater "
            "than 0 Pa."
        )
    
    if (
        requirements.maximum_pumping_power
        is not None
        and requirements.maximum_pumping_power <= 0.0
    ):
        review.validation_errors.append(
            "Maximum pumping power must be greater "
            "than 0 W."
        )        
 
    # --------------------------------------------------
    # Base dimensions
    # --------------------------------------------------
 
    if constraints.base_length is None:
        review.clarification_questions.append(
            ClarificationQuestion(
                field_name="base_length",
                question=(
                    "What base length is available for the heat sink, "
                    "in millimetres?"
                ),
                reason=(
                    "The available footprint defines the heat-transfer "
                    "area and geometric design space."
                ),
            )
        )
 
    elif constraints.base_length <= 0:
        review.validation_errors.append(
            "Base length must be greater than 0 mm."
        )
 
    if constraints.base_width is None:
        review.clarification_questions.append(
            ClarificationQuestion(
                field_name="base_width",
                question=(
                    "What base width is available for the heat sink, "
                    "in millimetres?"
                ),
                reason=(
                    "Base width is required to determine the number "
                    "of fins and available flow channels."
                ),
            )
        )
 
    elif constraints.base_width <= 0:
        review.validation_errors.append(
            "Base width must be greater than 0 mm."
        )
 
    # --------------------------------------------------
    # Maximum total height
    # --------------------------------------------------
 
    if constraints.max_height is None:
        review.clarification_questions.append(
            ClarificationQuestion(
                field_name="max_height",
                question=(
                    "What is the maximum permitted total heat-sink "
                    "height, including the base, in millimetres?"
                ),
                reason=(
                    "The total-height constraint limits both the base "
                    "thickness and fin height."
                ),
            )
        )
 
    elif constraints.max_height <= 0:
        review.validation_errors.append(
            "Maximum total height must be greater than 0 mm."
        )

    # --------------------------------------------------
    # Natural-convection configuration
    # --------------------------------------------------
 
    if convection_mode == "natural":
 
        natural_specification = (
            engineering.natural_convection
        )
 
        # Preserve the established V2 baseline whenever
        # orientation/radiation information is absent.
        if natural_specification is None:
            natural_specification = (
                NaturalConvectionSpecification(
                    orientation="vertical",
                    include_radiation=False,
                )
            )
 
            engineering.natural_convection = (
                natural_specification
            )
 
            review.assumptions.append(
                "Natural-convection orientation was not "
                "specified and is assumed to be vertical."
            )
 
        elif not isinstance(
            natural_specification,
            NaturalConvectionSpecification,
        ):
            review.validation_errors.append(
                "'natural_convection' must be a "
                "NaturalConvectionSpecification."
            )
 
            natural_specification = None
 
        if natural_specification is not None:
 
            # ------------------------------------------
            # Orientation
            # ------------------------------------------
 
            normalized_orientation = (
                _normalize_natural_convection_orientation(
                    natural_specification.orientation
                )
            )
 
            if normalized_orientation is None:
                normalized_orientation = "vertical"
 
                review.assumptions.append(
                    "Natural-convection orientation was "
                    "not specified and is assumed to be "
                    "vertical."
                )
 
            elif normalized_orientation == "horizontal":
                review.clarification_questions.append(
                    ClarificationQuestion(
                        field_name=(
                            "natural_convection_orientation"
                        ),
                        question=(
                            "For the horizontal heat sink, "
                            "should the fins face upward or "
                            "downward?"
                        ),
                        reason=(
                            "Upward- and downward-facing "
                            "horizontal plate-fin heat sinks "
                            "use different natural-convection "
                            "correlations."
                        ),
                    )
                )
 
            elif (
                normalized_orientation
                not in NATURAL_CONVECTION_ORIENTATIONS
            ):
                review.validation_errors.append(
                    "Natural-convection orientation must "
                    "be one of: vertical, "
                    "horizontal_fins_up, or "
                    "horizontal_fins_down."
                )
 
            natural_specification.orientation = (
                normalized_orientation
            )
 
            # ------------------------------------------
            # Radiation enable state
            # ------------------------------------------
 
            if not isinstance(
                natural_specification.include_radiation,
                bool,
            ):
                review.validation_errors.append(
                    "'include_radiation' must be a boolean."
                )
 
            elif natural_specification.include_radiation:
 
                emissivity = (
                    natural_specification
                    .surface_emissivity
                )
 
                surroundings_temperature = (
                    natural_specification
                    .surroundings_temperature
                )
 
                # --------------------------------------
                # Surface emissivity
                # --------------------------------------
 
                if emissivity is None:
                    review.clarification_questions.append(
                        ClarificationQuestion(
                            field_name=(
                                "surface_emissivity"
                            ),
                            question=(
                                "What surface emissivity "
                                "should be used for thermal "
                                "radiation?"
                            ),
                            reason=(
                                "Radiative heat transfer "
                                "depends directly on surface "
                                "emissivity."
                            ),
                        )
                    )
 
                elif (
                    not math.isfinite(emissivity)
                    or emissivity < 0.0
                    or emissivity > 1.0
                ):
                    review.validation_errors.append(
                        "Surface emissivity must be a "
                        "finite value between 0 and 1."
                    )
 
                # --------------------------------------
                # Surroundings temperature
                # --------------------------------------
 
                if surroundings_temperature is None:
                    natural_specification.surroundings_temperature = (
                        requirements.ambient_temperature
                    )
 
                    review.assumptions.append(
                        "Radiative surroundings temperature "
                        "was not specified and is assumed "
                        "equal to ambient air temperature."
                    )
 
                elif not math.isfinite(
                    surroundings_temperature
                ):
                    review.validation_errors.append(
                        "Surroundings temperature must be "
                        "finite."
                    )
 
                elif (
                    surroundings_temperature
                    <= -273.15
                ):
                    review.validation_errors.append(
                        "Surroundings temperature must be "
                        "above absolute zero."
                    )
 
                elif (
                    requirements.ambient_temperature
                    is not None
                    and not math.isclose(
                        surroundings_temperature,
                        requirements.ambient_temperature,
                        rel_tol=0.0,
                        abs_tol=1e-9,
                    )
                ):
                    review.validation_errors.append(
                        "The current radiation model requires "
                        "radiative surroundings temperature "
                        "to equal ambient air temperature."
                    )
    
    # --------------------------------------------------
    # Airflow requirements
    # --------------------------------------------------
 
    if convection_mode == "forced":
 
        if requirements.air_velocity is None:
            review.clarification_questions.append(
                ClarificationQuestion(
                    field_name="air_velocity",
                    question=(
                        "What inlet air velocity is available, "
                        "in metres per second?"
                    ),
                    reason=(
                        "Forced-convection heat transfer and pressure "
                        "drop depend on the available airflow."
                    ),
                )
            )
 
        elif requirements.air_velocity <= 0:
            review.validation_errors.append(
                "Air velocity must be greater than 0 m/s for "
                "forced convection."
            )
 
    elif convection_mode == "natural":
 
        if (
            requirements.air_velocity is not None
            and requirements.air_velocity < 0
        ):
            review.validation_errors.append(
                "Air velocity cannot be negative."
            )
 
        elif (
            requirements.air_velocity is not None
            and requirements.air_velocity > 0
        ):
            review.assumptions.append(
                "A positive air velocity was supplied with natural "
                "convection. The value will be ignored unless the "
                "cooling mode is changed to forced convection."
            )
 
    return review
 
 
def validate_requirements(
    engineering: EngineeringRequirements,
) -> EngineeringRequirements:
    """
    Backward-compatible strict validation function.
 
    This function raises an exception whenever clarification
    questions or validation errors exist.
    """
 
    review = review_requirements(engineering)
 
    messages: list[str] = []
 
    for question in review.clarification_questions:
        messages.append(
            f"Missing '{question.field_name}': {question.question}"
        )
 
    messages.extend(review.validation_errors)
 
    if messages:
        formatted_messages = "\n".join(
            f"- {message}" for message in messages
        )
 
        raise RequirementsValidationError(
            "Engineering requirements are not ready:\n"
            f"{formatted_messages}"
        )
 
    return review.engineering_requirements