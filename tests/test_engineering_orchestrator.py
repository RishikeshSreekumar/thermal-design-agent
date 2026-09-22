"""
End-to-end regression for the Thermal Design Agent
engineering orchestrator.
"""

import os
 
from pathlib import Path
 
from core.engineering_orchestrator import (
    EngineeringOrchestrator,
)
 
from models.engineering_application_result import (
    EngineeringApplicationResult,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
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
    )
 
    result = EngineeringOrchestrator.run(
        requirements,
        use_ai=False,
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
        result,
        EngineeringApplicationResult,
    )
 
    # --------------------------------------------------
    # Optimization
    # --------------------------------------------------
 
    assert (
        result.optimization_result
        .has_feasible_design
    )
 
    assert result.selected_candidate is not None
 
    assert (
        result.selected_candidate
        .convection_mode
        == "natural"
    )
 
    # --------------------------------------------------
    # Intelligence
    # --------------------------------------------------
 
    assert (
        result.intelligence_result
        .has_insights
    )
 
    assert (
        result.intelligence_result
        .has_assessments
    )
 
    # --------------------------------------------------
    # Review
    # --------------------------------------------------
 
    assert not result.has_ai_review
 
    assert (
        result.review_result.review
        is result.review_result
        .deterministic_review
    )
 
    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------
 
    assert not result.has_recommendations
 
    # --------------------------------------------------
    # Report
    # --------------------------------------------------
 
    assert (
        result.report.source
        is result.recommendation_result
    )
 
    assert (
        result.report.status
        == result.engineering_status
    )
 
    assert (
        result.report.get_section(
            "requirements"
        )
    )
 
    assert (
        result.report.get_section(
            "selected_design"
        )
    )
 
    assert (
        result.report.get_section(
            "thermal_performance"
        )
    )
 
    # --------------------------------------------------
    # Geometry / CAD
    # --------------------------------------------------
 
    assert result.geometry.fin_count > 0
 
    assert isinstance(
        result.step_file,
        Path,
    )
 
    assert result.step_file.is_file()
 
    assert (
        result.step_file.suffix.lower()
        == ".step"
    )
 
    # --------------------------------------------------
    # Traceability
    # --------------------------------------------------
 
    assert (
        result.intelligence_result
        .context
        .requirements
        is requirements
    )
 
    assert (
        result.review_result
        .source
        .intelligence_result
        is result.intelligence_result
    )
 
    assert (
        result.recommendation_result
        .review_result
        is result.review_result
    )

    # --------------------------------------------------
    # Forced-Convection End-to-End Regression
    # --------------------------------------------------
 
    forced_requirements = (
        EngineeringRequirements(
            component_type="heat_sink",
            convection_mode="forced",
 
            requirements=Requirements(
                heat_load=165.0,
                ambient_temperature=30.0,
                air_velocity=5.0,
            ),
 
            constraints=Constraints(
                base_length=50.0,
                base_width=50.0,
                max_height=30.0,
            ),
        )
    )
 
    forced_result = (
        EngineeringOrchestrator.run(
            forced_requirements,
            use_ai=False,
        )
    )
 
    assert isinstance(
        forced_result,
        EngineeringApplicationResult,
    )
 
    assert (
        forced_result
        .optimization_result
        .has_feasible_design
    )
 
    assert (
        forced_result.selected_candidate
        is not None
    )
 
    assert (
        forced_result
        .selected_candidate
        .convection_mode
        == "forced"
    )
 
    assert (
        forced_result
        .selected_candidate
        .approach_velocity
        > 0.0
    )
 
    assert (
        forced_result
        .selected_candidate
        .channel_velocity
        > 0.0
    )
 
    assert (
        forced_result
        .selected_candidate
        .pressure_drop
        >= 0.0
    )
 
    assert (
        forced_result
        .selected_candidate
        .pumping_power
        >= 0.0
    )
 
    assert (
        forced_result
        .intelligence_result
        .has_insights
    )
 
    assert (
        forced_result
        .intelligence_result
        .has_assessments
    )
 
    assert not (
        forced_result.has_ai_review
    )
 
    assert not (
        forced_result.has_recommendations
    )
 
    assert (
        forced_result.report.status
        == forced_result.engineering_status
    )
 
    assert (
        forced_result.step_file.is_file()
    )
 
    assert (
        forced_result.step_file.suffix.lower()
        == ".step"
    )
 
    assert (
        forced_result
        .intelligence_result
        .context
        .requirements
        is forced_requirements
    )
 
    assert (
        forced_result
        .recommendation_result
        .review_result
        is forced_result.review_result
    )
 
    print()
    print(
        "FORCED-CONVECTION ENGINEERING "
        "ORCHESTRATOR CHECKS PASSED"
    )
 
    print()
    print(
        "Selected geometry:",
        (
            result.selected_candidate
            .base_thickness,
            result.selected_candidate
            .fin_height,
            result.selected_candidate
            .fin_thickness,
            result.selected_candidate
            .fin_spacing,
            result.selected_candidate
            .fin_count,
        ),
    )
 
    print(
        "Engineering status:",
        result.engineering_status.value,
    )
 
    print(
        "Report sections:",
        result.report.section_count,
    )
 
    print(
        "STEP file:",
        result.step_file,
    )

    # --------------------------------------------------
    # Optional live-provider orchestration regression
    # --------------------------------------------------
 
    run_live_review = (
        os.getenv(
            "RUN_LIVE_LLM_REVIEW",
            "0",
        )
        == "1"
    )
 
    if run_live_review:
 
        live_result = (
            EngineeringOrchestrator.run(
                requirements,
                use_ai=True,
                fallback_to_deterministic=False,
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
        )
 
        assert live_result.has_ai_review
 
        assert (
            live_result.recommendation_result
            .has_recommendations
        )
 
        assert (
            live_result.report
            .has_recommendations
        )
 
        assert (
            live_result.report.status
            == live_result.engineering_status
        )
 
        assert (
            live_result.step_file.is_file()
        )
 
        print()
        print(
            "LIVE ENGINEERING ORCHESTRATOR "
            "CHECKS PASSED"
        )
 
    print()
    print(
        "ALL ENGINEERING ORCHESTRATOR "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()