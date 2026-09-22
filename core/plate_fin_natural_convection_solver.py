"""
plate_fin_natural_convection_solver.py
 
Iterative natural-convection thermal solver for the
current plate-fin heat-sink topology.
 
The reusable natural-convection correlation and buoyancy
physics remain inside NaturalConvectionSolver.
 
This layer supplies plate-fin geometry interpretation and
iterates surface temperature until the convection and
thermal states are mutually consistent.
"""
import math
 
from core.natural_convection_solver import (
    NaturalConvectionSolver,
)
from core.thermal_solver import ThermalSolver
 
from models.convection_state import ConvectionState
from models.design_candidate import DesignCandidate
from models.requirements import (
    EngineeringRequirements,
    NATURAL_CONVECTION_ORIENTATIONS,
)
from models.thermal_state import ThermalState
 
from physics.fluid_properties import air_properties
from physics.natural_convection import (
    film_temperature_c,
    grashof_number,
    heat_transfer_coefficient,
    kinematic_viscosity,
    rayleigh_number,
    volumetric_thermal_expansion_coefficient,
)
from physics.plate_fin_natural_convection import (
    tari_mehrtash_horizontal_downward_nusselt,
    tari_mehrtash_horizontal_upward_nusselt,
    upward_horizontal_modified_grashof,
)
from physics.radiation import (
    radiative_heat_transfer_coefficient,
)
 
 
class PlateFinNaturalConvectionSolver:
    """
    Solve plate-fin thermal performance under natural
    convection.
    """
 
    @staticmethod
    def solve(
        *,
        candidate: DesignCandidate,
        requirements: EngineeringRequirements,
        material_conductivity: float,
        initial_temperature_rise: float = 30.0,
        temperature_tolerance: float = 0.01,
        maximum_iterations: int = 100,
        relaxation_factor: float = 0.5,
    ) -> ThermalState:
        """
        Iteratively resolve orientation-aware natural
        convection and heat-sink temperature.
 
        Vertical orientation preserves the established
        Churchill-Chu V2 calculation using fin height as
        characteristic length.
 
        Horizontal plate-fin orientations use dedicated
        Tari-Mehrtash correlations based on fin spacing.
        """
 
        PlateFinNaturalConvectionSolver._validate_inputs(
            candidate=candidate,
            requirements=requirements,
            material_conductivity=(
                material_conductivity
            ),
            initial_temperature_rise=(
                initial_temperature_rise
            ),
            temperature_tolerance=(
                temperature_tolerance
            ),
            maximum_iterations=(
                maximum_iterations
            ),
            relaxation_factor=relaxation_factor,
        )
 
        ambient_temperature = (
            requirements
            .requirements
            .ambient_temperature
        )
 
        surface_temperature = (
            ambient_temperature
            + initial_temperature_rise
        )
 
        orientation = (
            PlateFinNaturalConvectionSolver
            ._resolve_orientation(
                requirements
            )
        )
 
 
        for _ in range(maximum_iterations):
 
            convection_state = (
                PlateFinNaturalConvectionSolver
                ._resolve_convection_state(
                    candidate=candidate,
                    requirements=requirements,
                    orientation=orientation,
                    surface_temperature_c=(
                        surface_temperature
                    ),
                    ambient_temperature_c=(
                        ambient_temperature
                    ),
                )
            )

            radiation_heat_transfer_coefficient = (
                PlateFinNaturalConvectionSolver
                ._resolve_radiation_heat_transfer_coefficient(
                    requirements=requirements,
                    surface_temperature_c=(
                        surface_temperature
                    ),
                    ambient_temperature_c=(
                        ambient_temperature
                    ),
                )
            )
 
            thermal_state = (
                ThermalSolver
                .solve_from_convection_state(
                    candidate=candidate,
                    convection_state=(
                        convection_state
                    ),
                    requirements=requirements,
                    material_conductivity=(
                        material_conductivity
                    ),
                    radiative_heat_transfer_coefficient=(
                        radiation_heat_transfer_coefficient
                    ),
                )
            )
 
            calculated_temperature = (
                thermal_state
                .estimated_base_temperature
            )
 
            temperature_error = abs(
                calculated_temperature
                - surface_temperature
            )
 
            latest_thermal_state = thermal_state
 
            if (
                temperature_error
                <= temperature_tolerance
            ):
                return thermal_state
 
            surface_temperature = (
                surface_temperature
                + relaxation_factor
                * (
                    calculated_temperature
                    - surface_temperature
                )
            )
 
        raise ValueError(
            "Plate-fin natural-convection solver did not "
            f"converge within {maximum_iterations} "
            "iterations."
        )

    @staticmethod
    def _resolve_orientation(
        requirements: EngineeringRequirements,
    ) -> str:
        """
        Resolve natural-convection orientation while
        preserving the established vertical legacy
        behaviour for callers that do not yet carry the
        new configuration object.
        """
 
        specification = (
            requirements.natural_convection
        )
 
        if specification is None:
            return "vertical"
 
        orientation = specification.orientation
 
        if orientation is None:
            return "vertical"
 
        if (
            orientation
            not in NATURAL_CONVECTION_ORIENTATIONS
        ):
            raise ValueError(
                "Unsupported natural-convection "
                f"orientation: '{orientation}'."
            )
 
        return orientation
 
 
    @staticmethod
    def _resolve_convection_state(
        *,
        candidate: DesignCandidate,
        requirements: EngineeringRequirements,
        orientation: str,
        surface_temperature_c: float,
        ambient_temperature_c: float,
    ) -> ConvectionState:
        """
        Resolve the convection correlation appropriate to
        the configured plate-fin orientation.
        """
 
        # --------------------------------------------------
        # Existing vertical V2 path
        # --------------------------------------------------
 
        if orientation == "vertical":
 
            characteristic_length = (
                candidate.fin_height
                / 1000.0
            )
 
            return NaturalConvectionSolver.solve(
                surface_temperature_c=(
                    surface_temperature_c
                ),
                ambient_temperature_c=(
                    ambient_temperature_c
                ),
                characteristic_length=(
                    characteristic_length
                ),
            )
 
        # --------------------------------------------------
        # Horizontal plate-fin paths
        # --------------------------------------------------
 
        fin_spacing = (
            candidate.fin_spacing
            / 1000.0
        )
 
        fin_height = (
            candidate.fin_height
            / 1000.0
        )
 
        heat_sink_length = (
            requirements
            .constraints
            .base_length
            / 1000.0
        )
 
        temperature_difference = (
            surface_temperature_c
            - ambient_temperature_c
        )
 
        film_temperature = film_temperature_c(
            surface_temperature_c,
            ambient_temperature_c,
        )
 
        rho, mu, air_k, _, pr = air_properties(
            film_temperature
        )
 
        beta = (
            volumetric_thermal_expansion_coefficient(
                film_temperature
            )
        )
 
        nu = kinematic_viscosity(
            density=rho,
            dynamic_viscosity=mu,
        )
 
        grashof_spacing = grashof_number(
            beta=beta,
            temperature_difference=(
                temperature_difference
            ),
            characteristic_length=fin_spacing,
            kinematic_viscosity_value=nu,
        )
 
        rayleigh_spacing = rayleigh_number(
            grashof_number_value=(
                grashof_spacing
            ),
            prandtl_number=pr,
        )
 
        # --------------------------------------------------
        # Horizontal — fins upward
        # --------------------------------------------------
 
        if orientation == "horizontal_fins_up":
 
            modified_grashof = (
                upward_horizontal_modified_grashof(
                    grashof_based_on_spacing=(
                        grashof_spacing
                    ),
                    fin_spacing=fin_spacing,
                    fin_height=fin_height,
                    heat_sink_length=(
                        heat_sink_length
                    ),
                )
            )
 
            nusselt = (
                tari_mehrtash_horizontal_upward_nusselt(
                    modified_grashof_number=(
                        modified_grashof
                    ),
                    prandtl_number=pr,
                )
            )
 
            correlation_name = (
                "tari_mehrtash_horizontal_"
                "upward_plate_fin"
            )
 
        # --------------------------------------------------
        # Horizontal — fins downward
        # --------------------------------------------------
 
        elif (
            orientation
            == "horizontal_fins_down"
        ):
 
            nusselt = (
                tari_mehrtash_horizontal_downward_nusselt(
                    rayleigh_number_based_on_spacing=(
                        rayleigh_spacing
                    ),
                )
            )
 
            correlation_name = (
                "tari_mehrtash_horizontal_"
                "downward_plate_fin"
            )
 
        else:
            raise ValueError(
                "Unsupported natural-convection "
                f"orientation: '{orientation}'."
            )
 
        h = heat_transfer_coefficient(
            nusselt_number=nusselt,
            thermal_conductivity=air_k,
            characteristic_length=fin_spacing,
        )
 
        return ConvectionState(
            mode="natural",
            nusselt_number=nusselt,
            heat_transfer_coefficient=h,
            characteristic_length=fin_spacing,
            correlation_name=correlation_name,
            rayleigh_number=rayleigh_spacing,
            grashof_number=grashof_spacing,
            prandtl_number=pr,
        )

    @staticmethod
    def _resolve_radiation_heat_transfer_coefficient(
        *,
        requirements: EngineeringRequirements,
        surface_temperature_c: float,
        ambient_temperature_c: float,
    ) -> float:
        """
        Resolve the linearized radiative heat-transfer
        coefficient for the current natural-convection
        iteration.
 
        The current reduced-order model permits radiation
        only to surroundings at the same temperature as
        the ambient air.
        """
 
        specification = (
            requirements.natural_convection
        )
 
        if specification is None:
            return 0.0
 
        if not specification.include_radiation:
            return 0.0
 
        emissivity = (
            specification.surface_emissivity
        )
 
        if emissivity is None:
            raise ValueError(
                "Surface emissivity is required when "
                "thermal radiation is enabled."
            )
 
        surroundings_temperature = (
            specification
            .surroundings_temperature
        )
 
        if surroundings_temperature is None:
            surroundings_temperature = (
                ambient_temperature_c
            )
 
        return (
            radiative_heat_transfer_coefficient(
                surface_temperature_c=(
                    surface_temperature_c
                ),
                surroundings_temperature_c=(
                    surroundings_temperature
                ),
                emissivity=emissivity,
            )
        )
 
    @staticmethod
    def _validate_inputs(
        *,
        candidate: DesignCandidate,
        requirements: EngineeringRequirements,
        material_conductivity: float,
        initial_temperature_rise: float,
        temperature_tolerance: float,
        maximum_iterations: int,
        relaxation_factor: float,
    ) -> None:
 
        if not isinstance(
            candidate,
            DesignCandidate,
        ):
            raise ValueError(
                "'candidate' must be a DesignCandidate."
            )
 
        if not isinstance(
            requirements,
            EngineeringRequirements,
        ):
            raise ValueError(
                "'requirements' must be an "
                "EngineeringRequirements object."
            )
 
        if (
            requirements.convection_mode
            != "natural"
        ):
            raise ValueError(
                "PlateFinNaturalConvectionSolver requires "
                "convection_mode='natural'."
            )

        natural_specification = (
            requirements.natural_convection
        )

        if (
            natural_specification is not None
            and natural_specification.include_radiation
        ):
            emissivity = (
                natural_specification
                .surface_emissivity
            )
 
            if emissivity is None:
                raise ValueError(
                    "Surface emissivity is required when "
                    "thermal radiation is enabled."
                )
 
            if (
                not math.isfinite(emissivity)
                or emissivity < 0.0
                or emissivity > 1.0
            ):
                raise ValueError(
                    "Surface emissivity must be a finite "
                    "value between 0 and 1."
                )
 
            surroundings_temperature = (
                natural_specification
                .surroundings_temperature
            )
 
            if surroundings_temperature is not None:
 
                if not math.isfinite(
                    surroundings_temperature
                ):
                    raise ValueError(
                        "Radiative surroundings "
                        "temperature must be finite."
                    )
 
                if (
                    surroundings_temperature
                    <= -273.15
                ):
                    raise ValueError(
                        "Radiative surroundings "
                        "temperature must be above "
                        "absolute zero."
                    )
 
                if not math.isclose(
                    surroundings_temperature,
                    requirements
                    .requirements
                    .ambient_temperature,
                    rel_tol=0.0,
                    abs_tol=1e-9,
                ):
                    raise ValueError(
                        "The current radiation model "
                        "requires radiative surroundings "
                        "temperature to equal ambient air "
                        "temperature."
                    )
 
        if (
            natural_specification is not None
            and natural_specification.orientation
            is not None
            and natural_specification.orientation
            not in NATURAL_CONVECTION_ORIENTATIONS
        ):
            raise ValueError(
                "Unsupported natural-convection "
                "orientation."
            )
 
        if (
            requirements
            .requirements
            .ambient_temperature
            is None
        ):
            raise ValueError(
                "Ambient temperature is required."
            )
 
        if (
            requirements
            .requirements
            .heat_load
            is None
            or requirements
            .requirements
            .heat_load
            <= 0
        ):
            raise ValueError(
                "Heat load must be greater than zero."
            )

        if (
            requirements.constraints.base_length
            is None
            or requirements.constraints.base_length
            <= 0
        ):
            raise ValueError(
                "Base length must be greater than zero."
            )
 
        if candidate.fin_spacing <= 0:
            raise ValueError(
                "Fin spacing must be greater than zero."
            )
 
        if candidate.fin_height <= 0:
            raise ValueError(
                "Fin height must be greater than zero."
            )
 
        if material_conductivity <= 0:
            raise ValueError(
                "Material thermal conductivity must be "
                "greater than zero."
            )
 
        if initial_temperature_rise <= 0:
            raise ValueError(
                "Initial temperature rise must be greater "
                "than zero."
            )
 
        if temperature_tolerance <= 0:
            raise ValueError(
                "Temperature tolerance must be greater "
                "than zero."
            )
 
        if maximum_iterations < 1:
            raise ValueError(
                "Maximum iterations must be at least 1."
            )
 
        if not (
            0.0
            < relaxation_factor
            <= 1.0
        ):
            raise ValueError(
                "Relaxation factor must be greater than "
                "0 and no greater than 1."
            )