"""
optimization_analyzer.py
 
Generate deterministic insights about optimization,
candidate feasibility, candidate selection, material, and
manufacturing-process metadata.
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
 
 
class OptimizationAnalyzer(
    EngineeringAnalyzer,
):
    """
    Generate high-confidence insights about a completed
    deterministic optimization workflow.
    """
 
    def analyze(
        self,
        context: EngineeringContext,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Generate optimization-related insights.
        """
 
        if not isinstance(
            context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )
 
        return (
            self._build_completion_insight(
                context
            ),
            self._build_feasibility_insight(
                context
            ),
            self._build_selection_insight(
                context
            ),
            self._build_material_insight(
                context
            ),
            self._build_process_insight(
                context
            ),
        )
 
    @staticmethod
    def _build_completion_insight(
        context: EngineeringContext,
    ) -> EngineeringInsight:
        """
        Describe successful completion of deterministic
        optimization and candidate selection.
        """
 
        return EngineeringInsight(
            insight_id="optimization.completed",
            severity=EngineeringSeverity.SUCCESS,
            category=(
                EngineeringCategory.OPTIMIZATION
            ),
            title="Optimization completed successfully",
            summary=(
                "The deterministic optimization workflow "
                "completed and produced at least one "
                "selected feasible design."
            ),
            evidence=(
                EngineeringEvidence(
                    key="total_candidate_count",
                    value=context.total_candidate_count,
                    description=(
                        "Total number of explored design "
                        "candidates."
                    ),
                ),
                EngineeringEvidence(
                    key="selected_candidate_count",
                    value=(
                        context
                        .selected_candidate_count
                    ),
                    description=(
                        "Number of candidates returned by "
                        "the configured selection strategy."
                    ),
                ),
            ),
            source="engineering_context",
        )
 
    @staticmethod
    def _build_feasibility_insight(
        context: EngineeringContext,
    ) -> EngineeringInsight:
        """
        Summarize candidate feasibility from the completed
        optimization run.
        """
 
        return EngineeringInsight(
            insight_id=(
                "optimization.candidate_feasibility"
            ),
            severity=EngineeringSeverity.INFO,
            category=(
                EngineeringCategory.OPTIMIZATION
            ),
            title="Candidate feasibility evaluated",
            summary=(
                "The deterministic workflow separated "
                "feasible candidates from rejected "
                "candidates before final selection."
            ),
            evidence=(
                EngineeringEvidence(
                    key="feasible_candidate_count",
                    value=(
                        context
                        .feasible_candidate_count
                    ),
                ),
                EngineeringEvidence(
                    key="rejected_candidate_count",
                    value=(
                        context
                        .rejected_candidate_count
                    ),
                ),
                EngineeringEvidence(
                    key="feasibility_rate",
                    value=context.feasibility_rate,
                    unit="percent",
                ),
            ),
            source="optimization_result",
        )
 
    @staticmethod
    def _build_selection_insight(
        context: EngineeringContext,
    ) -> EngineeringInsight:
        """
        Describe the deterministic strategy used to select
        the final candidate or candidate set.
        """
 
        if context.uses_legacy_selection:
            title = (
                "Minimum thermal resistance selection used"
            )
 
            summary = (
                "The final design was selected by choosing "
                "the feasible candidate with the minimum "
                "thermal resistance."
            )
 
        elif context.uses_weighted_selection:
            title = (
                "Weighted multi-objective selection used"
            )
 
            summary = (
                "The final design was selected using the "
                "configured weighted combination of "
                "engineering objectives."
            )
 
        elif context.uses_pareto_selection:
            title = "Pareto-front selection used"
 
            if context.has_tradeoff_set:
                summary = (
                    "The optimization returned multiple "
                    "non-dominated candidates representing "
                    "different engineering trade-offs."
                )
 
            else:
                summary = (
                    "The Pareto analysis returned one "
                    "non-dominated candidate."
                )
 
        else:
            raise RuntimeError(
                "Unsupported optimization selection mode "
                "in engineering context."
            )
 
        return EngineeringInsight(
            insight_id="optimization.selection_strategy",
            severity=EngineeringSeverity.INFO,
            category=(
                EngineeringCategory.OPTIMIZATION
            ),
            title=title,
            summary=summary,
            evidence=(
                EngineeringEvidence(
                    key="selection_mode",
                    value=context.selection_mode.value,
                ),
                EngineeringEvidence(
                    key="selected_candidate_count",
                    value=(
                        context
                        .selected_candidate_count
                    ),
                ),
                EngineeringEvidence(
                    key="contains_tradeoff_set",
                    value=context.has_tradeoff_set,
                ),
            ),
            source="candidate_selection_result",
        )
 
    @staticmethod
    def _build_material_insight(
        context: EngineeringContext,
    ) -> EngineeringInsight:
        """
        Record the material associated with the completed
        optimization run.
        """
 
        return EngineeringInsight(
            insight_id="material.selected",
            severity=EngineeringSeverity.INFO,
            category=EngineeringCategory.MATERIAL,
            title="Material selection recorded",
            summary=(
                "The engineering context records the "
                "material used for the selected design."
            ),
            evidence=(
                EngineeringEvidence(
                    key="selected_material",
                    value=context.selected_material,
                ),
            ),
            source="optimization_result",
        )
 
    @staticmethod
    def _build_process_insight(
        context: EngineeringContext,
    ) -> EngineeringInsight:
        """
        Record the manufacturing process associated with
        the completed optimization run.
        """
 
        return EngineeringInsight(
            insight_id=(
                "manufacturing.process_recorded"
            ),
            severity=EngineeringSeverity.INFO,
            category=(
                EngineeringCategory.MANUFACTURING
            ),
            title="Manufacturing process recorded",
            summary=(
                "The engineering context records the "
                "manufacturing process used during design "
                "generation and screening."
            ),
            evidence=(
                EngineeringEvidence(
                    key="selected_process",
                    value=context.selected_process,
                ),
            ),
            source="optimization_result",
        )