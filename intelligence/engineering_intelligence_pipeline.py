"""
engineering_intelligence_pipeline.py
 
Canonical orchestration entry point for deterministic
engineering intelligence.
 
The pipeline:
 
1. builds the shared EngineeringContext;
2. generates deterministic EngineeringInsight objects;
3. generates deterministic EngineeringAssessment objects;
4. returns one immutable aggregate result.
 
The pipeline contains no engineering thresholds and does
not invoke an LLM.
"""
 
from intelligence.context_builder import (
    EngineeringContextBuilder,
)
from intelligence.engineering_assessment_engine import (
    EngineeringAssessmentEngine,
)
from intelligence.insight_engine import (
    EngineeringInsightEngine,
)
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.optimization_result import (
    OptimizationResult,
)
from models.requirements import (
    EngineeringRequirements,
)
 
 
class EngineeringIntelligencePipeline:
    """
    Run the complete deterministic engineering-intelligence
    workflow.
    """
 
    def __init__(
        self,
        assessment_engine: EngineeringAssessmentEngine,
    ) -> None:
        """
        Create the pipeline with an explicitly configured
        assessment engine.
        """
 
        if not isinstance(
            assessment_engine,
            EngineeringAssessmentEngine,
        ):
            raise ValueError(
                "'assessment_engine' must be an "
                "EngineeringAssessmentEngine object."
            )
 
        self._assessment_engine = (
            assessment_engine
        )
 
    @property
    def assessment_engine(
        self,
    ) -> EngineeringAssessmentEngine:
        """
        Return the configured assessment engine.
        """
 
        return self._assessment_engine
 
    def run(
        self,
        requirements: EngineeringRequirements,
        optimization_result: OptimizationResult,
        known_limitations: tuple[
            str,
            ...,
        ] = (),
    ) -> EngineeringIntelligenceResult:
        """
        Run the complete deterministic intelligence
        pipeline.
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
            optimization_result,
            OptimizationResult,
        ):
            raise ValueError(
                "'optimization_result' must be an "
                "OptimizationResult object."
            )
 
        if not isinstance(
            known_limitations,
            tuple,
        ):
            raise ValueError(
                "'known_limitations' must be a tuple."
            )
 
        for limitation in known_limitations:
            if not isinstance(
                limitation,
                str,
            ):
                raise ValueError(
                    "Every known limitation must be a "
                    "string."
                )
 
        context = EngineeringContextBuilder.build(
            requirements=requirements,
            optimization_result=optimization_result,
            known_limitations=known_limitations,
        )
 
        insights = (
            EngineeringInsightEngine.generate(
                context
            )
        )
 
        assessments = (
            self._assessment_engine.evaluate(
                context=context,
                insights=insights,
            )
        )
 
        return EngineeringIntelligenceResult(
            context=context,
            insights=insights,
            assessments=assessments,
        )