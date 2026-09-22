"""
Focused regression for the Engineering Report model.
"""
from pathlib import Path
 
from core.engineering_report_html_renderer import (
    EngineeringReportHTMLRenderer,
)

from models.engineering_report import (
    EngineeringReport,
    EngineeringReportSection,
)
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
 
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
 
from core.thermal_optimizer import (
    ThermalOptimizer,
)
from intelligence.context_builder import (
    EngineeringContextBuilder,
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
 
    requirements = EngineeringRequirements(
        component_type="heat_sink",
        convection_mode="natural",
 
        requirements=Requirements(
            heat_load=20.0,
            ambient_temperature=30.0,
            air_velocity=None,
        ),
 
        constraints=Constraints(
            base_length=50.0,
            base_width=50.0,
            max_height=30.0,
        ),
    )
 
    optimization_result = (
        ThermalOptimizer()
        .optimize_with_details(
            requirements
        )
    )
 
    context = (
        EngineeringContextBuilder.build(
            requirements=requirements,
            optimization_result=(
                optimization_result
            ),
            known_limitations=(),
        )
    )
 
    assert isinstance(
        context,
        EngineeringContext,
    )
 
    intelligence_result = (
        EngineeringIntelligenceResult(
            context=context,
            insights=(),
            assessments=(),
        )
    )
 
    source = EngineeringReviewSource(
        intelligence_result=(
            intelligence_result
        ),
        insight_index={},
        assessment_index={},
        assessed_insight_ids=(),
        unassessed_insight_ids=(),
    )
 
    review = EngineeringReview(
        status=(
            EngineeringReviewStatus
            .INSUFFICIENT_EVIDENCE
        ),
        executive_summary=(
            "Engineering review completed."
        ),
        strengths=(),
        concerns=(),
        sections=(),
        tradeoffs=(),
        required_actions=(),
        validation_requirements=(),
        source_assessment_ids=(),
        source_insight_ids=(),
    )
 
    review_result = EngineeringReviewResult(
        source=source,
        deterministic_review=review,
        review=review,
        ai_requested=False,
        ai_enriched=False,
    )
 
    recommendation_result = (
        EngineeringRecommendationResult(
            review_result=review_result,
            recommendations=(),
        )
    )
 
    sections = (
        EngineeringReportSection(
            section_id="requirements",
            title="Design Requirements",
            content=(
                "Natural-convection plate-fin "
                "heat-sink design."
            ),
        ),
        EngineeringReportSection(
            section_id="selected_design",
            title="Selected Design",
            content=(
                "Selected design information."
            ),
        ),
    )
 
    report = EngineeringReport(
        source=recommendation_result,
        title="Thermal Design Engineering Report",
        executive_summary=(
            "Structured engineering report."
        ),
        status=(
            EngineeringReviewStatus
            .INSUFFICIENT_EVIDENCE
        ),
        sections=sections,
    )
 
    assert (
        report.source
        is recommendation_result
    )
 
    assert report.section_count == 2
 
    assert not report.has_recommendations
 
    assert (
        report.get_section(
            "requirements"
        )
        is sections[0]
    )
 
    assert (
        report.status
        == review_result.review.status
    )
 
    try:
        EngineeringReport(
            source=recommendation_result,
            title="Invalid Report",
            executive_summary="Invalid status.",
            status=(
                EngineeringReviewStatus
                .ACCEPTABLE
            ),
            sections=sections,
        )
 
    except ValueError as error:
        assert (
            "status must match"
            in str(error)
        )
 
    else:
        raise AssertionError(
            "Report accepted a status that differed "
            "from the authoritative review."
        )

    # --------------------------------------------------
    # Deterministic report builder
    # --------------------------------------------------
 
    built_report = (
        EngineeringReportBuilder.build(
            recommendation_result
        )
    )
 
    assert isinstance(
        built_report,
        EngineeringReport,
    )
 
    assert (
        built_report.source
        is recommendation_result
    )
 
    assert (
        built_report.status
        == review.status
    )
 
    assert (
        built_report.title
        == "Thermal Design Engineering Report"
    )
 
    assert (
        built_report.get_section(
            "requirements"
        )
    )
 
    assert (
        built_report.get_section(
            "selected_design"
        )
    )
 
    assert (
        built_report.get_section(
            "thermal_performance"
        )
    )
 
    assert (
        built_report.get_section(
            "engineering_assessment"
        )
    )
 
    assert (
        built_report.get_section(
            "validation"
        )
    )
 
    assert not built_report.has_recommendations

    # --------------------------------------------------
    # Professional HTML renderer
    # --------------------------------------------------
 
    rendered_html = (
        EngineeringReportHTMLRenderer.render(
            built_report,
            logo_path="assets/havells_logo.png",
        )
    )
 
    assert (
        "<!DOCTYPE html>"
        in rendered_html
    )
 
    assert (
        "Thermal Design Agent"
        in rendered_html
    )
 
    assert (
        'alt="Havells"'
        in rendered_html
    )
    
    assert (
        "data:image/png;base64,"
        in rendered_html
    )
 
    assert (
        "Thermal Design Engineering Report"
        in rendered_html
    )
 
    assert (
        "INSUFFICIENT EVIDENCE"
        in rendered_html
    )
 
    # User-facing report must not contain the old
    # prototype product identity or decorative emoji.
    assert (
        "Thermal AI Engineer"
        not in rendered_html
    )
 
    assert "🔥" not in rendered_html
    assert "🚀" not in rendered_html
    assert "🤖" not in rendered_html
 
    # HTML output must escape report content.
    escaped_section = EngineeringReportSection(
        section_id="escape_test",
        title="Escape Test",
        content="<script>alert('test')</script>",
    )
 
    escaped_report = EngineeringReport(
        source=recommendation_result,
        title="Escape Test Report",
        executive_summary=(
            "Safe <engineering> report."
        ),
        status=review.status,
        sections=(
            escaped_section,
        ),
    )
 
    escaped_html = (
        EngineeringReportHTMLRenderer.render(
            escaped_report
        )
    )
 
    assert "<script>" not in escaped_html
 
    assert (
        "&lt;script&gt;"
        in escaped_html
    )
 
    # --------------------------------------------------
    # HTML export
    # --------------------------------------------------
 
    output_path = Path(
        "generated"
    ) / "test_engineering_report.html"
 
    exported_path = (
        EngineeringReportHTMLRenderer.export(
            built_report,
            output_path,
            logo_path="assets/havells_logo.png",
        )
    )
 
    assert exported_path == output_path
    assert exported_path.is_file()
 
    exported_content = (
        exported_path.read_text(
            encoding="utf-8"
        )
    )
 
    assert (
        exported_content
        == rendered_html
    )
 
    print(
        "ALL ENGINEERING REPORT MODEL, BUILDER, "
        "AND HTML RENDERER CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()