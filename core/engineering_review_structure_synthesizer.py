"""
engineering_review_structure_synthesizer.py
 
Deterministically converts EngineeringReviewSource into
structured engineering-review components.
 
This module:
 
- does not perform engineering calculations;
- does not introduce new engineering acceptance rules;
- does not invoke an LLM;
- does not replace deterministic assessments.
 
It reorganizes existing engineering intelligence into
strengths, concerns, category sections, deterministic
actions, and validation requirements.
"""
 
from dataclasses import dataclass
 
from core.engineering_review_status_resolver import (
    EngineeringReviewStatusResolver,
)
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_insight import (
    EngineeringInsight,
)
from models.engineering_review_item import (
    EngineeringReviewItem,
)
from models.engineering_review_section import (
    EngineeringReviewSection,
)
from models.engineering_review_source import (
    EngineeringReviewSource,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
@dataclass(frozen=True)
class EngineeringReviewComponents:
    """
    Deterministically generated components used to assemble
    a complete EngineeringReview.
    """
 
    strengths: tuple[
        EngineeringReviewItem,
        ...,
    ] = ()
 
    concerns: tuple[
        EngineeringReviewItem,
        ...,
    ] = ()
 
    sections: tuple[
        EngineeringReviewSection,
        ...,
    ] = ()
 
    required_actions: tuple[
        EngineeringReviewItem,
        ...,
    ] = ()
 
    validation_requirements: tuple[
        EngineeringReviewItem,
        ...,
    ] = ()
 
 
class EngineeringReviewStructureSynthesizer:
    """
    Build structured review components from deterministic
    engineering intelligence.
    """
 
    @classmethod
    def synthesize(
        cls,
        source: EngineeringReviewSource,
    ) -> EngineeringReviewComponents:
        """
        Build all deterministic review components.
        """
 
        if not isinstance(
            source,
            EngineeringReviewSource,
        ):
            raise ValueError(
                "'source' must be an "
                "EngineeringReviewSource object."
            )
 
        strengths = cls._build_strengths(
            source
        )
 
        concerns = cls._build_concerns(
            source
        )
 
        required_actions = (
            cls._build_required_actions(
                source
            )
        )
 
        validation_requirements = (
            cls._build_validation_requirements(
                source
            )
        )
 
        sections = cls._build_sections(
            source=source,
            strengths=strengths,
            concerns=concerns,
        )
 
        return EngineeringReviewComponents(
            strengths=strengths,
            concerns=concerns,
            sections=sections,
            required_actions=(
                required_actions
            ),
            validation_requirements=(
                validation_requirements
            ),
        )
 
    @classmethod
    def _build_strengths(
        cls,
        source: EngineeringReviewSource,
    ) -> tuple[
        EngineeringReviewItem,
        ...,
    ]:
        """
        Convert confirmed successful assessments into
        top-level design strengths.
 
        A passing WARNING is intentionally not classified
        as a strength because it still requires engineering
        attention.
        """
 
        strengths: list[
            EngineeringReviewItem
        ] = []
 
        for assessment in source.assessments:
            if (
                assessment.passed
                and assessment.severity
                == EngineeringSeverity.SUCCESS
            ):
                strengths.append(
                    cls._item_from_assessment(
                        assessment=assessment,
                        item_prefix="strength",
                    )
                )
 
        for insight in source.unassessed_insights:
            if (
                insight.severity
                == EngineeringSeverity.SUCCESS
            ):
                strengths.append(
                    cls._item_from_insight(
                        insight=insight,
                        item_prefix="strength",
                    )
                )
 
        return tuple(
            strengths
        )
 
    @classmethod
    def _build_concerns(
        cls,
        source: EngineeringReviewSource,
    ) -> tuple[
        EngineeringReviewItem,
        ...,
    ]:
        """
        Build top-level concerns from deterministic
        assessment outcomes and unassessed warning or
        critical insights.
        """
 
        concerns: list[
            EngineeringReviewItem
        ] = []
 
        for assessment in source.assessments:
            if cls._assessment_is_concern(
                assessment
            ):
                concerns.append(
                    cls._item_from_assessment(
                        assessment=assessment,
                        item_prefix="concern",
                    )
                )
 
        for insight in source.unassessed_insights:
            if insight.severity in {
                EngineeringSeverity.WARNING,
                EngineeringSeverity.CRITICAL,
            }:
                concerns.append(
                    cls._item_from_insight(
                        insight=insight,
                        item_prefix="concern",
                    )
                )
 
        return tuple(
            concerns
        )
 
    @classmethod
    def _build_required_actions(
        cls,
        source: EngineeringReviewSource,
    ) -> tuple[
        EngineeringReviewItem,
        ...,
    ]:
        """
        Preserve deterministic recommendations as required
        review actions.
 
        Failed INFO assessments are handled separately as
        validation requirements because they represent
        missing evidence or missing evaluation limits.
        """
 
        actions: list[
            EngineeringReviewItem
        ] = []
 
        for assessment in source.assessments:
            if not assessment.has_recommendation:
                continue
 
            if (
                not assessment.passed
                and assessment.severity
                == EngineeringSeverity.INFO
            ):
                continue
 
            actions.append(
                EngineeringReviewItem(
                    item_id=(
                        "action."
                        f"{assessment.assessment_id}"
                    ),
                    category=assessment.category,
                    severity=assessment.severity,
                    title=(
                        f"Action — {assessment.title}"
                    ),
                    summary=(
                        assessment.recommendation
                    ),
                    source_assessment_ids=(
                        assessment.assessment_id,
                    ),
                    source_insight_ids=(
                        assessment.source_insight_ids
                    ),
                )
            )
 
        return tuple(
            actions
        )
 
    @classmethod
    def _build_validation_requirements(
        cls,
        source: EngineeringReviewSource,
    ) -> tuple[
        EngineeringReviewItem,
        ...,
    ]:
        """
        Build explicit validation requirements from:
 
        - failed informational assessments having a
          deterministic recommendation;
        - declared model limitations.
 
        This does not create a new engineering threshold.
        """
 
        requirements: list[
            EngineeringReviewItem
        ] = []
 
        for assessment in source.assessments:
            if not (
                not assessment.passed
                and assessment.severity
                == EngineeringSeverity.INFO
                and assessment.has_recommendation
            ):
                continue
 
            requirements.append(
                EngineeringReviewItem(
                    item_id=(
                        "validation."
                        f"{assessment.assessment_id}"
                    ),
                    category=assessment.category,
                    severity=assessment.severity,
                    title=(
                        "Validation required — "
                        f"{assessment.title}"
                    ),
                    summary=(
                        assessment.recommendation
                    ),
                    source_assessment_ids=(
                        assessment.assessment_id,
                    ),
                    source_insight_ids=(
                        assessment.source_insight_ids
                    ),
                )
            )
 
        for insight in source.unassessed_insights:
            if (
                insight.category
                != EngineeringCategory.MODEL_LIMITATION
            ):
                continue
 
            requirements.append(
                EngineeringReviewItem(
                    item_id=(
                        "validation."
                        f"{insight.insight_id}"
                    ),
                    category=insight.category,
                    severity=insight.severity,
                    title=insight.title,
                    summary=insight.summary,
                    verification=(
                        "Review the declared model "
                        "limitation and determine the "
                        "appropriate validation before "
                        "design release."
                    ),
                    source_insight_ids=(
                        insight.insight_id,
                    ),
                )
            )
 
        return tuple(
            requirements
        )
 
    @classmethod
    def _build_sections(
        cls,
        *,
        source: EngineeringReviewSource,
        strengths: tuple[
            EngineeringReviewItem,
            ...,
        ],
        concerns: tuple[
            EngineeringReviewItem,
            ...,
        ],
    ) -> tuple[
        EngineeringReviewSection,
        ...,
    ]:
        """
        Build one section for every engineering category
        represented by an insight or assessment.
        """
 
        strength_by_assessment_id = (
            cls._index_items_by_assessment(
                strengths
            )
        )
 
        concern_by_assessment_id = (
            cls._index_items_by_assessment(
                concerns
            )
        )
 
        strength_by_insight_id = (
            cls._index_items_by_insight(
                strengths
            )
        )
 
        concern_by_insight_id = (
            cls._index_items_by_insight(
                concerns
            )
        )
 
        sections: list[
            EngineeringReviewSection
        ] = []
 
        for category in EngineeringCategory:
            category_assessments = (
                source.assessments_for_category(
                    category
                )
            )
 
            category_insights = (
                source.insights_for_category(
                    category
                )
            )
 
            if (
                not category_assessments
                and not category_insights
            ):
                continue
 
            findings: list[
                EngineeringReviewItem
            ] = []
 
            for assessment in (
                category_assessments
            ):
                strength = (
                    strength_by_assessment_id.get(
                        assessment.assessment_id
                    )
                )
 
                if strength is not None:
                    findings.append(
                        strength
                    )
                    continue
 
                concern = (
                    concern_by_assessment_id.get(
                        assessment.assessment_id
                    )
                )
 
                if concern is not None:
                    findings.append(
                        concern
                    )
                    continue
 
                findings.append(
                    cls._item_from_assessment(
                        assessment=assessment,
                        item_prefix="observation",
                    )
                )
 
            for insight in category_insights:
                if (
                    insight.insight_id
                    not in source
                    .unassessed_insight_ids
                ):
                    continue
 
                strength = (
                    strength_by_insight_id.get(
                        insight.insight_id
                    )
                )
 
                if strength is not None:
                    findings.append(
                        strength
                    )
                    continue
 
                concern = (
                    concern_by_insight_id.get(
                        insight.insight_id
                    )
                )
 
                if concern is not None:
                    findings.append(
                        concern
                    )
                    continue
 
                findings.append(
                    cls._item_from_insight(
                        insight=insight,
                        item_prefix="observation",
                    )
                )
 
            section_status = (
                EngineeringReviewStatusResolver
                .resolve(
                    category_assessments
                )
            )
 
            sections.append(
                EngineeringReviewSection(
                    category=category,
                    status=section_status,
                    summary=(
                        cls._build_section_summary(
                            category=category,
                            assessment_count=len(
                                category_assessments
                            ),
                            insight_count=len(
                                category_insights
                            ),
                            status=section_status,
                        )
                    ),
                    findings=tuple(
                        findings
                    ),
                    source_assessment_ids=tuple(
                        assessment.assessment_id
                        for assessment
                        in category_assessments
                    ),
                    source_insight_ids=tuple(
                        insight.insight_id
                        for insight
                        in category_insights
                    ),
                )
            )
 
        return tuple(
            sections
        )
 
    @staticmethod
    def _assessment_is_concern(
        assessment: EngineeringAssessment,
    ) -> bool:
        """
        Return True when an assessment requires attention.
 
        Failed assessments always require attention.
        Passing WARNING or CRITICAL assessments also remain
        concerns rather than strengths.
        """
 
        return (
            not assessment.passed
            or assessment.severity
            in {
                EngineeringSeverity.WARNING,
                EngineeringSeverity.CRITICAL,
            }
        )
 
    @staticmethod
    def _item_from_assessment(
        *,
        assessment: EngineeringAssessment,
        item_prefix: str,
    ) -> EngineeringReviewItem:
        """
        Convert one assessment into a traceable review item
        without changing its engineering meaning.
        """
 
        return EngineeringReviewItem(
            item_id=(
                f"{item_prefix}."
                f"{assessment.assessment_id}"
            ),
            category=assessment.category,
            severity=assessment.severity,
            title=assessment.title,
            summary=assessment.summary,
            source_assessment_ids=(
                assessment.assessment_id,
            ),
            source_insight_ids=(
                assessment.source_insight_ids
            ),
        )
 
    @staticmethod
    def _item_from_insight(
        *,
        insight: EngineeringInsight,
        item_prefix: str,
    ) -> EngineeringReviewItem:
        """
        Convert one unassessed insight into a traceable
        review item without modifying its deterministic
        content.
        """
 
        return EngineeringReviewItem(
            item_id=(
                f"{item_prefix}."
                f"{insight.insight_id}"
            ),
            category=insight.category,
            severity=insight.severity,
            title=insight.title,
            summary=insight.summary,
            source_insight_ids=(
                insight.insight_id,
            ),
        )
 
    @staticmethod
    def _index_items_by_assessment(
        items: tuple[
            EngineeringReviewItem,
            ...,
        ],
    ) -> dict[
        str,
        EngineeringReviewItem,
    ]:
        """
        Build an assessment-ID lookup for generated items.
        """
 
        index: dict[
            str,
            EngineeringReviewItem,
        ] = {}
 
        for item in items:
            for assessment_id in (
                item.source_assessment_ids
            ):
                index[
                    assessment_id
                ] = item
 
        return index
 
    @staticmethod
    def _index_items_by_insight(
        items: tuple[
            EngineeringReviewItem,
            ...,
        ],
    ) -> dict[
        str,
        EngineeringReviewItem,
    ]:
        """
        Build an insight-ID lookup for generated items.
        """
 
        index: dict[
            str,
            EngineeringReviewItem,
        ] = {}
 
        for item in items:
            if item.source_assessment_ids:
                continue
 
            for insight_id in (
                item.source_insight_ids
            ):
                index[
                    insight_id
                ] = item
 
        return index
 
    @staticmethod
    def _build_section_summary(
        *,
        category: EngineeringCategory,
        assessment_count: int,
        insight_count: int,
        status,
    ) -> str:
        """
        Build a deliberately factual deterministic section
        summary.
 
        Rich engineering narrative will be added by the
        later synthesis layer.
        """
 
        return (
            f"The {category.value} review contains "
            f"{assessment_count} deterministic "
            f"assessment(s) and {insight_count} "
            f"engineering insight(s). Consolidated "
            f"status: {status.value}."
        )