"""
engineering_review_payload.py
 
Builds the controlled JSON-serializable engineering
evidence package supplied to LLM review synthesis.
 
The payload intentionally excludes the complete optimization
candidate population. That population may contain thousands
of candidates and is already represented by deterministic
optimization insights, selection metadata, and summary
counts.
 
The LLM receives:
 
- validated requirements;
- selected design(s);
- optimization-selection information;
- material/process information;
- deterministic insights and evidence;
- deterministic assessments and rule outcomes;
- deterministic review structure;
- known model limitations.
 
No engineering calculation occurs here.
"""
import math
from datetime import date
 
from dataclasses import (
    fields,
    is_dataclass,
)
from enum import Enum
 
from models.engineering_review import (
    EngineeringReview,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
 
 
class EngineeringReviewPayloadBuilder:
    """
    Build the grounded LLM input package for engineering
    review synthesis.
    """
 
    @classmethod
    def build(
        cls,
        *,
        source: EngineeringReviewSource,
        deterministic_review: EngineeringReview,
    ) -> dict:
        """
        Build a JSON-serializable grounded review payload.
        """
 
        if not isinstance(
            source,
            EngineeringReviewSource,
        ):
            raise ValueError(
                "'source' must be an "
                "EngineeringReviewSource object."
            )
 
        if not isinstance(
            deterministic_review,
            EngineeringReview,
        ):
            raise ValueError(
                "'deterministic_review' must be an "
                "EngineeringReview object."
            )
 
        cls._validate_review_traceability(
            source=source,
            review=deterministic_review,
        )
 
        context = source.context
 
        return {
            "review_contract": {
                "deterministic_status": (
                    deterministic_review.status.value
                ),
                "status_is_locked": True,
                "engineering_evidence_is_locked": True,
                "assessment_outcomes_are_locked": True,
                "allowed_ai_outputs": [
                    "executive_summary",
                    "section_summaries",
                    "engineering_tradeoffs",
                ],
            },
 
            "requirements": cls._to_json_value(
                context.requirements
            ),
 
            "selected_designs": [
                cls._to_json_value(
                    candidate
                )
                for candidate
                in context.selected_candidates
            ],
 
            "optimization": {
                "selection_mode": (
                    context.selection_mode.value
                ),
                "selection_configuration": (
                    cls._to_json_value(
                        context
                        .selection_configuration
                    )
                ),
                "selected_candidate_count": (
                    context.selected_candidate_count
                ),
                "feasible_candidate_count": (
                    context.feasible_candidate_count
                ),
                "rejected_candidate_count": (
                    context.rejected_candidate_count
                ),
                "total_candidate_count": (
                    context.total_candidate_count
                ),
                "feasibility_rate_percent": (
                    context.feasibility_rate
                ),
                "selected_material": (
                    context.selected_material
                ),
                "selected_process": (
                    context.selected_process
                ),
            },
 
            "known_limitations": list(
                context.known_limitations
            ),
 
            "insights": [
                {
                    "insight_id": insight.insight_id,
                    "category": (
                        insight.category.value
                    ),
                    "severity": (
                        insight.severity.value
                    ),
                    "title": insight.title,
                    "summary": insight.summary,
                    "source": insight.source,
                    "evidence": [
                        cls._to_json_value(
                            evidence
                        )
                        for evidence
                        in insight.evidence
                    ],
                }
                for insight in source.insights
            ],
 
            "assessments": [
                {
                    "assessment_id": (
                        assessment.assessment_id
                    ),
                    "rule_id": assessment.rule_id,
                    "category": (
                        assessment.category.value
                    ),
                    "severity": (
                        assessment.severity.value
                    ),
                    "passed": assessment.passed,
                    "title": assessment.title,
                    "summary": assessment.summary,
                    "recommendation": (
                        assessment.recommendation
                    ),
                    "source_insight_ids": list(
                        assessment
                        .source_insight_ids
                    ),
                    "evidence": [
                        cls._to_json_value(
                            evidence
                        )
                        for evidence
                        in assessment.evidence
                    ],
                }
                for assessment
                in source.assessments
            ],
 
            "deterministic_review": {
                "status": (
                    deterministic_review
                    .status
                    .value
                ),
                "executive_summary": (
                    deterministic_review
                    .executive_summary
                ),
                "strengths": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in deterministic_review
                    .strengths
                ],
                "concerns": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in deterministic_review
                    .concerns
                ],
                "sections": [
                    {
                        "category": (
                            section.category.value
                        ),
                        "status": (
                            section.status.value
                        ),
                        "summary": (
                            section.summary
                        ),
                        "source_assessment_ids": list(
                            section
                            .source_assessment_ids
                        ),
                        "source_insight_ids": list(
                            section
                            .source_insight_ids
                        ),
                    }
                    for section
                    in deterministic_review.sections
                ],
                "required_actions": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in deterministic_review
                    .required_actions
                ],
                "validation_requirements": [
                    cls._review_item_to_dict(
                        item
                    )
                    for item
                    in deterministic_review
                    .validation_requirements
                ],
            },
        }
 
    @staticmethod
    def _review_item_to_dict(
        item,
    ) -> dict:
        """
        Convert one deterministic review item to a compact
        JSON-safe dictionary.
        """
 
        return {
            "item_id": item.item_id,
            "category": item.category.value,
            "severity": item.severity.value,
            "title": item.title,
            "summary": item.summary,
            "consequence": item.consequence,
            "verification": item.verification,
            "source_assessment_ids": list(
                item.source_assessment_ids
            ),
            "source_insight_ids": list(
                item.source_insight_ids
            ),
        }
 
    @classmethod
    def _to_json_value(
        cls,
        value,
    ):
        """
        Recursively convert supported project-domain values
        to plain JSON-compatible Python values.
 
        Unsupported values are rejected rather than silently
        discarded or converted to arbitrary strings.
        """
 
        if value is None:
            return None
 
        if isinstance(
            value,
            bool,
        ):
            return value
 
        if isinstance(
            value,
            int,
        ):
            return value
 
        if isinstance(
            value,
            float,
        ):
            if not math.isfinite(
                value
            ):
                raise ValueError(
                    "Non-finite numerical value cannot be "
                    "included in the engineering-review "
                    "LLM payload."
                )
 
            return float(
                f"{value:.12g}"
            )
 
        if isinstance(
            value,
            str,
        ):
            return value

        if isinstance(
            value,
            date,
        ):
            return value.isoformat()
 
        if isinstance(
            value,
            Enum,
        ):
            return value.value
 
        if is_dataclass(
            value
        ):
            return {
                field.name: cls._to_json_value(
                    getattr(
                        value,
                        field.name,
                    )
                )
                for field in fields(value)
            }
 
        if isinstance(
            value,
            (
                tuple,
                list,
            ),
        ):
            return [
                cls._to_json_value(
                    item
                )
                for item in value
            ]
 
        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): cls._to_json_value(
                    item
                )
                for key, item
                in value.items()
            }
 
        raise ValueError(
            "Unsupported value in engineering-review "
            "LLM payload: "
            f"{type(value).__name__}."
        )
 
    @staticmethod
    def _validate_review_traceability(
        *,
        source: EngineeringReviewSource,
        review: EngineeringReview,
    ) -> None:
        """
        Confirm that the deterministic review and source
        package represent the same complete intelligence
        population.
        """
 
        expected_assessment_ids = tuple(
            assessment.assessment_id
            for assessment
            in source.assessments
        )
 
        expected_insight_ids = tuple(
            insight.insight_id
            for insight
            in source.insights
        )
 
        if (
            review.source_assessment_ids
            != expected_assessment_ids
        ):
            raise ValueError(
                "Deterministic review assessment sources "
                "do not match the engineering-review "
                "source package."
            )
 
        if (
            review.source_insight_ids
            != expected_insight_ids
        ):
            raise ValueError(
                "Deterministic review insight sources "
                "do not match the engineering-review "
                "source package."
            )