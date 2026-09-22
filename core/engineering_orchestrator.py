"""
engineering_orchestrator.py
 
Application-facing orchestration boundary for the complete
Thermal Design Agent engineering workflow.
 
The orchestrator coordinates existing public services.
 
It does not:
- perform thermal calculations;
- implement manufacturing rules;
- create engineering assessments itself;
- generate ungrounded AI conclusions;
- duplicate report logic.
"""
 
from llm.base import (
    LLMProvider,
)
 
from core.cad_generator import (
    CADGenerator,
)
from core.engineering_recommendation_service import (
    EngineeringRecommendationService,
)
from core.engineering_report_builder import (
    EngineeringReportBuilder,
)
from core.engineering_review_service import (
    EngineeringReviewService,
)
from core.geometry_planner import (
    GeometryPlanner,
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
 
from models.engineering_application_result import (
    EngineeringApplicationResult,
)
from models.requirements import (
    EngineeringRequirements,
)
 
 
class EngineeringOrchestrator:
    """
    Execute one complete engineering-design workflow.
    """
 
    @classmethod
    def run(
        cls,
        requirements: EngineeringRequirements,
        *,
        use_ai: bool = True,
        provider: LLMProvider | None = None,
        fallback_to_deterministic: bool = True,
        known_limitations: tuple[
            str,
            ...,
        ] = (),
    ) -> EngineeringApplicationResult:
        """
        Run the complete Thermal Design Agent workflow.
 
        Requirements must already have passed the existing
        requirement-review / clarification boundary.
        """
 
        if not isinstance(
            requirements,
            EngineeringRequirements,
        ):
            raise ValueError(
                "'requirements' must be an "
                "EngineeringRequirements object."
            )
 
        if not isinstance(
            use_ai,
            bool,
        ):
            raise ValueError(
                "'use_ai' must be a boolean."
            )
 
        if not isinstance(
            fallback_to_deterministic,
            bool,
        ):
            raise ValueError(
                "'fallback_to_deterministic' must be "
                "a boolean."
            )
 
        if not isinstance(
            known_limitations,
            tuple,
        ):
            raise ValueError(
                "'known_limitations' must be a tuple."
            )
 
        # --------------------------------------------------
        # 1. Deterministic Optimization
        # --------------------------------------------------
 
        optimization_result = (
            ThermalOptimizer()
            .optimize_with_details(
                requirements
            )
        )
 
        if not (
            optimization_result
            .has_feasible_design
        ):
            raise ValueError(
                "No feasible heat-sink design was found "
                "within the supplied engineering "
                "requirements."
            )
 
        if (
            optimization_result
            .selected_candidate
            is None
        ):
            raise ValueError(
                "The current application workflow requires "
                "one uniquely selected design."
            )
 
        # --------------------------------------------------
        # 2. Deterministic Engineering Intelligence
        # --------------------------------------------------
 
        assessment_engine = (
            EngineeringAssessmentEngine(
                evaluators=(
                    ManufacturabilityEvaluator(
                        capability=(
                            AL6063_EXTRUSION
                        ),
                    ),
                    ThermalMarginEvaluator(
                        warning_margin_temperature=10.0,
                    ),
                    AirflowPerformanceEvaluator(),
                )
            )
        )
 
        intelligence_pipeline = (
            EngineeringIntelligencePipeline(
                assessment_engine=(
                    assessment_engine
                )
            )
        )
 
        intelligence_result = (
            intelligence_pipeline.run(
                requirements=requirements,
                optimization_result=(
                    optimization_result
                ),
                known_limitations=(
                    known_limitations
                ),
            )
        )
 
        # --------------------------------------------------
        # 3. Engineering Review
        # --------------------------------------------------
 
        review_result = (
            EngineeringReviewService.build(
                intelligence_result,
                use_ai=use_ai,
                provider=provider,
                fallback_to_deterministic=(
                    fallback_to_deterministic
                ),
            )
        )
 
        # --------------------------------------------------
        # 4. Engineering Recommendations
        # --------------------------------------------------
 
        if use_ai:
            recommendation_result = (
                EngineeringRecommendationService
                .build(
                    review_result,
                    provider=provider,
                    fallback_to_empty=(
                        fallback_to_deterministic
                    ),
                )
            )
 
        else:
            from models.engineering_recommendation_result import (
                EngineeringRecommendationResult,
            )
 
            recommendation_result = (
                EngineeringRecommendationResult(
                    review_result=(
                        review_result
                    ),
                    recommendations=(),
                )
            )
 
        # --------------------------------------------------
        # 5. Engineering Report
        # --------------------------------------------------
 
        report = (
            EngineeringReportBuilder.build(
                recommendation_result
            )
        )
 
        # --------------------------------------------------
        # 6. Geometry Planning
        # --------------------------------------------------
 
        thermal_result = (
            optimization_result.best_result
        )
 
        if thermal_result is None:
            raise ValueError(
                "Selected design does not provide a "
                "single thermal result required for CAD."
            )
 
        geometry = (
            GeometryPlanner()
            .create_geometry(
                requirements,
                thermal_result,
            )
        )
 
        # --------------------------------------------------
        # 7. CAD / STEP Generation
        # --------------------------------------------------
 
        step_file = (
            CADGenerator()
            .generate(
                geometry
            )
        )
 
        # --------------------------------------------------
        # 8. Complete Application Result
        # --------------------------------------------------
 
        return EngineeringApplicationResult(
            requirements=requirements,
            optimization_result=(
                optimization_result
            ),
            intelligence_result=(
                intelligence_result
            ),
            review_result=review_result,
            recommendation_result=(
                recommendation_result
            ),
            report=report,
            geometry=geometry,
            step_file=step_file,
        )