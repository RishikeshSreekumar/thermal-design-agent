"""
engineering_report_builder.py
 
Deterministic builder for the canonical engineering report.
 
The builder converts the completed engineering
recommendation workflow into concise, professional,
renderer-neutral report content.
 
It does not:
- invoke an LLM;
- perform engineering calculations;
- change engineering-review status;
- render PDF, DOCX, HTML, or Streamlit output.
"""
 
from models.engineering_report import (
    EngineeringReport,
    EngineeringReportSection,
)
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
 
 
class EngineeringReportBuilder:
    """
    Build a professional structured engineering report
    from the completed recommendation workflow.
    """
 
    @classmethod
    def build(
        cls,
        source: EngineeringRecommendationResult,
    ) -> EngineeringReport:
 
        if not isinstance(
            source,
            EngineeringRecommendationResult,
        ):
            raise ValueError(
                "'source' must be an "
                "EngineeringRecommendationResult object."
            )
 
        review_result = source.review_result
        review = review_result.review
 
        intelligence_result = (
            review_result
            .source
            .intelligence_result
        )
 
        context = intelligence_result.context
        requirements = context.requirements
        optimization = context.optimization_result
 
        selected = optimization.selected_candidate
 
        sections = [
            cls._build_requirements_section(
                requirements
            ),
        ]
 
        if selected is not None:
            sections.extend(
                [
                    cls._build_selected_design_section(
                        selected=selected,
                        material_name=(
                            optimization.selected_material
                        ),
                        process_name=(
                            optimization.selected_process
                        ),
                    ),
                    cls._build_performance_section(
                        selected,
                        requirements,
                    ),
                ]
            )
 
        sections.append(
            cls._build_engineering_assessment_section(
                review
            )
        )
 
        if source.has_recommendations:
            sections.append(
                cls._build_recommendations_section(
                    source
                )
            )
 
        sections.append(
            cls._build_validation_section(
                review
            )
        )
 
        return EngineeringReport(
            source=source,
            title="Thermal Design Engineering Report",
            executive_summary=(
                review.executive_summary
            ),
            status=review.status,
            sections=tuple(sections),
        )

    @staticmethod
    def _format_natural_orientation(
        orientation: str,
    ) -> str:
        """
        Return engineer-readable natural-convection
        orientation text for reports.
        """
 
        labels = {
            "vertical": "Vertical",
            "horizontal_fins_up": (
                "Horizontal — Fins Upward"
            ),
            "horizontal_fins_down": (
                "Horizontal — Fins Downward"
            ),
        }
 
        return labels.get(
            orientation,
            orientation,
        )    
 
 
    @staticmethod
    def _build_requirements_section(
        requirements,
    ) -> EngineeringReportSection:
 
        thermal = requirements.requirements
        constraints = requirements.constraints
 
        lines = [
            (
                "Cooling mode: "
                f"{requirements.convection_mode}"
            ),
            (
                "Heat load: "
                f"{thermal.heat_load:g} W"
            ),
            (
                "Ambient temperature: "
                f"{thermal.ambient_temperature:g} °C"
            ),
            (
                "Available base: "
                f"{constraints.base_length:g} × "
                f"{constraints.base_width:g} mm"
            ),
            (
                "Maximum total height: "
                f"{constraints.max_height:g} mm"
            ),
        ]

        if requirements.convection_mode == "natural":
 
            specification = (
                requirements.natural_convection
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
 
            lines.extend(
                [
                    (
                        "Natural-convection orientation: "
                        f"{EngineeringReportBuilder._format_natural_orientation(orientation)}"
                    ),
                    (
                        "Thermal radiation: "
                        + (
                            "Included"
                            if radiation_enabled
                            else "Excluded"
                        )
                    ),
                ]
            )
 
            if (
                radiation_enabled
                and emissivity is not None
            ):
                lines.append(
                    "Surface emissivity: "
                    f"{emissivity:.2f}"
                )
 
            if (
                radiation_enabled
                and surroundings_temperature
                is not None
            ):
                lines.append(
                    "Radiative surroundings temperature: "
                    f"{surroundings_temperature:g} °C"
                )
 
        if (
            requirements.convection_mode
            == "forced"
            and thermal.air_velocity is not None
        ):
            lines.append(
                "Specified air velocity: "
                f"{thermal.air_velocity:g} m/s"
            )
 
        if (
            thermal.maximum_base_temperature
            is not None
        ):
            lines.append(
                "Maximum base temperature: "
                f"{thermal.maximum_base_temperature:g} °C"
            )
 
        return EngineeringReportSection(
            section_id="requirements",
            title="Design Requirements",
            content="\n".join(lines),
        )
 
    @staticmethod
    def _build_selected_design_section(
        *,
        selected,
        material_name: str,
        process_name: str,
    ) -> EngineeringReportSection:
 
        lines = [
            (
                "Material: "
                f"{material_name}"
            ),
            (
                "Manufacturing process: "
                f"{process_name}"
            ),
            (
                "Base thickness: "
                f"{selected.base_thickness:g} mm"
            ),
            (
                "Fin height: "
                f"{selected.fin_height:g} mm"
            ),
            (
                "Fin thickness: "
                f"{selected.fin_thickness:g} mm"
            ),
            (
                "Fin spacing: "
                f"{selected.fin_spacing:g} mm"
            ),
            (
                "Fin count: "
                f"{selected.fin_count}"
            ),
            (
                "Total height: "
                f"{selected.total_height:g} mm"
            ),
            (
                "Calculated mass: "
                f"{selected.mass:.4f} kg"
            ),
        ]
 
        if selected.has_material_cost:
            lines.extend(
                [
                    (
                        "Illustrative material cost: "
                        f"{selected.material_cost_currency} "
                        f"{selected.material_cost:.2f}"
                    ),
                    (
                        "Pricing basis: "
                        f"{selected.material_cost_result.pricing_basis}"
                    ),
                ]
            )
 
        return EngineeringReportSection(
            section_id="selected_design",
            title="Selected Design",
            content="\n".join(lines),
        )
 
    @staticmethod
    def _build_performance_section(
        selected,
        requirements,
    ) -> EngineeringReportSection:
 
        lines = [
            (
                "Nusselt number: "
                f"{selected.nusselt_number:.3f}"
            ),
        ]
 
        if requirements.convection_mode == "natural":
 
            lines.extend(
                [
                    (
                        "Convective heat-transfer coefficient: "
                        f"{selected.convective_heat_transfer_coefficient:.3f} "
                        "W/m²K"
                    ),
                    (
                        "Radiative heat-transfer coefficient: "
                        f"{selected.radiative_heat_transfer_coefficient:.3f} "
                        "W/m²K"
                    ),
                    (
                        "Effective heat-transfer coefficient: "
                        f"{selected.effective_heat_transfer_coefficient:.3f} "
                        "W/m²K"
                    ),
                ]
            )
 
        else:
 
            lines.append(
                (
                    "Heat-transfer coefficient: "
                    f"{selected.heat_transfer_coefficient:.3f} "
                    "W/m²K"
                )
            )
 
        lines.extend(
            [
                (
                    "Thermal resistance: "
                    f"{selected.thermal_resistance:.4f} °C/W"
                ),
                (
                    "Estimated base temperature: "
                    f"{selected.estimated_base_temperature:.2f} °C"
                ),
            ]
        )
 
        maximum_temperature = (
            requirements
            .requirements
            .maximum_base_temperature
        )
 
        if maximum_temperature is not None:
            margin = (
                maximum_temperature
                - selected.estimated_base_temperature
            )
 
            lines.append(
                "Temperature margin: "
                f"{margin:.2f} °C"
            )
 
        if requirements.convection_mode == "forced":
            lines.extend(
                [
                    (
                        "Reynolds number: "
                        f"{selected.reynolds_number:.0f}"
                    ),
                    (
                        "Pressure drop: "
                        f"{selected.pressure_drop:.3f} Pa"
                    ),
                    (
                        "Pumping power: "
                        f"{selected.pumping_power:.5f} W"
                    ),
                ]
            )
 
        return EngineeringReportSection(
            section_id="thermal_performance",
            title="Predicted Thermal Performance",
            content="\n".join(lines),
        )
 
    @staticmethod
    def _build_engineering_assessment_section(
        review,
    ) -> EngineeringReportSection:
 
        lines = [
            (
                "Overall status: "
                f"{review.status.value}"
            )
        ]
 
        for section in review.sections:
 
            lines.append(
                ""
            )
 
            lines.append(
                f"{section.category.value}: "
                f"{section.status.value}"
            )
 
            lines.append(
                section.summary
            )
 
        return EngineeringReportSection(
            section_id="engineering_assessment",
            title="Engineering Assessment",
            content="\n".join(lines),
        )
 
    @staticmethod
    def _build_recommendations_section(
        source,
    ) -> EngineeringReportSection:
 
        lines = []
 
        for index, recommendation in enumerate(
            source.recommendations,
            start=1,
        ):
 
            lines.append(
                (
                    f"{index}. "
                    f"{recommendation.title}"
                )
            )
 
            lines.append(
                (
                    "Priority: "
                    f"{recommendation.priority.value}"
                )
            )
 
            lines.append(
                recommendation.recommendation
            )
 
            lines.append("")
 
        content = "\n".join(lines).strip()
 
        return EngineeringReportSection(
            section_id="recommendations",
            title="Engineering Recommendations",
            content=content,
        )
 
    @staticmethod
    def _build_validation_section(
        review,
    ) -> EngineeringReportSection:
 
        lines = []
 
        for index, item in enumerate(
            review.validation_requirements,
            start=1,
        ):
            lines.append(
                f"{index}. {item.summary}"
            )
 
            if item.verification:
                lines.append(
                    "Verification: "
                    f"{item.verification}"
                )
 
            lines.append("")
 
        if not lines:
            lines.append(
                "No additional validation requirements "
                "were identified by the engineering review."
            )
 
        content = "\n".join(lines).strip()
 
        return EngineeringReportSection(
            section_id="validation",
            title="Validation Requirements",
            content=content,
        )