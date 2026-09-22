"""
thermal_margin_evaluator.py
 
Deterministic evaluator interpreting the thermal margin of
selected design candidates.
 
The evaluator does not recalculate temperatures or thermal
resistance. It compares optimizer-produced results against
the explicitly supplied maximum allowable base temperature.
"""
 
import math
 
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
 
 
class ThermalMarginEvaluator(
    EngineeringEvaluator,
):
    """
    Assess selected candidates against the explicitly
    supplied maximum allowable base temperature.
 
    The warning margin is injected so the evaluator does
    not contain an untraceable thermal-design threshold.
    """
 
    def __init__(
        self,
        warning_margin_temperature: float,
    ) -> None:
        """
        Create the evaluator.
 
        warning_margin_temperature:
            A positive temperature margin, in °C, at or
            below which a passing design requires thermal
            attention.
        """
 
        if not isinstance(
            warning_margin_temperature,
            (
                float,
                int,
            ),
        ):
            raise ValueError(
                "'warning_margin_temperature' must be "
                "numeric."
            )
 
        normalized_warning_margin = float(
            warning_margin_temperature
        )
 
        if not math.isfinite(
            normalized_warning_margin
        ):
            raise ValueError(
                "'warning_margin_temperature' must be "
                "finite."
            )
 
        if normalized_warning_margin <= 0.0:
            raise ValueError(
                "'warning_margin_temperature' must be "
                "greater than zero."
            )
 
        self._warning_margin_temperature = (
            normalized_warning_margin
        )
 
    @property
    def warning_margin_temperature(
        self,
    ) -> float:
        """
        Return the configured warning margin in °C.
        """
 
        return self._warning_margin_temperature
 
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
        Evaluate thermal compliance for every selected
        candidate.
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
 
        operating_requirements = (
            context.requirements.requirements
        )
 
        maximum_base_temperature = (
            operating_requirements
            .maximum_base_temperature
        )
 
        assessments: list[
            EngineeringAssessment
        ] = []
 
        for candidate_index, candidate in enumerate(
            context.selected_candidates,
            start=1,
        ):
            assessments.append(
                self._evaluate_candidate(
                    candidate_index=(
                        candidate_index
                    ),
                    estimated_base_temperature=(
                        candidate
                        .estimated_base_temperature
                    ),
                    thermal_resistance=(
                        candidate.thermal_resistance
                    ),
                    heat_load=(
                        operating_requirements
                        .heat_load
                    ),
                    ambient_temperature=(
                        operating_requirements
                        .ambient_temperature
                    ),
                    maximum_base_temperature=(
                        maximum_base_temperature
                    ),
                )
            )
 
        return tuple(
            assessments
        )
 
    def _evaluate_candidate(
        self,
        *,
        candidate_index: int,
        estimated_base_temperature: float,
        thermal_resistance: float,
        heat_load: float | None,
        ambient_temperature: float | None,
        maximum_base_temperature: float | None,
    ) -> EngineeringAssessment:
        """
        Convert one selected candidate's thermal result into
        a structured assessment.
        """
 
        evidence: list[
            EngineeringEvidence
        ] = [
            EngineeringEvidence(
                key="candidate_index",
                value=candidate_index,
            ),
            EngineeringEvidence(
                key="estimated_base_temperature",
                value=(
                    estimated_base_temperature
                ),
                unit="°C",
            ),
            EngineeringEvidence(
                key="thermal_resistance",
                value=thermal_resistance,
                unit="K/W",
            ),
            EngineeringEvidence(
                key="warning_margin_temperature",
                value=(
                    self
                    ._warning_margin_temperature
                ),
                unit="°C",
            ),
        ]
 
        if heat_load is not None:
            evidence.append(
                EngineeringEvidence(
                    key="heat_load",
                    value=heat_load,
                    unit="W",
                )
            )
 
        if ambient_temperature is not None:
            evidence.append(
                EngineeringEvidence(
                    key="ambient_temperature",
                    value=ambient_temperature,
                    unit="°C",
                )
            )
 
        if maximum_base_temperature is None:
            return EngineeringAssessment(
                assessment_id=(
                    "thermal."
                    f"selected_candidate_{candidate_index}"
                ),
                rule_id=(
                    "thermal."
                    "maximum_base_temperature_margin"
                ),
                severity=(
                    EngineeringSeverity.INFO
                ),
                category=(
                    EngineeringCategory.THERMAL
                ),
                title=(
                    "Thermal compliance was not evaluated"
                ),
                summary=(
                    "No maximum allowable base temperature "
                    "was supplied, so the selected design's "
                    "thermal margin cannot be determined."
                ),
                evidence=tuple(
                    evidence
                ),
                source_insight_ids=(
                    "thermal."
                    "selected_design_performance",
                ),
                recommendation=(
                    "Provide the maximum allowable heat-sink "
                    "base temperature to enable thermal "
                    "margin assessment."
                ),
                passed=False,
            )
 
        temperature_margin = (
            maximum_base_temperature
            - estimated_base_temperature
        )
 
        evidence.extend(
            (
                EngineeringEvidence(
                    key="maximum_base_temperature",
                    value=maximum_base_temperature,
                    unit="°C",
                ),
                EngineeringEvidence(
                    key="temperature_margin",
                    value=temperature_margin,
                    unit="°C",
                ),
            )
        )
 
        if temperature_margin < 0.0:
            severity = (
                EngineeringSeverity.CRITICAL
            )
 
            title = (
                "Selected design exceeds the allowable "
                "base temperature"
            )
 
            summary = (
                "The estimated base temperature exceeds "
                "the explicitly supplied maximum allowable "
                "base temperature."
            )
 
            recommendation = (
                "Reduce thermal resistance, reduce heat "
                "load, improve airflow, increase available "
                "heat-transfer area, or revise the allowable "
                "temperature only when supported by the "
                "component and application limits."
            )
 
            passed = False
 
        elif (
            temperature_margin
            <= self._warning_margin_temperature
        ):
            severity = (
                EngineeringSeverity.WARNING
            )
 
            title = (
                "Selected design has limited thermal margin"
            )
 
            summary = (
                "The estimated base temperature remains "
                "within the allowable limit, but the "
                "remaining temperature margin is at or "
                "below the configured warning margin."
            )
 
            recommendation = (
                "Review operating-condition uncertainty, "
                "thermal-interface resistance, fouling, "
                "airflow tolerance, and manufacturing "
                "variation before design release."
            )
 
            passed = True
 
        else:
            severity = (
                EngineeringSeverity.SUCCESS
            )
 
            title = (
                "Selected design passes the thermal "
                "temperature limit"
            )
 
            summary = (
                "The estimated base temperature remains "
                "below the allowable limit with more than "
                "the configured warning margin."
            )
 
            recommendation = ""
 
            passed = True
 
        return EngineeringAssessment(
            assessment_id=(
                "thermal."
                f"selected_candidate_{candidate_index}"
            ),
            rule_id=(
                "thermal."
                "maximum_base_temperature_margin"
            ),
            severity=severity,
            category=(
                EngineeringCategory.THERMAL
            ),
            title=title,
            summary=summary,
            evidence=tuple(
                evidence
            ),
            source_insight_ids=(
                "thermal."
                "selected_design_performance",
            ),
            recommendation=recommendation,
            passed=passed,
        )