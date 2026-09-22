"""
insight_engine.py
 
Orchestrate deterministic engineering analyzers and merge
their structured insights.
 
This module does not perform thermal calculations, alter
optimizer results, or invoke an LLM.
"""
 
from intelligence.analyzers.base_analyzer import (
    EngineeringAnalyzer,
)
from intelligence.analyzers.model_limitation_analyzer import (
    ModelLimitationAnalyzer,
)
from intelligence.analyzers.optimization_analyzer import (
    OptimizationAnalyzer,
)
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_insight import (
    EngineeringInsight,
)
from intelligence.analyzers.thermal_analyzer import (
    ThermalAnalyzer,
) 
from intelligence.analyzers.airflow_analyzer import (
    AirflowAnalyzer,
)
from intelligence.analyzers.geometry_analyzer import (
    GeometryAnalyzer,
)
 
class EngineeringInsightEngine:
    """
    Run the registered engineering analyzers and combine
    their structured insights.
    """
 
    _analyzers: tuple[
        EngineeringAnalyzer,
        ...,
    ] = (
        OptimizationAnalyzer(),
        GeometryAnalyzer(),
        ThermalAnalyzer(),
        AirflowAnalyzer(),
        ModelLimitationAnalyzer(),
    )
 
    @classmethod
    def generate(
        cls,
        context: EngineeringContext,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Generate all currently supported engineering
        insights for the supplied context.
        """
 
        if not isinstance(
            context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )
 
        insights: list[
            EngineeringInsight
        ] = []
 
        for analyzer in cls._analyzers:
            analyzer_insights = analyzer.analyze(
                context
            )
 
            for insight in analyzer_insights:
                if not isinstance(
                    insight,
                    EngineeringInsight,
                ):
                    raise TypeError(
                        "Engineering analyzers must return "
                        "EngineeringInsight objects."
                    )
 
            insights.extend(
                analyzer_insights
            )
 
        cls._validate_unique_insight_ids(
            insights
        )
 
        return tuple(
            insights
        )
 
    @staticmethod
    def _validate_unique_insight_ids(
        insights: list[
            EngineeringInsight
        ],
    ) -> None:
        """
        Ensure that analyzers do not produce conflicting
        insight identifiers.
        """
 
        seen_ids: set[
            str
        ] = set()
 
        for insight in insights:
            if insight.insight_id in seen_ids:
                raise ValueError(
                    "Duplicate engineering insight ID "
                    "generated: "
                    f"{insight.insight_id}"
                )
 
            seen_ids.add(
                insight.insight_id
            )