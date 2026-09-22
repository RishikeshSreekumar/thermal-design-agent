"""
End-to-end deterministic intelligence regression for
natural-convection optimization.
"""

import os
 
from core.engineering_review_service import (
    EngineeringReviewService,
)
from core.engineering_recommendation_service import (
    EngineeringRecommendationService,
)
from llm.factory import (
    get_llm_provider,
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
 
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
from core.engineering_report_builder import (
    EngineeringReportBuilder,
)
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Natural-convection requirements
    # --------------------------------------------------
 
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
    )
 
    # --------------------------------------------------
    # Optimization
    # --------------------------------------------------
 
    optimization_result = (
        ThermalOptimizer()
        .optimize_with_details(
            requirements
        )
    )
 
    assert optimization_result.has_feasible_design
 
    selected_candidate = (
        optimization_result.selected_candidate
    )
 
    assert selected_candidate is not None
 
    assert (
        selected_candidate.convection_mode
        == "natural"
    )
 
    # --------------------------------------------------
    # Engineering-intelligence pipeline
    # --------------------------------------------------
 
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
 
    pipeline = EngineeringIntelligencePipeline(
        assessment_engine=assessment_engine,
    )
 
    intelligence_result = pipeline.run(
        requirements=requirements,
        optimization_result=optimization_result,
        known_limitations=(
            (
                "Natural-convection predictions use "
                "reduced-order engineering correlations "
                "and require experimental or CFD validation "
                "before design release."
            ),
            (
                "Intermediate inclined orientations are "
                "not modeled. The current natural-convection "
                "model supports vertical, horizontal fins "
                "upward, and horizontal fins downward."
            ),
            (
                "The vertical natural-convection path "
                "uses the current Churchill-Chu-based "
                "reduced-order convection model."
            ),
            (
                "Thermal radiation is disabled for this "
                "analysis."
            ),
        ),
    )
 
    assert isinstance(
        intelligence_result,
        EngineeringIntelligenceResult,
    )
 
    # --------------------------------------------------
    # Natural convection must retain thermal evidence
    # --------------------------------------------------
 
    insight_ids = tuple(
        insight.insight_id
        for insight
        in intelligence_result.insights
    )
 
    assert (
        "thermal.selected_design_performance"
        in insight_ids
    )
 
    assert (
        "geometry.selected_design_dimensions"
        in insight_ids
    )
 
    assert (
        "optimization.selection_strategy"
        in insight_ids
    )
 
    # --------------------------------------------------
    # Forced-airflow evidence must not be fabricated
    # --------------------------------------------------
 
    assert (
        "airflow.selected_design_performance"
        not in insight_ids
    )
 
    assessment_ids = tuple(
        assessment.assessment_id
        for assessment
        in intelligence_result.assessments
    )
 
    assert not any(
        assessment_id.startswith(
            "airflow."
        )
        for assessment_id
        in assessment_ids
    )
 
    assert any(
        assessment_id.startswith(
            "thermal."
        )
        for assessment_id
        in assessment_ids
    )
 
    assert any(
        assessment_id.startswith(
            "manufacturing."
        )
        for assessment_id
        in assessment_ids
    )
 
    # --------------------------------------------------
    # Deterministic engineering review
    # --------------------------------------------------
 
    review_result = (
        EngineeringReviewService.build(
            intelligence_result,
            use_ai=False,
        )
    )
 
    assert review_result.review is not None
 
    review_categories = tuple(
        section.category.value
        for section
        in review_result.review.sections
    )
 
    assert "thermal" in review_categories
    assert "geometry" in review_categories
    assert "manufacturing" in review_categories
 
    assert "airflow" not in review_categories

    # --------------------------------------------------
    # Optional live-provider closure
    # --------------------------------------------------
 
    run_live_review = (
        os.getenv(
            "RUN_LIVE_LLM_REVIEW",
            "0",
        )
        == "1"
    )
 
    if run_live_review:
 
        provider = get_llm_provider()
 
        print()
        print(
            "LIVE NATURAL-CONVECTION PROVIDER:",
            provider.__class__.__name__,
        )
 
        # ----------------------------------------------
        # Grounded AI engineering review
        # ----------------------------------------------
 
        live_review_result = (
            EngineeringReviewService.build(
                intelligence_result,
                use_ai=True,
                provider=provider,
                fallback_to_deterministic=False,
            )
        )
 
        assert live_review_result.ai_requested
        assert live_review_result.ai_enriched
 
        live_review = live_review_result.review
 
        assert live_review is not None
 
        live_categories = tuple(
            section.category.value
            for section
            in live_review.sections
        )
 
        assert "thermal" in live_categories
        assert "geometry" in live_categories
        assert "manufacturing" in live_categories
 
        # Natural convection must not suddenly acquire
        # fabricated forced-airflow review content.
        assert "airflow" not in live_categories
 
        print()
        print("=" * 70)
        print(
            "LIVE NATURAL-CONVECTION "
            "ENGINEERING REVIEW"
        )
        print("=" * 70)
 
        print()
        print(
            "Deterministic status:",
            live_review.status.value,
        )
 
        print()
        print(
            "Executive summary:"
        )
        print(
            live_review.executive_summary
        )
 
        print()
        print(
            "Section summaries:"
        )
 
        for section in live_review.sections:
            print()
            print(
                f"[{section.category.value}]"
            )
            print(
                section.summary
            )
 
        # ----------------------------------------------
        # Grounded AI recommendations
        # ----------------------------------------------
 
        recommendation_result = (
            EngineeringRecommendationService.build(
                live_review_result,
                provider=provider,
            )
        )
 
        assert (
            recommendation_result.review_result
            is live_review_result
        )
 
        assert (
            recommendation_result
            .has_recommendations
        )
 
        print()
        print("=" * 70)
        print(
            "LIVE NATURAL-CONVECTION "
            "ENGINEERING RECOMMENDATIONS"
        )
        print("=" * 70)
 
        print()
        print(
            "Recommendation count:",
            recommendation_result
            .recommendation_count,
        )
 
        for index, recommendation in enumerate(
            recommendation_result.recommendations,
            start=1,
        ):
            print()
            print(
                f"{index}. {recommendation.title}"
            )
            print(
                " Type:",
                recommendation
                .recommendation_type.value,
            )
            print(
                " Priority:",
                recommendation.priority.value,
            )
            print(
                " Category:",
                recommendation.category.value,
            )
            print(
                " Recommendation:",
                recommendation.recommendation,
            )
            print(
                " Rationale:",
                recommendation.rationale,
            )

        # ----------------------------------------------
        # Engineering report
        # ----------------------------------------------
 
        report = (
            EngineeringReportBuilder.build(
                recommendation_result
            )
        )
 
        assert (
            report.source
            is recommendation_result
        )
 
        assert (
            report.status
            == live_review.status
        )
 
        assert report.has_recommendations
 
        assert (
            report.get_section(
                "requirements"
            )
        )
 
        assert (
            report.get_section(
                "selected_design"
            )
        )
 
        assert (
            report.get_section(
                "thermal_performance"
            )
        )
 
        assert (
            report.get_section(
                "engineering_assessment"
            )
        )
 
        assert (
            report.get_section(
                "recommendations"
            )
        )
 
        assert (
            report.get_section(
                "validation"
            )
        )
 
        # Natural-convection report must not fabricate
        # forced-flow performance.
        performance_content = (
            report.get_section(
                "thermal_performance"
            ).content
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
        print("=" * 70)
        print(
            "THERMAL DESIGN ENGINEERING REPORT"
        )
        print("=" * 70)
 
        print()
        print(
            "Status:",
            report.status.value,
        )
 
        print()
        print(
            "Executive Summary"
        )
        print(
            report.executive_summary
        )
 
        for section in report.sections:
 
            print()
            print(
                section.title.upper()
            )
            print("-" * len(section.title))
            print(
                section.content
            )
 
        print()
        print(
            "ALL REAL-WORKFLOW ENGINEERING "
            "REPORT CHECKS PASSED"
        )
 
        print()
        print(
            "ALL LIVE NATURAL-CONVECTION "
            "REVIEW AND RECOMMENDATION "
            "CHECKS PASSED"
        )

    
 
    print()
    print(
        "Natural-convection insight IDs:"
    )
 
    for insight_id in insight_ids:
        print("-", insight_id)
 
    print()
    print(
        "Natural-convection assessment IDs:"
    )
 
    for assessment_id in assessment_ids:
        print("-", assessment_id)
 
    print()
    print(
        "Deterministic review status:",
        review_result.review.status.value,
    )
 
    print(
        "ALL NATURAL CONVECTION INTELLIGENCE "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()