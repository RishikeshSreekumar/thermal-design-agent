"""
Focused regression checks for the engineering-review
source package and builder.
 
The fixture deliberately uses the existing deterministic
EngineeringIntelligencePipeline rather than manually
constructing an EngineeringIntelligenceResult.
 
This keeps the review layer connected to the real
engineering-intelligence architecture.
"""
import os
from datetime import date
 
from llm.factory import (
    get_llm_provider,
)
  
from dataclasses import replace
 
from core.engineering_review_source_builder import (
    EngineeringReviewSourceBuilder,
)
from core.engineering_review_structure_synthesizer import (
    EngineeringReviewStructureSynthesizer,
)
from core.engineering_review_synthesizer import (
    EngineeringReviewSynthesizer,
)
from core.engineering_review_status_resolver import (
    EngineeringReviewStatusResolver,
)
from core.engineering_review_ai_synthesizer import (
    EngineeringReviewAISynthesizer,
)
from core.engineering_recommendation_service import (
    EngineeringRecommendationService,
)
from core.engineering_review_service import (
    EngineeringReviewService,
)
from core.engineering_recommendation_ai_synthesizer import (
    EngineeringRecommendationAISynthesizer,
)
from models.engineering_recommendation import (
    EngineeringRecommendation,
)
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from llm.base import (
    LLMProvider,
)
from llm.engineering_review_payload import (
    EngineeringReviewPayloadBuilder,
)
from models.engineering_review_result import (
    EngineeringReviewResult,
)
from llm.engineering_review_parser import (
    EngineeringReviewAIParser,
)
from llm.mock_provider import (
    MockProvider,
)
from llm.engineering_recommendation_payload import (
    EngineeringRecommendationPayloadBuilder,
)
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
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
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
from models.optimization_result import (
    OptimizationResult,
)
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.requirements import (
    Constraints,
    EngineeringRequirements,
    Requirements,
)
 
 
def expect_value_error(
    action,
    expected_message: str,
) -> None:
    """
    Confirm that an action raises the expected validation
    error.
    """
 
    try:
        action()
 
    except ValueError as error:
        assert expected_message in str(error)
 
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
 
 
def expect_key_error(
    action,
    expected_message: str,
) -> None:
    """
    Confirm that an action raises the expected lookup
    error.
    """
 
    try:
        action()
 
    except KeyError as error:
        assert expected_message in str(error)
 
    else:
        raise AssertionError(
            "Expected KeyError was not raised."
        )
 
class FailingReviewProvider(
    LLMProvider
):
    """
    Provider fixture used to verify deterministic fallback.
    """
 
    def extract_requirements(
        self,
        user_prompt: str,
    ) -> dict:
        return {}
 
    def synthesize_engineering_review(
        self,
        payload: dict,
    ) -> dict:
        raise RuntimeError(
            "Simulated review-provider failure."
        )

    def synthesize_engineering_recommendations(
        self,
        payload: dict,
    ) -> dict:
        return {
            "recommendations": []
        }

class FailingRecommendationProvider(
    LLMProvider
):
    """
    Provider fixture used to verify safe recommendation
    fallback.
    """
    def extract_requirements(
        self,
        user_prompt: str,
    ) -> dict:
        return {}
    def synthesize_engineering_review(
        self,
        payload: dict,
    ) -> dict:
        return {
            "executive_summary": "Unused test synthesis.",
            "section_summaries": [],
            "tradeoffs": [],
        }
    def synthesize_engineering_recommendations(
        self,
        payload: dict,
    ) -> dict:
        raise RuntimeError(
            "Simulated recommendation-provider failure."
        )    
 
# --------------------------------------------------
# Existing deterministic engineering fixture
# --------------------------------------------------
 
candidate = DesignCandidate(
    base_thickness=3.0,
    fin_thickness=1.0,
    fin_height=8.0,
    fin_spacing=3.0,
    fin_count=12,
    total_height=11.0,
 
    gross_frontal_area=0.0014,
    open_flow_area=0.0010,
    blockage_ratio=0.2857,
    approach_velocity=3.0,
    channel_velocity=4.2,
 
    reynolds_number=2500.0,
    nusselt_number=8.5,
    heat_transfer_coefficient=45.0,
 
    friction_factor=0.04,
    pressure_drop=18.0,
    pumping_power=0.0756,
 
    thermal_resistance=0.42,
    estimated_base_temperature=99.3,
)
 
selection_configuration = (
    OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE
        )
    )
)
 
selection_result = CandidateSelectionResult(
    configuration=selection_configuration,
    selected_candidates=(
        candidate,
    ),
)
 
optimization_result = OptimizationResult(
    best_result=None,
    candidates=[
        candidate,
    ],
    feasible_candidate_count=1,
    rejected_candidate_count=3,
    selected_material="Al6063",
    selected_process="extrusion",
    selection_result=selection_result,
)
 
requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
    requirements=Requirements(
        heat_load=165.0,
        ambient_temperature=30.0,
        maximum_base_temperature=105.0,
        maximum_pressure_drop=25.0,
        maximum_pumping_power=0.10,
        air_velocity=5.0,
    ),
    constraints=Constraints(
        base_length=50.0,
        base_width=50.0,
        max_height=30.0,
    ),
)
 
known_limitations = (
    "Radiation heat transfer is not yet included.",
    "Fan accuracy depends on the supplied fan curve.",
)
 
 
# --------------------------------------------------
# Use the real deterministic intelligence pipeline
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
    known_limitations=known_limitations,
)
 
assert isinstance(
    intelligence_result,
    EngineeringIntelligenceResult,
)
 
assert intelligence_result.has_insights
 
assert intelligence_result.has_assessments
 
 
# --------------------------------------------------
# Build Step 34 review source
# --------------------------------------------------
 
source = (
    EngineeringReviewSourceBuilder.build(
        intelligence_result
    )
)
 
 
# --------------------------------------------------
# Complete aggregate preservation
# --------------------------------------------------
 
assert (
    source.intelligence_result
    is intelligence_result
)
 
assert (
    source.context
    is intelligence_result.context
)
 
assert (
    source.insights
    is intelligence_result.insights
)
 
assert (
    source.assessments
    is intelligence_result.assessments
)
 
 
# --------------------------------------------------
# Complete source population preserved
# --------------------------------------------------
 
assert len(
    source.insight_index
) == len(
    intelligence_result.insights
)
 
assert len(
    source.assessment_index
) == len(
    intelligence_result.assessments
)
 
assert tuple(
    source.insight_index
) == tuple(
    insight.insight_id
    for insight
    in intelligence_result.insights
)
 
assert tuple(
    source.assessment_index
) == tuple(
    assessment.assessment_id
    for assessment
    in intelligence_result.assessments
)
 
 
# --------------------------------------------------
# Stable lookup
# --------------------------------------------------
 
for insight in intelligence_result.insights:
    assert (
        source.get_insight(
            insight.insight_id
        )
        is insight
    )
 
for assessment in (
    intelligence_result.assessments
):
    assert (
        source.get_assessment(
            assessment.assessment_id
        )
        is assessment
    )
 
 
# --------------------------------------------------
# Assessment state preservation
# --------------------------------------------------
 
assert (
    source.passed_assessments
    == intelligence_result.passed_assessments
)
 
assert (
    source.failed_assessments
    == intelligence_result.failed_assessments
)
 
assert (
    source.has_failed_assessments
    == bool(
        intelligence_result.failed_assessments
    )
)
 
 
# --------------------------------------------------
# Assessed/unassessed insight partition
# --------------------------------------------------
 
all_source_insight_ids = {
    insight.insight_id
    for insight
    in intelligence_result.insights
}
 
assessed_id_set = set(
    source.assessed_insight_ids
)
 
unassessed_id_set = set(
    source.unassessed_insight_ids
)
 
assert not (
    assessed_id_set
    & unassessed_id_set
)
 
assert (
    assessed_id_set
    | unassessed_id_set
) == all_source_insight_ids
 
assert (
    len(source.assessed_insights)
    == len(source.assessed_insight_ids)
)
 
assert (
    len(source.unassessed_insights)
    == len(source.unassessed_insight_ids)
)
 
assert (
    source.has_unassessed_insights
    == bool(
        source.unassessed_insight_ids
    )
)
 
 
# --------------------------------------------------
# Existing unassessed intelligence remains available
# --------------------------------------------------
 
optimization_insights = (
    source.insights_for_category(
        EngineeringCategory.OPTIMIZATION
    )
)
 
assert optimization_insights
 
assert all(
    insight.category
    == EngineeringCategory.OPTIMIZATION
    for insight in optimization_insights
)
 
limitation_insights = (
    source.insights_for_category(
        EngineeringCategory.MODEL_LIMITATION
    )
)
 
assert len(
    limitation_insights
) == len(
    known_limitations
)
 
assert all(
    insight.insight_id
    in source.unassessed_insight_ids
    for insight in limitation_insights
)
 
 
# --------------------------------------------------
# Category access
# --------------------------------------------------
 
thermal_insights = (
    source.insights_for_category(
        EngineeringCategory.THERMAL
    )
)
 
thermal_assessments = (
    source.assessments_for_category(
        EngineeringCategory.THERMAL
    )
)
 
assert thermal_insights
 
assert thermal_assessments
 
assert all(
    insight.category
    == EngineeringCategory.THERMAL
    for insight in thermal_insights
)
 
assert all(
    assessment.category
    == EngineeringCategory.THERMAL
    for assessment in thermal_assessments
)
 
 
# --------------------------------------------------
# Severity access
# --------------------------------------------------
 
warning_insights = (
    source.insights_for_severity(
        EngineeringSeverity.WARNING
    )
)
 
warning_assessments = (
    source.assessments_for_severity(
        EngineeringSeverity.WARNING
    )
)
 
assert all(
    insight.severity
    == EngineeringSeverity.WARNING
    for insight in warning_insights
)
 
assert all(
    assessment.severity
    == EngineeringSeverity.WARNING
    for assessment in warning_assessments
)
 
 
# --------------------------------------------------
# Assessment-to-insight traceability
# --------------------------------------------------
 
for assessment in source.assessments:
    resolved_insights = (
        source.source_insights_for_assessment(
            assessment.assessment_id
        )
    )
 
    assert tuple(
        insight.insight_id
        for insight in resolved_insights
    ) == assessment.source_insight_ids
 
 
# --------------------------------------------------
# Lookup protection
# --------------------------------------------------
 
expect_key_error(
    lambda: source.get_insight(
        "unknown.insight"
    ),
    "Unknown engineering insight ID",
)
 
expect_key_error(
    lambda: source.get_assessment(
        "unknown.assessment"
    ),
    "Unknown engineering assessment ID",
)
 
# --------------------------------------------------
# Duplicate assessment-ID protection
# --------------------------------------------------
 
first_assessment = (
    intelligence_result.assessments[0]
)
 
second_assessment = (
    intelligence_result.assessments[1]
)
 
duplicate_assessment = replace(
    second_assessment,
    assessment_id=(
        first_assessment.assessment_id
    ),
)
 
duplicate_assessment_result = (
    EngineeringIntelligenceResult(
        context=(
            intelligence_result.context
        ),
        insights=(
            intelligence_result.insights
        ),
        assessments=(
            first_assessment,
            duplicate_assessment,
        ),
    )
)
 
expect_value_error(
    lambda: (
        EngineeringReviewSourceBuilder.build(
            duplicate_assessment_result
        )
    ),
    "Duplicate engineering assessment ID",
)
 
 
# --------------------------------------------------
# Unknown assessment-source protection
# --------------------------------------------------
 
invalid_reference_assessment = replace(
    first_assessment,
    assessment_id=(
        "assessment.invalid.reference"
    ),
    source_insight_ids=(
        "insight.does.not.exist",
    ),
)
 
invalid_reference_result = (
    EngineeringIntelligenceResult(
        context=(
            intelligence_result.context
        ),
        insights=(
            intelligence_result.insights
        ),
        assessments=(
            invalid_reference_assessment,
        ),
    )
)
 
expect_value_error(
    lambda: (
        EngineeringReviewSourceBuilder.build(
            invalid_reference_result
        )
    ),
    "references unknown insight ID",
)
 
 
# --------------------------------------------------
# Partition-integrity protection
# --------------------------------------------------
 
all_insights = (
    intelligence_result.insights
)
 
first_source_id = (
    all_insights[0].insight_id
)
 
expect_value_error(
    lambda: EngineeringReviewSource(
        intelligence_result=(
            intelligence_result
        ),
        insight_index={
            insight.insight_id: insight
            for insight
            in intelligence_result.insights
        },
        assessment_index={
            assessment.assessment_id: assessment
            for assessment
            in intelligence_result.assessments
        },
        assessed_insight_ids=(
            first_source_id,
        ),
        unassessed_insight_ids=(),
    ),
    "must together contain every source insight",
)
 
 
print(
    "ALL ENGINEERING REVIEW SOURCE CHECKS PASSED"
)


# --------------------------------------------------
# Step 34.3B — Structured review synthesis
# --------------------------------------------------
 
components = (
    EngineeringReviewStructureSynthesizer
    .synthesize(
        source
    )
)
 
 
# --------------------------------------------------
# Review components are populated
# --------------------------------------------------
 
assert components.sections
 
assert (
    len(components.sections)
    > 0
)
 
 
# --------------------------------------------------
# Strengths are true deterministic successes
# --------------------------------------------------
 
for strength in components.strengths:
    assert (
        strength.severity
        == EngineeringSeverity.SUCCESS
    )
 
    assert strength.is_traceable
 
 
# --------------------------------------------------
# Concerns preserve deterministic attention signals
# --------------------------------------------------
 
for concern in components.concerns:
    assert concern.is_traceable
 
    if concern.source_assessment_ids:
        assessment = source.get_assessment(
            concern.source_assessment_ids[0]
        )
 
        assert (
            not assessment.passed
            or assessment.severity
            in {
                EngineeringSeverity.WARNING,
                EngineeringSeverity.CRITICAL,
            }
        )
 
 
# --------------------------------------------------
# Category sections preserve complete source coverage
# --------------------------------------------------
 
section_categories = {
    section.category
    for section in components.sections
}
 
source_categories = {
    insight.category
    for insight in source.insights
} | {
    assessment.category
    for assessment in source.assessments
}
 
assert (
    section_categories
    == source_categories
)
 
 
# --------------------------------------------------
# Every section source ID resolves
# --------------------------------------------------
 
for section in components.sections:
 
    assert isinstance(
        section.status,
        EngineeringReviewStatus,
    )
 
    assert section.summary.strip()
 
    for assessment_id in (
        section.source_assessment_ids
    ):
        assessment = source.get_assessment(
            assessment_id
        )
 
        assert (
            assessment.category
            == section.category
        )
 
    for insight_id in (
        section.source_insight_ids
    ):
        insight = source.get_insight(
            insight_id
        )
 
        assert (
            insight.category
            == section.category
        )
 
    for finding in section.findings:
        assert (
            finding.category
            == section.category
        )
 
        assert finding.is_traceable
 
 
# --------------------------------------------------
# Deterministic recommendations are preserved
# --------------------------------------------------
 
for action in components.required_actions:
 
    assert action.source_assessment_ids
 
    assessment = source.get_assessment(
        action.source_assessment_ids[0]
    )
 
    assert assessment.has_recommendation
 
    assert (
        action.summary
        == assessment.recommendation
    )
 
 
# --------------------------------------------------
# Failed INFO recommendations become validation needs
# --------------------------------------------------
 
expected_info_validation_ids = {
    assessment.assessment_id
    for assessment in source.assessments
    if (
        not assessment.passed
        and assessment.severity
        == EngineeringSeverity.INFO
        and assessment.has_recommendation
    )
}
 
actual_info_validation_ids = {
    assessment_id
    for item
    in components.validation_requirements
    for assessment_id
    in item.source_assessment_ids
}
 
assert (
    expected_info_validation_ids
    <= actual_info_validation_ids
)
 
 
# --------------------------------------------------
# Model limitations remain explicit validation needs
# --------------------------------------------------
 
model_limitation_ids = {
    insight.insight_id
    for insight in source.unassessed_insights
    if (
        insight.category
        == EngineeringCategory.MODEL_LIMITATION
    )
}
 
validation_insight_ids = {
    insight_id
    for item
    in components.validation_requirements
    for insight_id
    in item.source_insight_ids
}
 
assert (
    model_limitation_ids
    <= validation_insight_ids
)
 
 
# --------------------------------------------------
# No deterministic source is invented
# --------------------------------------------------
 
for collection in (
    components.strengths,
    components.concerns,
    components.required_actions,
    components.validation_requirements,
):
 
    for item in collection:
 
        for assessment_id in (
            item.source_assessment_ids
        ):
            assert (
                assessment_id
                in source.assessment_index
            )
 
        for insight_id in (
            item.source_insight_ids
        ):
            assert (
                insight_id
                in source.insight_index
            )
 
 
# --------------------------------------------------
# Input contract protection
# --------------------------------------------------
 
expect_value_error(
    lambda: (
        EngineeringReviewStructureSynthesizer
        .synthesize(
            "invalid"
        )
    ),
    "'source' must be an "
    "EngineeringReviewSource object",
)
 
 
print(
    "ALL ENGINEERING REVIEW STRUCTURE CHECKS PASSED"
)

# --------------------------------------------------
# Complete deterministic review
# --------------------------------------------------
 
review = (
    EngineeringReviewSynthesizer
    .synthesize(
        source
    )
)
 
assert isinstance(
    review,
    EngineeringReview,
)
 
assert isinstance(
    review.status,
    EngineeringReviewStatus,
)
 
assert review.executive_summary.strip()
 
assert (
    review.strengths
    == components.strengths
)
 
assert (
    review.concerns
    == components.concerns
)
 
assert (
    review.sections
    == components.sections
)
 
assert (
    review.required_actions
    == components.required_actions
)
 
assert (
    review.validation_requirements
    == components.validation_requirements
)
 
 
# --------------------------------------------------
# Complete deterministic traceability is preserved
# --------------------------------------------------
 
assert (
    review.source_assessment_ids
    == tuple(
        assessment.assessment_id
        for assessment
        in source.assessments
    )
)
 
assert (
    review.source_insight_ids
    == tuple(
        insight.insight_id
        for insight
        in source.insights
    )
)
 
 
# --------------------------------------------------
# Every review source resolves to the original source
# --------------------------------------------------
 
for assessment_id in (
    review.source_assessment_ids
):
    assert (
        source.get_assessment(
            assessment_id
        )
        is source.assessment_index[
            assessment_id
        ]
    )
 
for insight_id in (
    review.source_insight_ids
):
    assert (
        source.get_insight(
            insight_id
        )
        is source.insight_index[
            insight_id
        ]
    )
 
 
# --------------------------------------------------
# Deterministic review does not invent trade-offs
# --------------------------------------------------
 
assert review.tradeoffs == ()
 
 
# --------------------------------------------------
# Overall status remains assessment-driven
# --------------------------------------------------
 
resolved_status = (
    EngineeringReviewStatusResolver
    .resolve(
        source.assessments
    )
)
 
if (
    resolved_status
    == EngineeringReviewStatus.ACCEPTABLE
    and review.validation_requirements
):
    expected_status = (
        EngineeringReviewStatus
        .ACCEPTABLE_WITH_ACTIONS
    )
 
else:
    expected_status = resolved_status
 
assert review.status == expected_status
 
 
# --------------------------------------------------
# Executive summary reports actual source counts
# --------------------------------------------------
 
assert (
    str(len(source.insights))
    in review.executive_summary
)
 
assert (
    str(len(source.assessments))
    in review.executive_summary
)
 
 
# --------------------------------------------------
# Input contract protection
# --------------------------------------------------
 
expect_value_error(
    lambda: (
        EngineeringReviewSynthesizer
        .synthesize(
            "invalid"
        )
    ),
    "'source' must be an "
    "EngineeringReviewSource object",
)

# --------------------------------------------------
# Grounded AI review synthesis
# --------------------------------------------------
 
mock_provider = MockProvider()
 
ai_review = (
    EngineeringReviewAISynthesizer
    .synthesize(
        source=source,
        deterministic_review=review,
        provider=mock_provider,
    )
)
 
 
# AI improves communication.
assert (
    ai_review.executive_summary
    != review.executive_summary
)
 
assert ai_review.executive_summary.startswith(
    "AI synthesis:"
)
 
 
# --------------------------------------------------
# Deterministic authority remains locked
# --------------------------------------------------
 
assert ai_review.status == review.status
 
assert (
    ai_review.strengths
    == review.strengths
)
 
assert (
    ai_review.concerns
    == review.concerns
)
 
assert (
    ai_review.required_actions
    == review.required_actions
)
 
assert (
    ai_review.validation_requirements
    == review.validation_requirements
)
 
assert (
    ai_review.source_assessment_ids
    == review.source_assessment_ids
)
 
assert (
    ai_review.source_insight_ids
    == review.source_insight_ids
)
 
 
# --------------------------------------------------
# AI section summaries may improve communication
# --------------------------------------------------
 
assert (
    len(ai_review.sections)
    == len(review.sections)
)
 
for original_section, ai_section in zip(
    review.sections,
    ai_review.sections,
):
    assert (
        ai_section.category
        == original_section.category
    )
 
    assert (
        ai_section.status
        == original_section.status
    )
 
    assert (
        ai_section.findings
        == original_section.findings
    )
 
    assert (
        ai_section.source_assessment_ids
        == original_section.source_assessment_ids
    )
 
    assert (
        ai_section.source_insight_ids
        == original_section.source_insight_ids
    )
 
    assert ai_section.summary.startswith(
        "AI synthesis:"
    )
 
 
# --------------------------------------------------
# Mock does not invent engineering trade-offs
# --------------------------------------------------
 
assert ai_review.tradeoffs == ()
 
 
# --------------------------------------------------
# Unknown source IDs from an LLM are rejected
# --------------------------------------------------
 
available_categories = [
    section.category.value
    for section in review.sections
]
 
assert available_categories
 
invalid_ai_response = {
    "executive_summary": (
        "Invalid grounded response test."
    ),
    "section_summaries": [],
    "tradeoffs": [
        {
            "tradeoff_id": (
                "ai.tradeoff.invalid"
            ),
            "title": (
                "Unsupported trade-off"
            ),
            "severity": "warning",
            "categories": (
                available_categories[:2]
                if len(available_categories) >= 2
                else [
                    available_categories[0],
                    available_categories[0],
                ]
            ),
            "benefit": "Unsupported benefit.",
            "penalty": "Unsupported penalty.",
            "guidance": "",
            "source_assessment_ids": [
                "assessment.does.not.exist"
            ],
            "source_insight_ids": [],
        }
    ],
}
 
expect_value_error(
    lambda: (
        EngineeringReviewAIParser.parse(
            data=invalid_ai_response,
            source=source,
            deterministic_review=review,
        )
    ),
    "references unknown assessment ID",
)
 
 
print(
    "ALL GROUNDED AI ENGINEERING REVIEW CHECKS PASSED"
) 

# --------------------------------------------------
# Step 34.5 — Final Engineering Review Service
# --------------------------------------------------
 
service_result = (
    EngineeringReviewService.build(
        intelligence_result,
        use_ai=True,
        provider=MockProvider(),
    )
)
 
assert isinstance(
    service_result,
    EngineeringReviewResult,
)
 
assert (
    service_result.source.intelligence_result
    is intelligence_result
)
 
assert service_result.ai_requested
 
assert service_result.ai_enriched
 
assert service_result.used_ai
 
assert not service_result.used_fallback
 
assert (
    service_result.review.status
    == service_result
    .deterministic_review.status
)
 
assert (
    service_result.review
    .source_assessment_ids
    == service_result
    .deterministic_review
    .source_assessment_ids
)
 
assert (
    service_result.review
    .source_insight_ids
    == service_result
    .deterministic_review
    .source_insight_ids
)
 
 
# --------------------------------------------------
# Deterministic-only mode
# --------------------------------------------------
 
deterministic_result = (
    EngineeringReviewService.build(
        intelligence_result,
        use_ai=False,
    )
)
 
assert not deterministic_result.ai_requested
 
assert not deterministic_result.ai_enriched
 
assert not deterministic_result.used_ai
 
assert not deterministic_result.used_fallback
 
assert (
    deterministic_result.review
    == deterministic_result
    .deterministic_review
)
 
 
# --------------------------------------------------
# AI failure safely falls back
# --------------------------------------------------
 
fallback_result = (
    EngineeringReviewService.build(
        intelligence_result,
        use_ai=True,
        provider=FailingReviewProvider(),
        fallback_to_deterministic=True,
    )
)
 
assert fallback_result.ai_requested
 
assert not fallback_result.ai_enriched
 
assert not fallback_result.used_ai
 
assert fallback_result.used_fallback
 
assert (
    "Simulated review-provider failure"
    in fallback_result.fallback_reason
)
 
assert (
    fallback_result.review
    == fallback_result
    .deterministic_review
)
 
 
# --------------------------------------------------
# Strict mode still exposes provider failures
# --------------------------------------------------
 
try:
    EngineeringReviewService.build(
        intelligence_result,
        use_ai=True,
        provider=FailingReviewProvider(),
        fallback_to_deterministic=False,
    )
 
except RuntimeError as error:
    assert (
        "Simulated review-provider failure"
        in str(error)
    )
 
else:
    raise AssertionError(
        "Strict AI-review mode did not propagate the "
        "provider failure."
    )
 
 
# --------------------------------------------------
# Professional floating-point payload formatting
# --------------------------------------------------
 
assert (
    EngineeringReviewPayloadBuilder
    ._to_json_value(
        5.700000000000003
    )
    == 5.7
)
 
assert (
    EngineeringReviewPayloadBuilder
    ._to_json_value(
        0.024400000000000005
    )
    == 0.0244
)

assert (
    EngineeringReviewPayloadBuilder
    ._to_json_value(
        date(
            2026,
            7,
            29,
        )
    )
    == "2026-07-29"
)
 
expect_value_error(
    lambda: (
        EngineeringReviewPayloadBuilder
        ._to_json_value(
            float("inf")
        )
    ),
    "Non-finite numerical value",
)
 
 
print(
    "ALL FINAL ENGINEERING REVIEW SERVICE CHECKS PASSED"
)

# --------------------------------------------------
# Step 35.2 — Grounded recommendation payload
# --------------------------------------------------
 
recommendation_payload = (
    EngineeringRecommendationPayloadBuilder
    .build(
        service_result
    )
)
 
assert isinstance(
    recommendation_payload,
    dict,
)
 
assert (
    recommendation_payload[
        "recommendation_contract"
    ][
        "engineering_calculations_are_locked"
    ]
)
 
assert (
    recommendation_payload[
        "engineering_evidence"
    ][
        "review_contract"
    ][
        "engineering_evidence_is_locked"
    ]
)
 
assert (
    recommendation_payload[
        "final_engineering_review"
    ][
        "status"
    ]
    == service_result.review.status.value
)
 
 
# --------------------------------------------------
# Required actions remain available to Gemini
# --------------------------------------------------
 
payload_action_ids = {
    item["item_id"]
    for item
    in recommendation_payload[
        "final_engineering_review"
    ][
        "required_actions"
    ]
}
 
expected_action_ids = {
    item.item_id
    for item
    in service_result.review.required_actions
}
 
assert (
    payload_action_ids
    == expected_action_ids
)
 
 
# --------------------------------------------------
# Validation requirements remain available
# --------------------------------------------------
 
payload_validation_ids = {
    item["item_id"]
    for item
    in recommendation_payload[
        "final_engineering_review"
    ][
        "validation_requirements"
    ]
}
 
expected_validation_ids = {
    item.item_id
    for item
    in (
        service_result.review
        .validation_requirements
    )
}
 
assert (
    payload_validation_ids
    == expected_validation_ids
)
 
 
# --------------------------------------------------
# Grounded Step 34 trade-offs remain available
# --------------------------------------------------
 
payload_tradeoff_ids = {
    tradeoff["tradeoff_id"]
    for tradeoff
    in recommendation_payload[
        "final_engineering_review"
    ][
        "tradeoffs"
    ]
}
 
expected_tradeoff_ids = {
    tradeoff.tradeoff_id
    for tradeoff
    in service_result.review.tradeoffs
}
 
assert (
    payload_tradeoff_ids
    == expected_tradeoff_ids
)
 
 
# --------------------------------------------------
# Complete deterministic ID registries preserved
# --------------------------------------------------
 
assert set(
    recommendation_payload[
        "valid_source_ids"
    ][
        "assessment_ids"
    ]
) == set(
    service_result
    .review
    .source_assessment_ids
)
 
assert set(
    recommendation_payload[
        "valid_source_ids"
    ][
        "insight_ids"
    ]
) == set(
    service_result
    .review
    .source_insight_ids
)
 
 
# --------------------------------------------------
# Invalid recommendation source rejected
# --------------------------------------------------
 
expect_value_error(
    lambda: (
        EngineeringRecommendationPayloadBuilder
        .build(
            "invalid"
        )
    ),
    "'review_result' must be an "
    "EngineeringReviewResult object",
)
 
 
print(
    "ALL ENGINEERING RECOMMENDATION PAYLOAD CHECKS PASSED"
)

# --------------------------------------------------
# Step 35.3D — Grounded AI recommendation synthesis
# --------------------------------------------------
 
 
class GroundedRecommendationTestProvider(
    LLMProvider
):
    """
    Controlled provider used to verify the complete
    recommendation synthesis boundary.
    """
 
    def extract_requirements(
        self,
        text: str,
    ) -> dict:
        return {}
 
    def synthesize_engineering_review(
        self,
        payload: dict,
    ) -> dict:
        return {}
 
    def synthesize_engineering_recommendations(
        self,
        payload: dict,
    ) -> dict:
        review_item_ids = (
            payload[
                "valid_source_ids"
            ][
                "review_item_ids"
            ]
        )
 
        assessment_ids = (
            payload[
                "valid_source_ids"
            ][
                "assessment_ids"
            ]
        )
 
        insight_ids = (
            payload[
                "valid_source_ids"
            ][
                "insight_ids"
            ]
        )
 
        assert review_item_ids
 
        return {
            "recommendations": [
                {
                    "recommendation_id": (
                        "ai.recommendation.test"
                    ),
                    "recommendation_type": (
                        "design_improvement"
                    ),
                    "priority": "high",
                    "category": "thermal",
                    "severity": "warning",
                    "title": (
                        "Review thermal margin"
                    ),
                    "recommendation": (
                        "Review the selected design's "
                        "limited thermal margin before "
                        "design release."
                    ),
                    "rationale": (
                        "The supplied engineering review "
                        "identifies limited remaining "
                        "thermal margin."
                    ),
                    "expected_effect": (
                        "Improve confidence in thermal "
                        "robustness before release."
                    ),
                    "verification": (
                        "Re-run the deterministic thermal "
                        "assessment after any accepted "
                        "design refinement."
                    ),
                    "source_review_item_ids": [
                        review_item_ids[0]
                    ],
                    "source_tradeoff_ids": [],
                    "source_assessment_ids": (
                        assessment_ids[:1]
                    ),
                    "source_insight_ids": (
                        insight_ids[:1]
                    ),
                }
            ]
        }
 
 
recommendation_test_provider = (
    GroundedRecommendationTestProvider()
)
 
ai_recommendations = (
    EngineeringRecommendationAISynthesizer
    .synthesize(
        review_result=service_result,
        provider=(
            recommendation_test_provider
        ),
    )
)
 
assert isinstance(
    ai_recommendations,
    tuple,
)
 
assert len(
    ai_recommendations
) == 1
 
assert isinstance(
    ai_recommendations[0],
    EngineeringRecommendation,
)
 
assert (
    ai_recommendations[0]
    .recommendation_id
    == "ai.recommendation.test"
)
 
assert (
    ai_recommendations[0]
    .is_traceable
)
 
 
# --------------------------------------------------
# Invented source IDs must fail grounding
# --------------------------------------------------
 
 
class UngroundedRecommendationTestProvider(
    LLMProvider
):
    def extract_requirements(
        self,
        text: str,
    ) -> dict:
        return {}
 
    def synthesize_engineering_review(
        self,
        payload: dict,
    ) -> dict:
        return {}
 
    def synthesize_engineering_recommendations(
        self,
        payload: dict,
    ) -> dict:
        return {
            "recommendations": [
                {
                    "recommendation_id": (
                        "ai.recommendation.ungrounded"
                    ),
                    "recommendation_type": (
                        "validation"
                    ),
                    "priority": "medium",
                    "category": "thermal",
                    "severity": "warning",
                    "title": "Invalid recommendation",
                    "recommendation": (
                        "Perform unsupported validation."
                    ),
                    "rationale": (
                        "This deliberately references "
                        "invented evidence."
                    ),
                    "expected_effect": "",
                    "verification": "",
                    "source_review_item_ids": [
                        "review.item.does.not.exist"
                    ],
                    "source_tradeoff_ids": [],
                    "source_assessment_ids": [],
                    "source_insight_ids": [],
                }
            ]
        }
 
 
expect_value_error(
    lambda: (
        EngineeringRecommendationAISynthesizer
        .synthesize(
            review_result=service_result,
            provider=(
                UngroundedRecommendationTestProvider()
            ),
        )
    ),
    "unknown source_review_item_ids",
)
 
 
print(
    "ALL GROUNDED AI ENGINEERING "
    "RECOMMENDATION CHECKS PASSED"
)

# --------------------------------------------------
# Step 35.4 — Engineering Recommendation Service
# --------------------------------------------------
 
recommendation_result = (
    EngineeringRecommendationService.build(
        service_result,
        provider=(
            recommendation_test_provider
        ),
    )
)
 
assert isinstance(
    recommendation_result,
    EngineeringRecommendationResult,
)
 
assert (
    recommendation_result.review_result
    is service_result
)
 
assert (
    recommendation_result.recommendations
    == ai_recommendations
)
 
assert recommendation_result.has_recommendations
 
assert (
    recommendation_result.recommendation_count
    == len(ai_recommendations)
)
 
for recommendation in (
    recommendation_result.recommendations
):
    assert isinstance(
        recommendation,
        EngineeringRecommendation,
    )
 
    assert recommendation.is_traceable

# --------------------------------------------------
# Recommendation AI failure fallback
# --------------------------------------------------
fallback_recommendation_result = (
    EngineeringRecommendationService.build(
        service_result,
        provider=(
            FailingRecommendationProvider()
        ),
        fallback_to_empty=True,
    )
)
assert isinstance(
    fallback_recommendation_result,
    EngineeringRecommendationResult,
)
assert (
    fallback_recommendation_result.review_result
    is service_result
)
assert (
    fallback_recommendation_result.recommendations
    == ()
)
assert not (
    fallback_recommendation_result
    .has_recommendations
)
# --------------------------------------------------
# Strict recommendation mode must still raise
# --------------------------------------------------
try:
    EngineeringRecommendationService.build(
        service_result,
        provider=(
            FailingRecommendationProvider()
        ),
        fallback_to_empty=False,
    )
except RuntimeError as error:
    assert (
        "Simulated recommendation-provider failure."
        in str(error)
    )
else:
    raise AssertionError(
        "Strict recommendation synthesis did not "
        "propagate the provider failure."
    ) 
 
# --------------------------------------------------
# Service input validation
# --------------------------------------------------
 
expect_value_error(
    lambda: (
        EngineeringRecommendationService.build(
            "invalid"
        )
    ),
    "'review_result' must be an "
    "EngineeringReviewResult object",
)
 
expect_value_error(
    lambda: (
        EngineeringRecommendationService.build(
            service_result,
            provider="invalid",
        )
    ),
    "'provider' must be an LLMProvider object or None",
)

expect_value_error(
    lambda: (
        EngineeringRecommendationService.build(
            service_result,
            fallback_to_empty="invalid",
        )
    ),
    "'fallback_to_empty' must be a boolean",
)
 
 
 
print(
    "ALL ENGINEERING RECOMMENDATION SERVICE CHECKS PASSED"
)

# --------------------------------------------------
# Optional live-provider smoke test
# --------------------------------------------------
 
if (
    os.getenv(
        "RUN_LIVE_LLM_REVIEW",
        "",
    ).strip()
    == "1"
):
    live_provider = get_llm_provider()
 
    print()
    print(
        "LIVE ENGINEERING REVIEW PROVIDER:",
        live_provider.__class__.__name__,
    )
 
    live_review = (
        EngineeringReviewAISynthesizer
        .synthesize(
            source=source,
            deterministic_review=review,
            provider=live_provider,
        )
    )
 
    # --------------------------------------------------
    # Deterministic authority must remain locked
    # --------------------------------------------------
 
    assert (
        live_review.status
        == review.status
    )
 
    assert (
        live_review.strengths
        == review.strengths
    )
 
    assert (
        live_review.concerns
        == review.concerns
    )
 
    assert (
        live_review.required_actions
        == review.required_actions
    )
 
    assert (
        live_review.validation_requirements
        == review.validation_requirements
    )
 
    assert (
        live_review.source_assessment_ids
        == review.source_assessment_ids
    )
 
    assert (
        live_review.source_insight_ids
        == review.source_insight_ids
    )
 
    # --------------------------------------------------
    # Structural integrity
    # --------------------------------------------------
 
    assert live_review.executive_summary.strip()
 
    assert (
        len(live_review.sections)
        == len(review.sections)
    )
 
    for deterministic_section, live_section in zip(
        review.sections,
        live_review.sections,
    ):
        assert (
            live_section.category
            == deterministic_section.category
        )
 
        assert (
            live_section.status
            == deterministic_section.status
        )
 
        assert (
            live_section.findings
            == deterministic_section.findings
        )
 
        assert (
            live_section.source_assessment_ids
            == deterministic_section
            .source_assessment_ids
        )
 
        assert (
            live_section.source_insight_ids
            == deterministic_section
            .source_insight_ids
        )
 
        assert live_section.summary.strip()
 
    # --------------------------------------------------
    # AI trade-offs must remain traceable
    # --------------------------------------------------
 
    for tradeoff in live_review.tradeoffs:
 
        assert (
            len(tradeoff.categories)
            >= 2
        )
 
        assert (
            tradeoff.source_assessment_ids
            or tradeoff.source_insight_ids
        )
 
        for assessment_id in (
            tradeoff.source_assessment_ids
        ):
            assert (
                assessment_id
                in source.assessment_index
            )
 
        for insight_id in (
            tradeoff.source_insight_ids
        ):
            assert (
                insight_id
                in source.insight_index
            )
 
    # --------------------------------------------------
    # Human-readable smoke-test output
    # --------------------------------------------------
 
    print()
    print("=" * 70)
    print("LIVE AI ENGINEERING REVIEW")
    print("=" * 70)
 
    print()
    print(
        "Deterministic status:",
        live_review.status.value,
    )
 
    print()
    print("Executive summary:")
    print(
        live_review.executive_summary
    )
 
    print()
    print("Section summaries:")
 
    for section in live_review.sections:
        print()
        print(
            f"[{section.category.value}]"
        )
        print(
            section.summary
        )
 
    print()
    print(
        "AI trade-offs:",
        len(live_review.tradeoffs),
    )
 
    for tradeoff in live_review.tradeoffs:
        print()
        print(
            f"- {tradeoff.title}"
        )
        print(
            "  Categories:",
            ", ".join(
                category.value
                for category
                in tradeoff.categories
            ),
        )
        print(
            "  Benefit:",
            tradeoff.benefit,
        )
        print(
            "  Penalty:",
            tradeoff.penalty,
        )
 
    print()
    print(
        "ALL LIVE PROVIDER ENGINEERING REVIEW "
        "CHECKS PASSED"
    )

# --------------------------------------------------
# Step 35.3E — Live AI recommendation synthesis
# --------------------------------------------------
 
if (
    os.getenv(
        "RUN_LIVE_LLM_REVIEW",
        "",
    ).strip()
    == "1"
):
    live_recommendation_provider = (
        get_llm_provider()
    )
 
    print()
    print(
        "LIVE ENGINEERING RECOMMENDATION PROVIDER:",
        live_recommendation_provider
        .__class__.__name__,
    )
 
    # Build the canonical Step 34 result using the
    # deterministic source/review plus the live AI-enriched
    # review already produced by the preceding live test.
    live_engineering_review_result = (
        EngineeringReviewResult(
            source=source,
            deterministic_review=review,
            review=live_review,
            ai_requested=True,
            ai_enriched=True,
        )
    )
 
    live_recommendations = (
        EngineeringRecommendationAISynthesizer
        .synthesize(
            review_result=(
                live_engineering_review_result
            ),
            provider=(
                live_recommendation_provider
            ),
        )
    )
 
    print()
    print("=" * 70)
    print(
        "LIVE AI ENGINEERING RECOMMENDATIONS"
    )
    print("=" * 70)
 
    print()
    print(
        "Recommendation count:",
        len(
            live_recommendations
        ),
    )
 
    for index, recommendation in enumerate(
        live_recommendations,
        start=1,
    ):
        print()
        print(
            f"{index}. {recommendation.title}"
        )
 
        print(
            "   Type:",
            recommendation
            .recommendation_type
            .value,
        )
 
        print(
            "   Priority:",
            recommendation.priority.value,
        )
 
        print(
            "   Category:",
            recommendation.category.value,
        )
 
        print(
            "   Severity:",
            recommendation.severity.value,
        )
 
        print(
            "   Recommendation:",
            recommendation.recommendation,
        )
 
        print(
            "   Rationale:",
            recommendation.rationale,
        )
 
        if recommendation.expected_effect:
            print(
                "   Expected effect:",
                recommendation.expected_effect,
            )
 
        if recommendation.verification:
            print(
                "   Verification:",
                recommendation.verification,
            )
 
        print(
            "   Review sources:",
            recommendation
            .source_review_item_ids,
        )
 
        print(
            "   Trade-off sources:",
            recommendation
            .source_tradeoff_ids,
        )
 
        print(
            "   Assessment sources:",
            recommendation
            .source_assessment_ids,
        )
 
        print(
            "   Insight sources:",
            recommendation
            .source_insight_ids,
        )
 
    assert isinstance(
        live_recommendations,
        tuple,
    )
 
    for recommendation in (
        live_recommendations
    ):
        assert isinstance(
            recommendation,
            EngineeringRecommendation,
        )
 
        assert recommendation.is_traceable
 
    print()
    print(
        "ALL LIVE PROVIDER ENGINEERING "
        "RECOMMENDATION CHECKS PASSED"
    )
 
print(
    "ALL DETERMINISTIC ENGINEERING REVIEW CHECKS PASSED"
)