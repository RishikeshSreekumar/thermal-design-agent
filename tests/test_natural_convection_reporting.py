"""
End-to-end regression for natural-convection orientation
and radiation traceability through engineering intelligence
and the deterministic engineering report.
"""
 
import math
 
from core.engineering_report_builder import (
    EngineeringReportBuilder,
)
from core.engineering_review_service import (
    EngineeringReviewService,
)
from core.thermal_optimizer import (
    ThermalOptimizer,
)
 
from intelligence.engineering_assessment_engine import (
    EngineeringAssessmentEngine,
)
from intelligence.engineering_intelligence_pipeline import (
    EngineeringIntelligencePipeline,
)
from intelligence.evaluators.airflow_performance_evaluator import (
    AirflowPerformanceEvaluator,
)
from intelligence.evaluators.manufacturability_evaluator import (
    ManufacturabilityEvaluator,
)
from intelligence.evaluators.thermal_margin_evaluator import (
    ThermalMarginEvaluator,
)
 
from manufacturing.extrusion_capability import (
    AL6063_EXTRUSION,
)
 
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    NaturalConvectionSpecification,
    Requirements,
)
 
 
def main() -> None:
 
    requirements = EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="natural",
 
        requirements=Requirements(
            heat_load=20.0,
            ambient_temperature=30.0,
            maximum_base_temperature=120.0,
            air_velocity=None,
        ),
 
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=30.0,
        ),
 
        natural_convection=(
            NaturalConvectionSpecification(
                orientation="horizontal_fins_up",
                include_radiation=True,
                surface_emissivity=0.85,
                surroundings_temperature=30.0,
            )
        ),
    )
 
    optimization_result = (
        ThermalOptimizer()
        .optimize_with_details(
            requirements
        )
    )
 
    assert optimization_result.has_feasible_design
 
    selected = (
        optimization_result.selected_candidate
    )
 
    assert selected is not None
 
    assert (
        selected
        .radiative_heat_transfer_coefficient
        > 0.0
    )
 
    assessment_engine = (
        EngineeringAssessmentEngine(
            evaluators=(
                ManufacturabilityEvaluator(
                    capability=AL6063_EXTRUSION,
                ),
                ThermalMarginEvaluator(
                    warning_margin_temperature=10.0,
                ),
                AirflowPerformanceEvaluator(),
            )
        )
    )
 
    intelligence_result = (
        EngineeringIntelligencePipeline(
            assessment_engine=(
                assessment_engine
            )
        )
        .run(
            requirements=requirements,
            optimization_result=(
                optimization_result
            ),
            known_limitations=(
                (
                    "Horizontal plate-fin performance "
                    "uses an orientation-specific "
                    "reduced-order correlation."
                ),
                (
                    "Radiation uses a gray-diffuse "
                    "large-surroundings approximation."
                ),
            ),
        )
    )
 
    thermal_insight = next(
        insight
        for insight
        in intelligence_result.insights
        if (
            insight.insight_id
            == "thermal.selected_design_performance"
        )
    )
 
    evidence = {
        item.key: item.value
        for item in thermal_insight.evidence
    }
 
    assert (
        evidence[
            "natural_convection_orientation"
        ]
        == "horizontal_fins_up"
    )
 
    assert (
        evidence["radiation_enabled"]
        is True
    )
 
    assert math.isclose(
        evidence["surface_emissivity"],
        0.85,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        evidence[
            "convective_heat_transfer_coefficient"
        ],
        selected
        .convective_heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        evidence[
            "radiative_heat_transfer_coefficient"
        ],
        selected
        .radiative_heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        evidence[
            "effective_heat_transfer_coefficient"
        ],
        selected
        .effective_heat_transfer_coefficient,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    review_result = (
        EngineeringReviewService.build(
            intelligence_result,
            use_ai=False,
        )
    )
 
    recommendation_result = (
        EngineeringRecommendationResult(
            review_result=review_result,
            recommendations=(),
        )
    )
 
    report = EngineeringReportBuilder.build(
        recommendation_result
    )
 
    requirements_content = (
        report.get_section(
            "requirements"
        ).content
    )
 
    performance_content = (
        report.get_section(
            "thermal_performance"
        ).content
    )
 
    assert (
        "Natural-convection orientation: "
        "Horizontal — Fins Upward"
        in requirements_content
    )
 
    assert (
        "Thermal radiation: Included"
        in requirements_content
    )
 
    assert (
        "Surface emissivity: 0.85"
        in requirements_content
    )
 
    assert (
        "Radiative surroundings temperature: "
        "30 °C"
        in requirements_content
    )
 
    assert (
        "Convective heat-transfer coefficient:"
        in performance_content
    )
 
    assert (
        "Radiative heat-transfer coefficient:"
        in performance_content
    )
 
    assert (
        "Effective heat-transfer coefficient:"
        in performance_content
    )
 
    assert (
        "Reynolds number"
        not in performance_content
    )
 
    assert (
        "Pressure drop"
        not in performance_content
    )
 
    assert (
        "Pumping power"
        not in performance_content
    )
 
    print()
    print(requirements_content)
 
    print()
    print(performance_content)
 
    print()
 
    print(
        "ALL NATURAL-CONVECTION INTELLIGENCE "
        "AND REPORTING CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()