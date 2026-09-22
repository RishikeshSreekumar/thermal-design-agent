"""
airflow_performance_evaluator.py
 
Deterministic evaluator comparing selected-design airflow
performance against explicitly supplied engineering limits.
 
The evaluator does not recalculate pressure drop or pumping
power. It interprets optimizer-produced candidate results.
"""
 
from intelligence.evaluators.base_evaluator import (
    EngineeringEvaluator,
)
from models.engineering_assessment import (
    EngineeringAssessment,
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
 
 
class AirflowPerformanceEvaluator(
    EngineeringEvaluator,
):
    """
    Evaluate selected candidates against explicitly
    supplied pressure-drop and pumping-power limits.
    """
 
    def evaluate(
        self,
        context: EngineeringContext,
        insights: tuple[
            EngineeringInsight,
            ...,
        ],
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Evaluate pressure-drop and pumping-power compliance
        for every selected candidate.
        """
 
        if not isinstance(
            context,
            EngineeringContext,
        ):
            raise ValueError(
                "'context' must be an "
                "EngineeringContext object."
            )
 
        if not isinstance(
            insights,
            tuple,
        ):
            raise ValueError(
                "'insights' must be a tuple."
            )
 
        for insight in insights:
            if not isinstance(
                insight,
                EngineeringInsight,
            ):
                raise ValueError(
                    "Every insight must be an "
                    "EngineeringInsight object."
                )

        if (
            context.requirements.convection_mode
            == "natural"
        ):
            return ()    
 
        operating_requirements = (
            context.requirements.requirements
        )
 
        if operating_requirements is None:
            raise ValueError(
                "Airflow performance evaluation requires "
                "operating requirements."
            )
 
        maximum_pressure_drop = (
            operating_requirements
            .maximum_pressure_drop
        )
 
        maximum_pumping_power = (
            operating_requirements
            .maximum_pumping_power
        )
 
        assessments: list[
            EngineeringAssessment
        ] = []
 
        for candidate_index, candidate in enumerate(
            context.selected_candidates,
            start=1,
        ):
            assessments.append(
                self._evaluate_pressure_drop(
                    candidate_index=candidate_index,
                    pressure_drop=(
                        candidate.pressure_drop
                    ),
                    maximum_pressure_drop=(
                        maximum_pressure_drop
                    ),
                )
            )
 
            assessments.append(
                self._evaluate_pumping_power(
                    candidate_index=candidate_index,
                    pumping_power=(
                        candidate.pumping_power
                    ),
                    maximum_pumping_power=(
                        maximum_pumping_power
                    ),
                )
            )
 
        return tuple(
            assessments
        )
 
    @staticmethod
    def _evaluate_pressure_drop(
        *,
        candidate_index: int,
        pressure_drop: float,
        maximum_pressure_drop: float | None,
    ) -> EngineeringAssessment:
        """
        Evaluate one candidate's calculated pressure drop.
        """
 
        evidence: list[
            EngineeringEvidence
        ] = [
            EngineeringEvidence(
                key="candidate_index",
                value=candidate_index,
            ),
            EngineeringEvidence(
                key="pressure_drop",
                value=pressure_drop,
                unit="Pa",
            ),
        ]
 
        if maximum_pressure_drop is None:
            return EngineeringAssessment(
                assessment_id=(
                    "airflow.pressure_drop."
                    f"selected_candidate_{candidate_index}"
                ),
                rule_id=(
                    "airflow."
                    "maximum_pressure_drop"
                ),
                severity=EngineeringSeverity.INFO,
                category=EngineeringCategory.AIRFLOW,
                title=(
                    "Pressure-drop compliance was not "
                    "evaluated"
                ),
                summary=(
                    "No maximum allowable pressure drop "
                    "was supplied, so pressure-drop "
                    "compliance cannot be determined."
                ),
                evidence=tuple(
                    evidence
                ),
                source_insight_ids=(
                    "airflow."
                    "selected_design_performance",
                ),
                recommendation=(
                    "Provide the maximum allowable "
                    "pressure drop to enable airflow "
                    "constraint assessment."
                ),
                passed=False,
            )
 
        pressure_drop_margin = (
            maximum_pressure_drop
            - pressure_drop
        )
 
        evidence.extend(
            (
                EngineeringEvidence(
                    key="maximum_pressure_drop",
                    value=maximum_pressure_drop,
                    unit="Pa",
                ),
                EngineeringEvidence(
                    key="pressure_drop_margin",
                    value=pressure_drop_margin,
                    unit="Pa",
                ),
            )
        )
 
        if pressure_drop_margin < 0.0:
            severity = EngineeringSeverity.CRITICAL
 
            title = (
                "Selected design exceeds the allowable "
                "pressure drop"
            )
 
            summary = (
                "The calculated heat-sink pressure drop "
                "exceeds the explicitly supplied maximum "
                "allowable pressure drop."
            )
 
            recommendation = (
                "Increase open flow area, increase fin "
                "spacing, reduce channel length, reduce "
                "airflow, revise the geometry, or select "
                "a fan capable of supporting the required "
                "system resistance."
            )
 
            passed = False
 
        else:
            severity = EngineeringSeverity.SUCCESS
 
            title = (
                "Selected design passes the pressure-drop "
                "limit"
            )
 
            summary = (
                "The calculated heat-sink pressure drop "
                "does not exceed the explicitly supplied "
                "maximum allowable pressure drop."
            )
 
            recommendation = ""
 
            passed = True
 
        return EngineeringAssessment(
            assessment_id=(
                "airflow.pressure_drop."
                f"selected_candidate_{candidate_index}"
            ),
            rule_id=(
                "airflow.maximum_pressure_drop"
            ),
            severity=severity,
            category=EngineeringCategory.AIRFLOW,
            title=title,
            summary=summary,
            evidence=tuple(
                evidence
            ),
            source_insight_ids=(
                "airflow."
                "selected_design_performance",
            ),
            recommendation=recommendation,
            passed=passed,
        )
 
    @staticmethod
    def _evaluate_pumping_power(
        *,
        candidate_index: int,
        pumping_power: float,
        maximum_pumping_power: float | None,
    ) -> EngineeringAssessment:
        """
        Evaluate one candidate's calculated ideal fluid
        pumping power.
        """
 
        evidence: list[
            EngineeringEvidence
        ] = [
            EngineeringEvidence(
                key="candidate_index",
                value=candidate_index,
            ),
            EngineeringEvidence(
                key="pumping_power",
                value=pumping_power,
                unit="W",
            ),
        ]
 
        if maximum_pumping_power is None:
            return EngineeringAssessment(
                assessment_id=(
                    "airflow.pumping_power."
                    f"selected_candidate_{candidate_index}"
                ),
                rule_id=(
                    "airflow."
                    "maximum_pumping_power"
                ),
                severity=EngineeringSeverity.INFO,
                category=EngineeringCategory.AIRFLOW,
                title=(
                    "Pumping-power compliance was not "
                    "evaluated"
                ),
                summary=(
                    "No maximum allowable pumping power "
                    "was supplied, so pumping-power "
                    "compliance cannot be determined."
                ),
                evidence=tuple(
                    evidence
                ),
                source_insight_ids=(
                    "airflow."
                    "selected_design_performance",
                ),
                recommendation=(
                    "Provide the maximum allowable "
                    "pumping power to enable airflow "
                    "power assessment."
                ),
                passed=False,
            )
 
        pumping_power_margin = (
            maximum_pumping_power
            - pumping_power
        )
 
        evidence.extend(
            (
                EngineeringEvidence(
                    key="maximum_pumping_power",
                    value=maximum_pumping_power,
                    unit="W",
                ),
                EngineeringEvidence(
                    key="pumping_power_margin",
                    value=pumping_power_margin,
                    unit="W",
                ),
            )
        )
 
        if pumping_power_margin < 0.0:
            severity = EngineeringSeverity.CRITICAL
 
            title = (
                "Selected design exceeds the allowable "
                "pumping power"
            )
 
            summary = (
                "The calculated ideal fluid pumping power "
                "exceeds the explicitly supplied maximum "
                "allowable pumping power."
            )
 
            recommendation = (
                "Reduce system pressure drop, reduce the "
                "required airflow, revise the heat-sink "
                "geometry, or review the fan and system "
                "power architecture."
            )
 
            passed = False
 
        else:
            severity = EngineeringSeverity.SUCCESS
 
            title = (
                "Selected design passes the pumping-power "
                "limit"
            )
 
            summary = (
                "The calculated ideal fluid pumping power "
                "does not exceed the explicitly supplied "
                "maximum allowable pumping power."
            )
 
            recommendation = ""
 
            passed = True
 
        return EngineeringAssessment(
            assessment_id=(
                "airflow.pumping_power."
                f"selected_candidate_{candidate_index}"
            ),
            rule_id=(
                "airflow.maximum_pumping_power"
            ),
            severity=severity,
            category=EngineeringCategory.AIRFLOW,
            title=title,
            summary=summary,
            evidence=tuple(
                evidence
            ),
            source_insight_ids=(
                "airflow."
                "selected_design_performance",
            ),
            recommendation=recommendation,
            passed=passed,
        )