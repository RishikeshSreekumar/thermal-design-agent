"""
model_limitation_analyzer.py
 
Convert explicitly declared model and workflow limitations
into structured engineering insights.
"""
 
from intelligence.analyzers.base_analyzer import (
    EngineeringAnalyzer,
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
 
 
class ModelLimitationAnalyzer(
    EngineeringAnalyzer,
):
    """
    Generate one warning insight for every explicitly
    declared model or workflow limitation.
    """
 
    def analyze(
        self,
        context: EngineeringContext,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Convert declared limitations into traceable
        engineering insights.
        """
 
        if not isinstance(
            context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )
 
        return tuple(
            EngineeringInsight(
                insight_id=(
                    "model_limitation."
                    f"{index}"
                ),
                severity=EngineeringSeverity.WARNING,
                category=(
                    EngineeringCategory
                    .MODEL_LIMITATION
                ),
                title="Declared model limitation",
                summary=limitation,
                evidence=(
                    EngineeringEvidence(
                        key="limitation_number",
                        value=index,
                    ),
                    EngineeringEvidence(
                        key="limitation",
                        value=limitation,
                    ),
                ),
                source="engineering_context",
            )
            for index, limitation in enumerate(
                context.known_limitations,
                start=1,
            )
        )