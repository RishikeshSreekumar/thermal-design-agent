"""
thermal_solver.py
 
Deterministic thermal solver for plate-fin heat-sink
design candidates.
 
The solver now supports a common ConvectionState boundary.
 
Forced-convection callers may continue using the existing
solve() interface with a resolved FlowNetworkResult.
 
Natural convection and future convection models may use
solve_from_convection_state() directly after resolving
their own ConvectionState.
 
Responsibilities:
 
- Calculate total heat-transfer surface area
- Calculate fin efficiency
- Calculate thermal resistance
- Estimate heat-sink base temperature
 
The solver does not perform:
 
- Design-space generation
- Manufacturability assessment
- Fan operating-point calculations
- Hydraulic calculations
- Candidate ranking
- Natural- or forced-convection correlation selection
"""

import math
  
from core.forced_convection_solver import (
    ForcedConvectionSolver,
)
 
from models.convection_state import (
    ConvectionState,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.requirements import (
    EngineeringRequirements,
)
from models.thermal_state import (
    ThermalState,
)
 
from physics.fin_model import (
    fin_efficiency as calculate_fin_efficiency,
    total_surface_area as calculate_total_surface_area,
)
from physics.flow_network import (
    FlowNetworkResult,
)
from physics.resistance import (
    thermal_resistance as calculate_thermal_resistance,
)
 
 
class ThermalSolver:
    """
    Evaluate thermal performance for one plate-fin
    heat-sink design candidate.
 
    The common thermal calculation consumes a resolved
    ConvectionState.
 
    The existing solve() entry point is retained for
    backward-compatible forced-convection callers.
    """
 
    @staticmethod
    def solve(
        candidate: DesignCandidate,
        flow_state: FlowNetworkResult,
        requirements: EngineeringRequirements,
        air_conductivity: float,
        prandtl_number: float,
        material_conductivity: float,
    ) -> ThermalState:
        """
        Backward-compatible forced-convection thermal solve.
 
        The supplied FlowNetworkResult is first converted
        into the common ConvectionState before the common
        thermal calculation is performed.
        """
 
        ThermalSolver._validate_inputs(
            candidate=candidate,
            flow_state=flow_state,
            requirements=requirements,
            air_conductivity=air_conductivity,
            prandtl_number=prandtl_number,
            material_conductivity=material_conductivity,
        )
 
        convection_state = (
            ForcedConvectionSolver.solve(
                flow_state=flow_state,
                air_conductivity=air_conductivity,
                prandtl_number=prandtl_number,
            )
        )
 
        return (
            ThermalSolver.solve_from_convection_state(
                candidate=candidate,
                convection_state=convection_state,
                requirements=requirements,
                material_conductivity=(
                    material_conductivity
                ),
            )
        )
 
    def solve_from_convection_state(
        *,
        candidate: DesignCandidate,
        convection_state: ConvectionState,
        requirements: EngineeringRequirements,
        material_conductivity: float,
        radiative_heat_transfer_coefficient: float = 0.0,
    ) -> ThermalState:
        """
        Calculate thermal performance using an already
        resolved convection state.
 
        This is the common thermal boundary for:
 
        - forced convection;
        - natural convection;
        - future convection models.
 
        The convection model is responsible for determining
        Nusselt number and heat-transfer coefficient before
        this method is called.
        """
 
        ThermalSolver._validate_convection_inputs(
            candidate=candidate,
            convection_state=convection_state,
            requirements=requirements,
            material_conductivity=(
                material_conductivity
            ),
            radiative_heat_transfer_coefficient=(
                radiative_heat_transfer_coefficient
            ),
        )

        convective_heat_transfer_coefficient = (
            convection_state
            .heat_transfer_coefficient
        )
 
        effective_heat_transfer_coefficient = (
            convective_heat_transfer_coefficient
            + radiative_heat_transfer_coefficient
        )
 
        total_surface_area = (
            calculate_total_surface_area(
                requirements.constraints.base_length,
                requirements.constraints.base_width,
                candidate.fin_height,
                candidate.fin_thickness,
                candidate.fin_count,
            )
        )
 
        fin_efficiency = (
            calculate_fin_efficiency(
                effective_heat_transfer_coefficient,
                candidate.fin_thickness,
                candidate.fin_height,
                conductivity=(
                    material_conductivity
                ),
            )
        )
 
        thermal_resistance = (
            calculate_thermal_resistance(
                effective_heat_transfer_coefficient,
                total_surface_area,
                fin_efficiency,
            )
        )
 
        estimated_base_temperature = (
            requirements
            .requirements
            .ambient_temperature
            + requirements
            .requirements
            .heat_load
            * thermal_resistance
        )
 
        return ThermalState(
            nusselt_number=(
                convection_state.nusselt_number
            ),
            heat_transfer_coefficient=(
                effective_heat_transfer_coefficient
            ),
            total_surface_area=(
                total_surface_area
            ),
            fin_efficiency=(
                fin_efficiency
            ),
            thermal_resistance=(
                thermal_resistance
            ),
            estimated_base_temperature=(
                estimated_base_temperature
            ),
            radiative_heat_transfer_coefficient=(
                radiative_heat_transfer_coefficient
            ),
        )
 
    @staticmethod
    def _validate_convection_inputs(
        *,
        candidate: DesignCandidate,
        convection_state: ConvectionState,
        requirements: EngineeringRequirements,
        material_conductivity: float,
        radiative_heat_transfer_coefficient: float = 0.0,
    ) -> None:
        """
        Validate inputs required by the common thermal
        calculation.
        """
 
        if not isinstance(
            candidate,
            DesignCandidate,
        ):
            raise ValueError(
                "'candidate' must be a "
                "DesignCandidate object."
            )
 
        if not isinstance(
            convection_state,
            ConvectionState,
        ):
            raise ValueError(
                "'convection_state' must be a "
                "ConvectionState object."
            )
 
        if not isinstance(
            requirements,
            EngineeringRequirements,
        ):
            raise ValueError(
                "'requirements' must be an "
                "EngineeringRequirements object."
            )
 
        if candidate.fin_count <= 0:
            raise ValueError(
                "Fin count must be greater than zero."
            )
 
        if candidate.fin_height <= 0:
            raise ValueError(
                "Fin height must be greater than zero."
            )
 
        if candidate.fin_thickness <= 0:
            raise ValueError(
                "Fin thickness must be greater than zero."
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
 
        if (
            requirements.constraints.base_width
            is None
            or requirements.constraints.base_width
            <= 0
        ):
            raise ValueError(
                "Base width must be greater than zero."
            )
 
        if (
            requirements.requirements.heat_load
            is None
            or requirements.requirements.heat_load
            <= 0
        ):
            raise ValueError(
                "Heat load must be greater than zero."
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
 
        if material_conductivity <= 0:
            raise ValueError(
                "Material thermal conductivity must be "
                "greater than zero."
            )
        if not math.isfinite(
            radiative_heat_transfer_coefficient
        ):
            raise ValueError(
                "Radiative heat-transfer coefficient "
                "must be finite."
            )
 
        if (
            radiative_heat_transfer_coefficient
            < 0.0
        ):
            raise ValueError(
                "Radiative heat-transfer coefficient "
                "cannot be negative."
            )

    
 
    @staticmethod
    def _validate_inputs(
        candidate: DesignCandidate,
        flow_state: FlowNetworkResult,
        requirements: EngineeringRequirements,
        air_conductivity: float,
        prandtl_number: float,
        material_conductivity: float,
    ) -> None:
        """
        Validate inputs required by the existing
        forced-convection solve() interface.
 
        This validation is retained to preserve the existing
        ThermalSolver contract and regression behaviour.
        """
 
        if candidate.fin_count <= 0:
            raise ValueError(
                "Fin count must be greater than zero."
            )
 
        if candidate.fin_height <= 0:
            raise ValueError(
                "Fin height must be greater than zero."
            )
 
        if candidate.fin_thickness <= 0:
            raise ValueError(
                "Fin thickness must be greater than zero."
            )
 
        if flow_state.hydraulic_diameter <= 0:
            raise ValueError(
                "Hydraulic diameter must be greater "
                "than zero."
            )
 
        if flow_state.reynolds_number < 0:
            raise ValueError(
                "Reynolds number cannot be negative."
            )
 
        if requirements.constraints.base_length <= 0:
            raise ValueError(
                "Base length must be greater than zero."
            )
 
        if requirements.constraints.base_width <= 0:
            raise ValueError(
                "Base width must be greater than zero."
            )
 
        if requirements.requirements.heat_load <= 0:
            raise ValueError(
                "Heat load must be greater than zero."
            )
 
        if air_conductivity <= 0:
            raise ValueError(
                "Air thermal conductivity must be "
                "greater than zero."
            )
 
        if prandtl_number <= 0:
            raise ValueError(
                "Prandtl number must be greater than zero."
            )
 
        if material_conductivity <= 0:
            raise ValueError(
                "Material thermal conductivity must be "
                "greater than zero."
            )