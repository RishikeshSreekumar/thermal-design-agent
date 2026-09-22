"""
thermal_analyzer.py
 
Generate deterministic insights describing the thermal
performance of selected heat-sink candidates.
 
This analyzer reports calculated thermal facts. It does
not apply unsupported acceptance thresholds and does not
invoke an LLM.
"""
 
from intelligence.analyzers.base_analyzer import (
    EngineeringAnalyzer,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_evidence import (
    EngineeringEvidence,
)
from models.engineering_insight import (
    EngineeringInsight,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
class ThermalAnalyzer(
    EngineeringAnalyzer,
):
    """
    Generate structured thermal-performance insights for
    the candidate or candidates selected by optimization.
    """
 
    def analyze(
        self,
        context: EngineeringContext,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Generate thermal insights appropriate to the
        selection result.
        """
 
        if not isinstance(
            context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )
 
        if context.has_single_selected_design:
            selected_candidate = (
                context.selected_candidate
            )
 
            if selected_candidate is None:
                raise RuntimeError(
                    "Single-design engineering context "
                    "contains no selected candidate."
                )
 
            return (
                self._build_single_candidate_insight(
                    selected_candidate,
                    context,
                ),
            )
 
        return (
            self._build_tradeoff_set_insight(
                context.selected_candidates,
                context,
            ),
        )
 
    @staticmethod
    def _build_single_candidate_insight(
        candidate: DesignCandidate,
        context: EngineeringContext,
    ) -> EngineeringInsight:
        """
        Report calculated thermal performance for one
        uniquely selected design.
 
        Natural-convection results additionally preserve
        the configured orientation and separated
        convection/radiation heat-transfer state.
        """
 
        evidence = [
            EngineeringEvidence(
                key="thermal_resistance",
                value=candidate.thermal_resistance,
                unit="degC/W",
            ),
            EngineeringEvidence(
                key="estimated_base_temperature",
                value=(
                    candidate.estimated_base_temperature
                ),
                unit="degC",
            ),
            EngineeringEvidence(
                key="heat_transfer_coefficient",
                value=(
                    candidate.heat_transfer_coefficient
                ),
                unit="W/(m^2*K)",
            ),
            EngineeringEvidence(
                key="nusselt_number",
                value=candidate.nusselt_number,
            ),
            EngineeringEvidence(
                key="reynolds_number",
                value=candidate.reynolds_number,
            ),
        ]
 
        if candidate.convection_mode == "natural":
 
            specification = (
                context.requirements
                .natural_convection
            )
 
            orientation = "vertical"
            radiation_enabled = False
            emissivity = None
            surroundings_temperature = None
 
            if specification is not None:
 
                if specification.orientation is not None:
                    orientation = (
                        specification.orientation
                    )
 
                radiation_enabled = (
                    specification.include_radiation
                )
 
                emissivity = (
                    specification.surface_emissivity
                )
 
                surroundings_temperature = (
                    specification
                    .surroundings_temperature
                )
 
            evidence.extend(
                [
                    EngineeringEvidence(
                        key=(
                            "natural_convection_orientation"
                        ),
                        value=orientation,
                    ),
                    EngineeringEvidence(
                        key="radiation_enabled",
                        value=radiation_enabled,
                    ),
                    EngineeringEvidence(
                        key=(
                            "convective_heat_transfer_"
                            "coefficient"
                        ),
                        value=(
                            candidate
                            .convective_heat_transfer_coefficient
                        ),
                        unit="W/(m^2*K)",
                    ),
                    EngineeringEvidence(
                        key=(
                            "radiative_heat_transfer_"
                            "coefficient"
                        ),
                        value=(
                            candidate
                            .radiative_heat_transfer_coefficient
                        ),
                        unit="W/(m^2*K)",
                    ),
                    EngineeringEvidence(
                        key=(
                            "effective_heat_transfer_"
                            "coefficient"
                        ),
                        value=(
                            candidate
                            .effective_heat_transfer_coefficient
                        ),
                        unit="W/(m^2*K)",
                    ),
                ]
            )
 
            if (
                radiation_enabled
                and emissivity is not None
            ):
                evidence.append(
                    EngineeringEvidence(
                        key="surface_emissivity",
                        value=emissivity,
                    )
                )
 
            if (
                radiation_enabled
                and surroundings_temperature
                is not None
            ):
                evidence.append(
                    EngineeringEvidence(
                        key=(
                            "radiative_surroundings_"
                            "temperature"
                        ),
                        value=(
                            surroundings_temperature
                        ),
                        unit="degC",
                    )
                )
 
        return EngineeringInsight(
            insight_id=(
                "thermal.selected_design_performance"
            ),
            severity=EngineeringSeverity.INFO,
            category=EngineeringCategory.THERMAL,
            title="Selected-design thermal performance",
            summary=(
                "The deterministic thermal model "
                "calculated the thermal performance of "
                "the uniquely selected heat-sink design."
            ),
            evidence=tuple(evidence),
            source="selected_design_candidate",
        )
 
    @staticmethod
    def _build_tradeoff_set_insight(
        candidates: tuple[
            DesignCandidate,
            ...,
        ],
        context: EngineeringContext,
    ) -> EngineeringInsight:
        """
        Report thermal ranges across multiple selected
        Pareto-optimal candidates.
        """
 
        if len(candidates) < 2:
            raise ValueError(
                "Thermal trade-off insight requires at "
                "least two selected candidates."
            )
 
        thermal_resistances = tuple(
            candidate.thermal_resistance
            for candidate in candidates
        )
 
        base_temperatures = tuple(
            candidate.estimated_base_temperature
            for candidate in candidates
        )
 
        heat_transfer_coefficients = tuple(
            candidate.heat_transfer_coefficient
            for candidate in candidates
        )

        additional_evidence = []
 
        if all(
            candidate.convection_mode == "natural"
            for candidate in candidates
        ):
            specification = (
                context.requirements
                .natural_convection
            )
 
            orientation = "vertical"
            radiation_enabled = False
            emissivity = None
 
            if specification is not None:
 
                if specification.orientation is not None:
                    orientation = (
                        specification.orientation
                    )
 
                radiation_enabled = (
                    specification.include_radiation
                )
 
                emissivity = (
                    specification.surface_emissivity
                )
 
            convective_coefficients = tuple(
                candidate
                .convective_heat_transfer_coefficient
                for candidate in candidates
            )
 
            radiative_coefficients = tuple(
                candidate
                .radiative_heat_transfer_coefficient
                for candidate in candidates
            )
 
            additional_evidence.extend(
                [
                    EngineeringEvidence(
                        key=(
                            "natural_convection_orientation"
                        ),
                        value=orientation,
                    ),
                    EngineeringEvidence(
                        key="radiation_enabled",
                        value=radiation_enabled,
                    ),
                    EngineeringEvidence(
                        key=(
                            "minimum_convective_heat_"
                            "transfer_coefficient"
                        ),
                        value=min(
                            convective_coefficients
                        ),
                        unit="W/(m^2*K)",
                    ),
                    EngineeringEvidence(
                        key=(
                            "maximum_convective_heat_"
                            "transfer_coefficient"
                        ),
                        value=max(
                            convective_coefficients
                        ),
                        unit="W/(m^2*K)",
                    ),
                    EngineeringEvidence(
                        key=(
                            "minimum_radiative_heat_"
                            "transfer_coefficient"
                        ),
                        value=min(
                            radiative_coefficients
                        ),
                        unit="W/(m^2*K)",
                    ),
                    EngineeringEvidence(
                        key=(
                            "maximum_radiative_heat_"
                            "transfer_coefficient"
                        ),
                        value=max(
                            radiative_coefficients
                        ),
                        unit="W/(m^2*K)",
                    ),
                ]
            )
 
            if (
                radiation_enabled
                and emissivity is not None
            ):
                additional_evidence.append(
                    EngineeringEvidence(
                        key="surface_emissivity",
                        value=emissivity,
                    )
                )
 
        return EngineeringInsight(
            insight_id=(
                "thermal.tradeoff_set_performance"
            ),
            severity=EngineeringSeverity.INFO,
            category=EngineeringCategory.THERMAL,
            title="Thermal range across trade-off set",
            summary=(
                "The selected Pareto-optimal candidates "
                "span a range of calculated thermal "
                "performance values."
            ),
            evidence=(
                EngineeringEvidence(
                    key="selected_candidate_count",
                    value=len(candidates),
                ),
                EngineeringEvidence(
                    key=(
                        "minimum_thermal_resistance"
                    ),
                    value=min(
                        thermal_resistances
                    ),
                    unit="degC/W",
                ),
                EngineeringEvidence(
                    key=(
                        "maximum_thermal_resistance"
                    ),
                    value=max(
                        thermal_resistances
                    ),
                    unit="degC/W",
                ),
                EngineeringEvidence(
                    key=(
                        "minimum_estimated_base_temperature"
                    ),
                    value=min(
                        base_temperatures
                    ),
                    unit="degC",
                ),
                EngineeringEvidence(
                    key=(
                        "maximum_estimated_base_temperature"
                    ),
                    value=max(
                        base_temperatures
                    ),
                    unit="degC",
                ),
                EngineeringEvidence(
                    key=(
                        "minimum_heat_transfer_coefficient"
                    ),
                    value=min(
                        heat_transfer_coefficients
                    ),
                    unit="W/(m^2*K)",
                ),
                EngineeringEvidence(
                    key=(
                        "maximum_heat_transfer_coefficient"
                    ),
                    value=max(
                        heat_transfer_coefficients
                    ),
                    unit="W/(m^2*K)",
                ),
                *additional_evidence,
            ),
            source="selected_pareto_candidates",
        )