"""
airflow_analyzer.py
 
Generate deterministic insights describing the airflow
and hydraulic performance of selected heat-sink
candidates.
 
This analyzer reports calculated engineering facts. It
does not apply unsupported acceptance thresholds and
does not invoke an LLM.
"""
 
from intelligence.analyzers.base_analyzer import (
    EngineeringAnalyzer,
)
from models.design_candidate import (
    DesignCandidate,
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
 
 
class AirflowAnalyzer(
    EngineeringAnalyzer,
):
    """
    Generate structured airflow-performance insights for
    the candidate or candidates selected by optimization.
    """
 
    def analyze(
        self,
        context: EngineeringContext,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Generate airflow insights appropriate to the
        candidate-selection result.
        """
 
        if not isinstance(
            context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )

        if (
            context.requirements.convection_mode
            == "natural"
        ):
            return ()
 
        if context.has_single_selected_design:
            selected_candidate = (
                context.selected_candidate
            )
 
            if selected_candidate is None:
                raise RuntimeError(
                    "Single-design engineering context "
                    "contains no selected candidate."
                )
 
            return (
                self._build_single_candidate_insight(
                    selected_candidate
                ),
            )
 
        return (
            self._build_tradeoff_set_insight(
                context.selected_candidates
            ),
        )
 
    @staticmethod
    def _build_single_candidate_insight(
        candidate: DesignCandidate,
    ) -> EngineeringInsight:
        """
        Report calculated airflow performance for one
        uniquely selected design.
        """
 
        return EngineeringInsight(
            insight_id=(
                "airflow.selected_design_performance"
            ),
            severity=EngineeringSeverity.INFO,
            category=EngineeringCategory.AIRFLOW,
            title="Selected-design airflow performance",
            summary=(
                "The deterministic airflow model "
                "calculated the flow and hydraulic "
                "performance of the uniquely selected "
                "heat-sink design."
            ),
            evidence=(
                EngineeringEvidence(
                    key="approach_velocity",
                    value=candidate.approach_velocity,
                    unit="m/s",
                ),
                EngineeringEvidence(
                    key="channel_velocity",
                    value=candidate.channel_velocity,
                    unit="m/s",
                ),
                EngineeringEvidence(
                    key="open_flow_area",
                    value=candidate.open_flow_area,
                    unit="m^2",
                ),
                EngineeringEvidence(
                    key="blockage_ratio",
                    value=candidate.blockage_ratio,
                ),
                EngineeringEvidence(
                    key="reynolds_number",
                    value=candidate.reynolds_number,
                ),
                EngineeringEvidence(
                    key="pressure_drop",
                    value=candidate.pressure_drop,
                    unit="Pa",
                ),
                EngineeringEvidence(
                    key="pumping_power",
                    value=candidate.pumping_power,
                    unit="W",
                ),
            ),
            source="selected_design_candidate",
        )
 
    @staticmethod
    def _build_tradeoff_set_insight(
        candidates: tuple[
            DesignCandidate,
            ...,
        ],
    ) -> EngineeringInsight:
        """
        Report airflow-performance ranges across multiple
        selected Pareto-optimal candidates.
        """
 
        if len(candidates) < 2:
            raise ValueError(
                "Airflow trade-off insight requires at "
                "least two selected candidates."
            )
 
        approach_velocities = tuple(
            candidate.approach_velocity
            for candidate in candidates
        )
 
        channel_velocities = tuple(
            candidate.channel_velocity
            for candidate in candidates
        )
 
        open_flow_areas = tuple(
            candidate.open_flow_area
            for candidate in candidates
        )
 
        blockage_ratios = tuple(
            candidate.blockage_ratio
            for candidate in candidates
        )
 
        reynolds_numbers = tuple(
            candidate.reynolds_number
            for candidate in candidates
        )
 
        pressure_drops = tuple(
            candidate.pressure_drop
            for candidate in candidates
        )
 
        pumping_powers = tuple(
            candidate.pumping_power
            for candidate in candidates
        )
 
        return EngineeringInsight(
            insight_id=(
                "airflow.tradeoff_set_performance"
            ),
            severity=EngineeringSeverity.INFO,
            category=EngineeringCategory.AIRFLOW,
            title="Airflow range across trade-off set",
            summary=(
                "The selected Pareto-optimal candidates "
                "span a range of calculated airflow and "
                "hydraulic performance values."
            ),
            evidence=(
                EngineeringEvidence(
                    key="selected_candidate_count",
                    value=len(candidates),
                ),
                EngineeringEvidence(
                    key="minimum_approach_velocity",
                    value=min(
                        approach_velocities
                    ),
                    unit="m/s",
                ),
                EngineeringEvidence(
                    key="maximum_approach_velocity",
                    value=max(
                        approach_velocities
                    ),
                    unit="m/s",
                ),
                EngineeringEvidence(
                    key="minimum_channel_velocity",
                    value=min(
                        channel_velocities
                    ),
                    unit="m/s",
                ),
                EngineeringEvidence(
                    key="maximum_channel_velocity",
                    value=max(
                        channel_velocities
                    ),
                    unit="m/s",
                ),
                EngineeringEvidence(
                    key="minimum_open_flow_area",
                    value=min(
                        open_flow_areas
                    ),
                    unit="m^2",
                ),
                EngineeringEvidence(
                    key="maximum_open_flow_area",
                    value=max(
                        open_flow_areas
                    ),
                    unit="m^2",
                ),
                EngineeringEvidence(
                    key="minimum_blockage_ratio",
                    value=min(
                        blockage_ratios
                    ),
                ),
                EngineeringEvidence(
                    key="maximum_blockage_ratio",
                    value=max(
                        blockage_ratios
                    ),
                ),
                EngineeringEvidence(
                    key="minimum_reynolds_number",
                    value=min(
                        reynolds_numbers
                    ),
                ),
                EngineeringEvidence(
                    key="maximum_reynolds_number",
                    value=max(
                        reynolds_numbers
                    ),
                ),
                EngineeringEvidence(
                    key="minimum_pressure_drop",
                    value=min(
                        pressure_drops
                    ),
                    unit="Pa",
                ),
                EngineeringEvidence(
                    key="maximum_pressure_drop",
                    value=max(
                        pressure_drops
                    ),
                    unit="Pa",
                ),
                EngineeringEvidence(
                    key="minimum_pumping_power",
                    value=min(
                        pumping_powers
                    ),
                    unit="W",
                ),
                EngineeringEvidence(
                    key="maximum_pumping_power",
                    value=max(
                        pumping_powers
                    ),
                    unit="W",
                ),
            ),
            source="selected_pareto_candidates",
        )