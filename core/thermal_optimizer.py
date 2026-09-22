"""
thermal_optimizer.py
 
Thermal design-space exploration engine.
 
The optimizer evaluates combinations of:
 
- base thickness
- fin height
- fin thickness
- fin spacing
- derived fin count
 
Manufacturable candidates are evaluated using a
forced-convection flow and thermal model.
"""
 
import logging
import math

from core.airflow_solver import solve_candidate_airflow
from core.candidate_selector import (
    CandidateSelectionError,
    select_candidates,
)
from core.thermal_solver import ThermalSolver
from core.plate_fin_natural_convection_solver import (
    PlateFinNaturalConvectionSolver,
)
 
from fan.fan_curve import FanCurve
from fan.fan_database import get_fan_curve


from physics.flow_model import (
    blockage_ratio as calculate_blockage_ratio,
    gross_frontal_area as calculate_gross_frontal_area,
    open_flow_area as calculate_open_flow_area,
)
from physics.flow_network import evaluate_flow_network
from physics.fluid_properties import air_properties
from physics.hydraulic_model import (
    fin_count as calculate_fin_count,
)
from physics.mass_model import component_mass
from physics.solid_geometry import (
    plate_fin_heat_sink_volume,
)

from manufacturing.process_database import (
    get_process_capability,
)
from manufacturing.rule_engine import (
    assess_manufacturability,
)
 
from models.material import Material
from models.design_candidate import DesignCandidate
from models.optimization_result import OptimizationResult
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
)
from models.thermal import ThermalResults

from materials.material_cost_database import (
    get_material_cost_profile_for_material,
)
from models.material_cost import (
    MaterialCostProfile,
)
from physics.material_cost_model import (
    calculate_material_cost,
)
 
 
logger = logging.getLogger(__name__)
 
 
class ThermalOptimizer:
    """
    Forced-convection heat-sink design optimizer.
    """
 
    def optimize(
        self,
        requirements,
        selection_configuration: (
            OptimizationSelectionConfiguration | None
        ) = None,
    ) -> ThermalResults:
        """
        Return one uniquely selected thermal result.
 
        When no selection configuration is supplied, the
        existing minimum-thermal-resistance behavior is
        preserved.
 
        Pareto-front selection may produce multiple
        non-dominated candidates. In that case callers
        must use optimize_with_details().
        """
 
        optimization_result = self.optimize_with_details(
            requirements,
            selection_configuration=(
                selection_configuration
            ),
        )
 
        if not optimization_result.has_feasible_design:
            raise ValueError(
                "No manufacturable heat-sink geometry "
                "was found within the supplied design "
                "envelope."
            )
 
        if (
            not optimization_result
            .has_single_selected_design
        ):
            raise ValueError(
                "The configured selection method did not "
                "produce one uniquely selected design. "
                "Use optimize_with_details() to inspect "
                "the complete selection result."
            )
 
        if optimization_result.best_result is None:
            raise RuntimeError(
                "Optimizer reported a single selected "
                "design without a thermal result."
            )
 
        return optimization_result.best_result
 
    def optimize_with_details(
        self,
        requirements,
        selection_configuration: (
            OptimizationSelectionConfiguration | None
        ) = None,
    ) -> OptimizationResult:
        """
        Explore the configured extrusion design space and
        select candidates using the requested strategy.
 
        When selection_configuration is None, minimum
        thermal resistance is used.
        """
 
        thermal_requirements = requirements.requirements
        constraints = requirements.constraints
 
        self._validate_required_inputs(
            requirements
        )

        fan_curve = (
            self._resolve_fan_curve(
                requirements
            )
            if requirements.convection_mode
            == "forced"
            else None
        )
 
        capability = get_process_capability(
            "al6063_t5_extrusion"
        )
 
        _, _, air_k, _, pr = air_properties(
            thermal_requirements.ambient_temperature
        )
 
        maximum_total_height = constraints.max_height
 
        feasible_candidates: list[DesignCandidate] = []
 
        rejected_candidate_count = 0
        total_candidate_count = 0
 
        best_candidate: DesignCandidate | None = None
        best_result: ThermalResults | None = None
 
        selection_result = None

        material_cost_profile = (
            get_material_cost_profile_for_material(
                capability.material
            )
        )
 
        # --------------------------------------------------
        # Design Space
        # --------------------------------------------------
 
        base_thickness_values = [
            3.0,
            4.0,
            5.0,
            6.0,
            8.0,
            10.0,
        ]
 
        fin_thickness_values = [
            0.8,
            1.0,
            1.2,
            1.5,
            2.0,
        ]
 
        fin_height_values = self._float_range(
            start=5.0,
            stop=maximum_total_height - 3.0,
            step=1.0,
        )
 
        fin_spacing_values = self._float_range(
            start=1.6,
            stop=6.0,
            step=0.2,
        )
 
        # --------------------------------------------------
        # Candidate Exploration
        # --------------------------------------------------
 
        for base_thickness in base_thickness_values:
 
            for fin_thickness in fin_thickness_values:
 
                for fin_height in fin_height_values:
 
                    total_height = (
                        base_thickness
                        + fin_height
                    )
 
                    for fin_spacing in fin_spacing_values:
 
                        total_candidate_count += 1
 
                        fin_count = calculate_fin_count(
                            constraints.base_width,
                            fin_thickness,
                            fin_spacing,
                        )
 
                        geometry_candidate = DesignCandidate(
                            base_thickness=base_thickness,
                            fin_thickness=fin_thickness,
                            fin_height=fin_height,
                            fin_spacing=fin_spacing,
                            fin_count=fin_count,
                            total_height=total_height,
 
                            gross_frontal_area=0.0,
                            open_flow_area=0.0,
                            blockage_ratio=0.0,
                            approach_velocity=(
                                thermal_requirements.air_velocity
                            ),
                            channel_velocity=0.0,
 
                            reynolds_number=0.0,
                            nusselt_number=0.0,
                            heat_transfer_coefficient=0.0,

                            friction_factor=float("inf"),
                            pressure_drop=float("inf"),
                            pumping_power=float("inf"),
 
                            thermal_resistance=float("inf"),
                            estimated_base_temperature=float("inf"),
 
                            hydraulic_diameter=0.0,
 
                            solid_volume=0.0,
                            mass=0.0,
 
                            convection_mode=(
                                requirements
                                .convection_mode
                            ),
                        )
 
                        manufacturing_assessment = (
                            assess_manufacturability(
                                candidate=geometry_candidate,
                                capability=capability,
                                maximum_total_height=(
                                    maximum_total_height
                                ),
                            )
                        )
 
                        if not manufacturing_assessment.is_feasible:
                            rejected_candidate_count += 1
                            continue
 
                        try:
                            thermal_candidate = (
                                self._evaluate_thermal_candidate(
                                    candidate=geometry_candidate,
                                    requirements=requirements,
                                    air_conductivity=air_k,
                                    prandtl_number=pr,
                                    material=(
                                        capability.material
                                    ),
                                    fan_curve=fan_curve,
                                    approach_velocity=(
                                        thermal_requirements.air_velocity
                                        if (
                                            requirements
                                            .convection_mode
                                            == "forced"
                                        )
                                        else 0.0
                                    ),
                                    material_cost_profile=(
                                        material_cost_profile
                                    ),
                                )
                            )
 
                        except ValueError as exc:
                            logger.debug(
                                "Candidate rejected during flow "
                                "evaluation: %s",
                                exc,
                            )
 
                            rejected_candidate_count += 1
                            continue

                        material_cost_budget = (
                            constraints.material_cost_budget
                        )
 
                        if material_cost_budget is not None:
                            if (
                                thermal_candidate.material_cost
                                is None
                                or thermal_candidate
                                .material_cost_currency
                                is None
                            ):
                                raise RuntimeError(
                                    "Material-cost evaluation "
                                    "is missing from a completed "
                                    "candidate."
                                )
 
                            if (
                                thermal_candidate
                                .material_cost_currency
                                != material_cost_budget
                                .currency_code
                            ):
                                raise ValueError(
                                    "Material-cost budget currency "
                                    "does not match the candidate "
                                    "cost currency. "
                                    f"Budget: "
                                    f"{material_cost_budget.currency_code}; "
                                    f"candidate: "
                                    f"{thermal_candidate.material_cost_currency}."
                                )
 
                            if (
                                thermal_candidate.material_cost
                                >
                                material_cost_budget
                                .maximum_amount
                            ):
                                rejected_candidate_count += 1
                                continue
 
                        feasible_candidates.append(
                            thermal_candidate
                        )
 
                        
 
        # --------------------------------------------------
        # Candidate Selection
        # --------------------------------------------------
 
        if feasible_candidates:
            try:
                selection_result = select_candidates(
                    tuple(feasible_candidates),
                    selection_configuration,
                )
 
            except CandidateSelectionError as exc:
                raise ValueError(
                    "Feasible thermal candidates were "
                    "generated, but candidate selection "
                    "could not be completed."
                ) from exc
 
            best_candidate = (
                selection_result.selected_candidate
            )
 
        # --------------------------------------------------
        # Convert Unique Selected Candidate
        # --------------------------------------------------
 
        if best_candidate is not None:
            best_result = (
                self._candidate_to_thermal_results(
                    candidate=best_candidate,
                    material_name=(
                        capability.material.display_name
                    ),
                )
            )
 
        logger.info(
            "Design-space exploration completed."
        )
 
        logger.info(
            "Total candidates evaluated: %d",
            total_candidate_count,
        )
 
        logger.info(
            "Feasible candidates: %d",
            len(feasible_candidates),
        )
 
        logger.info(
            "Rejected candidates: %d",
            rejected_candidate_count,
        )
 
        if best_candidate is not None:
            logger.info(
                (
                    "Selected design | Base=%.1f mm | "
                    "Fin height=%.1f mm | "
                    "Fin thickness=%.1f mm | "
                    "Spacing=%.1f mm | "
                    "Fins=%d | Channel velocity=%.2f m/s | "
                    "Rth=%.3f °C/W"
                ),
                best_candidate.base_thickness,
                best_candidate.fin_height,
                best_candidate.fin_thickness,
                best_candidate.fin_spacing,
                best_candidate.fin_count,
                best_candidate.channel_velocity,
                best_candidate.thermal_resistance,
            )
 
        elif (
            selection_result is not None
            and selection_result.uses_pareto_selection
        ):
            logger.info(
                (
                    "Pareto selection returned %d "
                    "non-dominated designs."
                ),
                (
                    selection_result
                    .selected_candidate_count
                ),
            )
 
        return OptimizationResult(
            best_result=best_result,
 
            candidates=feasible_candidates,
 
            feasible_candidate_count=len(
                feasible_candidates
            ),
 
            rejected_candidate_count=(
                rejected_candidate_count
            ),
 
            selected_material=(
                capability.material.display_name
            ),
 
            selected_process=(
                capability.process_name
            ),
 
            selection_result=selection_result,
        )
    
    
    @staticmethod
    def _candidate_to_thermal_results(
        candidate: DesignCandidate,
        material_name: str,
    ) -> ThermalResults:
        """
        Convert one selected DesignCandidate into the
        existing UI-facing ThermalResults model.
        """
 
        return ThermalResults(
            gross_frontal_area=(
                candidate.gross_frontal_area
            ),
            open_flow_area=(
                candidate.open_flow_area
            ),
            blockage_ratio=(
                candidate.blockage_ratio
            ),
            approach_velocity=(
                candidate.approach_velocity
            ),
            channel_velocity=(
                candidate.channel_velocity
            ),
 
            reynolds_number=(
                candidate.reynolds_number
            ),
            hydraulic_diameter=(
                candidate.hydraulic_diameter
                * 1000.0
            ),
            nusselt_number=(
                candidate.nusselt_number
            ),
            heat_transfer_coefficient=(
                candidate.heat_transfer_coefficient
            ),
            radiative_heat_transfer_coefficient=(
                candidate
                .radiative_heat_transfer_coefficient
            ),
            friction_factor=(
                candidate.friction_factor
            ),
            pressure_drop=(
                candidate.pressure_drop
            ),
            pumping_power=(
                candidate.pumping_power
            ),
 
            fin_count=candidate.fin_count,
            fin_thickness=(
                candidate.fin_thickness
            ),
            fin_spacing=(
                candidate.fin_spacing
            ),
            fin_height=(
                candidate.fin_height
            ),
            base_thickness=(
                candidate.base_thickness
            ),
 
            thermal_resistance=(
                candidate.thermal_resistance
            ),
            estimated_base_temperature=(
                candidate.estimated_base_temperature
            ),
 
            material=material_name,
        )
 
    @staticmethod
    def _evaluate_thermal_candidate(
        candidate: DesignCandidate,
        requirements,
        air_conductivity: float,
        prandtl_number: float,
        material: Material,
        fan_curve: FanCurve | None,
        approach_velocity: float | None,
        material_cost_profile: (
            MaterialCostProfile
        ),
    ) -> DesignCandidate:
        """
        Evaluate thermal performance for one manufacturable
        geometry using the configured convection mode.
        """
 
        base_width = (
            requirements.constraints.base_width
        )

        # ---------------------------------------------------------
        # Natural-Convection Evaluation
        # ---------------------------------------------------------
 
        if requirements.convection_mode == "natural":
 
            thermal_state = (
                PlateFinNaturalConvectionSolver.solve(
                    candidate=candidate,
                    requirements=requirements,
                    material_conductivity=(
                        material.thermal_conductivity
                    ),
                )
            )
 
            gross_area = (
                calculate_gross_frontal_area(
                    base_width,
                    candidate.fin_height,
                )
            )
 
            open_area = (
                calculate_open_flow_area(
                    candidate.fin_count,
                    candidate.fin_spacing,
                    candidate.fin_height,
                )
            )
 
            blockage = (
                calculate_blockage_ratio(
                    gross_area,
                    open_area,
                )
            )
 
            solid_volume = (
                plate_fin_heat_sink_volume(
                    base_length_mm=(
                        requirements
                        .constraints
                        .base_length
                    ),
                    base_width_mm=(
                        requirements
                        .constraints
                        .base_width
                    ),
                    base_thickness_mm=(
                        candidate.base_thickness
                    ),
                    fin_height_mm=(
                        candidate.fin_height
                    ),
                    fin_thickness_mm=(
                        candidate.fin_thickness
                    ),
                    fin_count=candidate.fin_count,
                )
            )
 
            mass = component_mass(
                solid_volume,
                material,
            )
 
            material_cost_result = (
                calculate_material_cost(
                    mass_kg=mass,
                    cost_profile=(
                        material_cost_profile
                    ),
                )
            )
 
            return DesignCandidate(
                base_thickness=(
                    candidate.base_thickness
                ),
                fin_thickness=(
                    candidate.fin_thickness
                ),
                fin_height=candidate.fin_height,
                fin_spacing=candidate.fin_spacing,
                fin_count=candidate.fin_count,
                total_height=candidate.total_height,
 
                gross_frontal_area=gross_area,
                open_flow_area=open_area,
                blockage_ratio=blockage,
 
                approach_velocity=0.0,
                channel_velocity=0.0,
 
                reynolds_number=0.0,
 
                nusselt_number=(
                    thermal_state.nusselt_number
                ),
 
                heat_transfer_coefficient=(
                    thermal_state
                    .heat_transfer_coefficient
                ),
                radiative_heat_transfer_coefficient=(
                    thermal_state
                    .radiative_heat_transfer_coefficient
                ),
 
                friction_factor=0.0,
                pressure_drop=0.0,
                pumping_power=0.0,
 
                thermal_resistance=(
                    thermal_state
                    .thermal_resistance
                ),
 
                estimated_base_temperature=(
                    thermal_state
                    .estimated_base_temperature
                ),
 
                hydraulic_diameter=0.0,
 
                solid_volume=solid_volume,
                mass=mass,
 
                material_cost_result=(
                    material_cost_result
                ),
 
                convection_mode="natural",
            )
 
        # ---------------------------------------------------------
        # Airflow Evaluation
        # ---------------------------------------------------------
        
        if fan_curve is not None:
        
            flow_state = solve_candidate_airflow(
                fan_curve=fan_curve,
                base_width_mm=base_width,
                fin_height_mm=candidate.fin_height,
                fin_count_value=candidate.fin_count,
                fin_spacing_mm=candidate.fin_spacing,
                channel_length_mm=(
                    requirements.constraints.base_length
                ),
                air_temperature_c=(
                    requirements
                    .requirements
                    .ambient_temperature
                ),
            )
        
        else:
        
            if approach_velocity is None:
                raise ValueError(
                    "Approach air velocity is required when "
                    "no fan specification is supplied."
                )
        
            resolved_approach_velocity = (
                approach_velocity
            )
        
            flow_state = evaluate_flow_network(
                volumetric_flow_rate=(
                    calculate_gross_frontal_area(
                        base_width,
                        candidate.fin_height,
                    )
                    * resolved_approach_velocity
                ),
                base_width_mm=base_width,
                fin_height_mm=candidate.fin_height,
                fin_count_value=candidate.fin_count,
                fin_spacing_mm=candidate.fin_spacing,
                channel_length_mm=(
                    requirements.constraints.base_length
                ),
                air_temperature_c=(
                    requirements
                    .requirements
                    .ambient_temperature
                ),
            )
 
        thermal_state = ThermalSolver.solve(
            candidate=candidate,
            flow_state=flow_state,
            requirements=requirements,
            air_conductivity=air_conductivity,
            prandtl_number=prandtl_number,
            material_conductivity=(
                material.thermal_conductivity
            ),
        )

        solid_volume = (
            plate_fin_heat_sink_volume(
                base_length_mm=(
                    requirements
                    .constraints
                    .base_length
                ),
                base_width_mm=(
                    requirements
                    .constraints
                    .base_width
                ),
                base_thickness_mm=(
                    candidate.base_thickness
                ),
                fin_height_mm=(
                    candidate.fin_height
                ),
                fin_thickness_mm=(
                    candidate.fin_thickness
                ),
                fin_count=candidate.fin_count,
            )
        )
 
        mass = component_mass(
            solid_volume,
            material,
        )

        material_cost_result = (
            calculate_material_cost(
                mass_kg=mass,
                cost_profile=(
                    material_cost_profile
                ),
            )
        )
 
        return DesignCandidate(
            base_thickness=candidate.base_thickness,
            fin_thickness=candidate.fin_thickness,
            fin_height=candidate.fin_height,
            fin_spacing=candidate.fin_spacing,
            fin_count=candidate.fin_count,
            total_height=candidate.total_height,
 
            gross_frontal_area=flow_state.gross_flow_area,
            open_flow_area=flow_state.open_flow_area,
            blockage_ratio=flow_state.blockage_ratio,
            approach_velocity=flow_state.approach_velocity,
            channel_velocity=flow_state.channel_velocity,
            
            reynolds_number=flow_state.reynolds_number,
            
            friction_factor=flow_state.friction_factor,
            pressure_drop=flow_state.pressure_drop,
            pumping_power=flow_state.pumping_power,

            nusselt_number=thermal_state.nusselt_number,
 
            heat_transfer_coefficient=(
                thermal_state.heat_transfer_coefficient
            ),
            
            thermal_resistance=(
                thermal_state.thermal_resistance
            ),
            
            estimated_base_temperature=(
                thermal_state.estimated_base_temperature
            ),
 
            hydraulic_diameter=(
                flow_state.hydraulic_diameter
            ),
 
            solid_volume=solid_volume,
            mass=mass,

            material_cost_result=(
                material_cost_result
            ),
        )
 
    @staticmethod
    def _resolve_fan_curve(
        requirements,
    ) -> FanCurve | None:
        """
        Resolve the fan curve for fan-coupled mode.
    
        Returning None selects the legacy fixed-air-velocity
        calculation.
        """
    
        fan_specification = requirements.fan
    
        if fan_specification is None:
            return None
    
        if fan_specification.fan_count != 1:
            raise ValueError(
                "The current fan-coupled optimizer supports "
                "exactly one fan."
            )
    
        if fan_specification.speed_fraction != 1.0:
            raise ValueError(
                "Fan speed scaling is not implemented yet. "
                "speed_fraction must currently equal 1.0."
            )
    
        if fan_specification.fan_curve is not None:
            return fan_specification.fan_curve
    
        if fan_specification.fan_name is not None:
            return get_fan_curve(
                fan_specification.fan_name
            )
    
        raise ValueError(
            "FanSpecification must contain either "
            "fan_curve or fan_name."
        )
    
    @staticmethod
    def _validate_required_inputs(
        requirements,
    ) -> None:
        """
        Defensive validation before optimization.
        """
 
        thermal = requirements.requirements
        constraints = requirements.constraints
 
        if requirements.convection_mode not in {
            "forced",
            "natural",
        }:
            raise ValueError(
                "Convection mode must be either "
                "'forced' or 'natural'."
            )
 
        required_values = {
            "heat_load": thermal.heat_load,
            "ambient_temperature": (
                thermal.ambient_temperature
            ),
            "base_length": constraints.base_length,
            "base_width": constraints.base_width,
            "max_height": constraints.max_height,
        }
        
        if (
            requirements.convection_mode == "forced"
            and requirements.fan is None
        ):
            required_values["air_velocity"] = (
                thermal.air_velocity
            )
 
        missing_fields = [
            field_name
            for field_name, value
            in required_values.items()
            if value is None
        ]
 
        if missing_fields:
            raise ValueError(
                "Missing required optimizer inputs: "
                + ", ".join(missing_fields)
            )
 
        if thermal.heat_load <= 0:
            raise ValueError(
                "Heat load must be greater than 0 W."
            )
 
        if (
            requirements.convection_mode == "forced"
            and requirements.fan is None
        ):
 
            if thermal.air_velocity is None:
                raise ValueError(
                    "Approach air velocity is required when "
                    "no fan specification is supplied."
                )
        
            if thermal.air_velocity <= 0:
                raise ValueError(
                    "Approach air velocity must be greater "
                    "than 0 m/s."
                )

        if (
            requirements.convection_mode == "natural"
            and requirements.fan is not None
        ):
            raise ValueError(
                "A fan specification is not applicable "
                "to natural-convection optimization."
            )    
 
        if constraints.base_length <= 0:
            raise ValueError(
                "Base length must be greater than 0 mm."
            )
 
        if constraints.base_width <= 0:
            raise ValueError(
                "Base width must be greater than 0 mm."
            )
 
        if constraints.max_height <= 3.0:
            raise ValueError(
                "Maximum total height must exceed the "
                "minimum 3 mm base thickness."
            )
 
    @staticmethod
    def _float_range(
        start: float,
        stop: float,
        step: float,
    ) -> list[float]:
        """
        Generate an inclusive floating-point range.
        """
 
        if step <= 0:
            raise ValueError(
                "Range step must be greater than zero."
            )
 
        values: list[float] = []
 
        current = start
 
        while current <= stop + 1e-9:
            values.append(
                round(current, 10)
            )
 
            current += step
 
        return values