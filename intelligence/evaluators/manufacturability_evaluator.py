"""
manufacturability_evaluator.py
 
Adapter connecting the existing deterministic
manufacturing-rule engine to the engineering-assessment
layer.
 
This evaluator does not define or duplicate manufacturing
thresholds. It delegates geometry checking to the existing
manufacturing rule engine and converts the result into
structured EngineeringAssessment objects.
"""
 
from intelligence.evaluators.base_evaluator import (
    EngineeringEvaluator,
)
from manufacturing.rule_engine import (
    assess_manufacturability,
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
from models.process_capability import (
    ProcessCapability,
)
 
 
class ManufacturabilityEvaluator(
    EngineeringEvaluator,
):
    """
    Evaluate selected heat-sink candidates using an
    existing manufacturing process capability.
 
    The capability is injected explicitly so this evaluator
    remains independent of the process database and can be
    tested without hidden configuration lookup.
    """
 
    def __init__(
        self,
        capability: ProcessCapability,
    ) -> None:
        """
        Create the manufacturability evaluator.
        """
 
        if not isinstance(
            capability,
            ProcessCapability,
        ):
            raise ValueError(
                "'capability' must be a "
                "ProcessCapability object."
            )
 
        self._capability = capability
 
    @property
    def capability(
        self,
    ) -> ProcessCapability:
        """
        Return the configured manufacturing capability.
        """
 
        return self._capability
 
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
        Assess every selected candidate against the
        configured manufacturing capability.
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
 
        constraints = (
            context.requirements.constraints
        )
 
        if constraints is None:
            raise ValueError(
                "Manufacturability evaluation requires "
                "engineering constraints."
            )
 
        maximum_total_height = (
            constraints.max_height
        )
 
        if maximum_total_height is None:
            raise ValueError(
                "Manufacturability evaluation requires "
                "'constraints.max_height'."
            )
 
        assessments: list[
            EngineeringAssessment
        ] = []
 
        for candidate_index, candidate in enumerate(
            context.selected_candidates,
            start=1,
        ):
            manufacturing_result = (
                assess_manufacturability(
                    candidate=candidate,
                    capability=self._capability,
                    maximum_total_height=(
                        maximum_total_height
                    ),
                )
            )
 
            assessments.append(
                self._adapt_result(
                    candidate_index=(
                        candidate_index
                    ),
                    manufacturing_result=(
                        manufacturing_result
                    ),
                    maximum_total_height=(
                        maximum_total_height
                    ),
                )
            )
 
        return tuple(
            assessments
        )
 
    @staticmethod
    def _adapt_result(
        candidate_index: int,
        manufacturing_result,
        maximum_total_height: float,
    ) -> EngineeringAssessment:
        """
        Convert an existing ManufacturingAssessment into
        one structured EngineeringAssessment.
        """
 
        if not manufacturing_result.is_feasible:
            severity = (
                EngineeringSeverity.CRITICAL
            )
 
            title = (
                "Selected design is not manufacturable"
            )
 
            summary = (
                "The selected design violates one or more "
                "configured manufacturing capability "
                "rules."
            )
 
            recommendation = (
                "Revise the selected geometry or use a "
                "validated manufacturing capability that "
                "supports the required dimensions."
            )
 
            passed = False
 
        elif manufacturing_result.warnings:
            severity = (
                EngineeringSeverity.WARNING
            )
 
            title = (
                "Selected design requires "
                "manufacturing review"
            )
 
            summary = (
                "The selected design satisfies the "
                "configured manufacturing rules but has "
                "one or more manufacturing warnings."
            )
 
            recommendation = (
                "Complete supplier or manufacturing "
                "engineering review before release."
            )
 
            passed = True
 
        else:
            severity = (
                EngineeringSeverity.SUCCESS
            )
 
            title = (
                "Selected design passes "
                "manufacturability checks"
            )
 
            summary = (
                "The selected design satisfies all "
                "configured manufacturing capability "
                "rules without warnings."
            )
 
            recommendation = ""
 
            passed = True
 
        evidence: list[
            EngineeringEvidence
        ] = [
            EngineeringEvidence(
                key="candidate_index",
                value=candidate_index,
            ),
            EngineeringEvidence(
                key="manufacturing_process",
                value=(
                    manufacturing_result.process
                ),
            ),
            EngineeringEvidence(
                key="material",
                value=(
                    manufacturing_result.material
                ),
            ),
            EngineeringEvidence(
                key="manufacturing_status",
                value=(
                    manufacturing_result.status
                ),
            ),
            EngineeringEvidence(
                key="is_feasible",
                value=(
                    manufacturing_result.is_feasible
                ),
            ),
            EngineeringEvidence(
                key="maximum_total_height",
                value=maximum_total_height,
                unit="mm",
            ),
            EngineeringEvidence(
                key="checked_rule_count",
                value=len(
                    manufacturing_result.checked_rules
                ),
            ),
            EngineeringEvidence(
                key="violation_count",
                value=len(
                    manufacturing_result.violations
                ),
            ),
            EngineeringEvidence(
                key="warning_count",
                value=len(
                    manufacturing_result.warnings
                ),
            ),
        ]
 
        for violation_index, violation in enumerate(
            manufacturing_result.violations,
            start=1,
        ):
            evidence.append(
                EngineeringEvidence(
                    key=(
                        f"violation_{violation_index}"
                    ),
                    value=violation,
                )
            )
 
        for warning_index, warning in enumerate(
            manufacturing_result.warnings,
            start=1,
        ):
            evidence.append(
                EngineeringEvidence(
                    key=(
                        f"warning_{warning_index}"
                    ),
                    value=warning,
                )
            )
 
        return EngineeringAssessment(
            assessment_id=(
                "manufacturing."
                f"selected_candidate_{candidate_index}"
            ),
            rule_id=(
                "manufacturing."
                "configured_process_capability"
            ),
            severity=severity,
            category=(
                EngineeringCategory.MANUFACTURING
            ),
            title=title,
            summary=summary,
            evidence=tuple(
                evidence
            ),
            source_insight_ids=(
                "manufacturing.process_recorded",
                "geometry.selected_design_dimensions",
            ),
            recommendation=recommendation,
            passed=passed,
        )