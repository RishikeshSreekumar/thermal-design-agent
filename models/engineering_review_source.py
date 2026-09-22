"""
engineering_review_source.py
 
Validated and lossless source package supplied to
engineering-review synthesis.
 
The package preserves the complete deterministic
engineering-intelligence result while providing convenient
and traceable access to its context, insights, and
assessments.
 
It performs no engineering calculation and no LLM
operation.
"""
 
from dataclasses import dataclass
 
from models.engineering_assessment import (
    EngineeringAssessment,
)
from models.engineering_category import (
    EngineeringCategory,
)
from models.engineering_context import (
    EngineeringContext,
)
from models.engineering_insight import (
    EngineeringInsight,
)
from models.engineering_intelligence_result import (
    EngineeringIntelligenceResult,
)
from models.engineering_severity import (
    EngineeringSeverity,
)
 
 
@dataclass(frozen=True)
class EngineeringReviewSource:
    """
    Complete deterministic source population available to
    engineering-review synthesis.
    """
 
    intelligence_result: EngineeringIntelligenceResult
 
    insight_index: dict[
        str,
        EngineeringInsight,
    ]
 
    assessment_index: dict[
        str,
        EngineeringAssessment,
    ]
 
    assessed_insight_ids: tuple[
        str,
        ...,
    ] = ()
 
    unassessed_insight_ids: tuple[
        str,
        ...,
    ] = ()
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate the complete engineering-review source
        package.
        """
 
        if not isinstance(
            self.intelligence_result,
            EngineeringIntelligenceResult,
        ):
            raise ValueError(
                "'intelligence_result' must be an "
                "EngineeringIntelligenceResult object."
            )
 
        self._validate_insight_index()
 
        self._validate_assessment_index()
 
        assessed_ids = (
            self._validate_insight_id_collection(
                insight_ids=self.assessed_insight_ids,
                field_name="assessed_insight_ids",
            )
        )
 
        unassessed_ids = (
            self._validate_insight_id_collection(
                insight_ids=self.unassessed_insight_ids,
                field_name="unassessed_insight_ids",
            )
        )
 
        object.__setattr__(
            self,
            "assessed_insight_ids",
            assessed_ids,
        )
 
        object.__setattr__(
            self,
            "unassessed_insight_ids",
            unassessed_ids,
        )
 
        overlap = (
            set(assessed_ids)
            & set(unassessed_ids)
        )
 
        if overlap:
            raise ValueError(
                "Assessed and unassessed insight "
                "collections cannot overlap."
            )
 
        expected_ids = set(
            self.insight_index
        )
 
        packaged_ids = (
            set(assessed_ids)
            | set(unassessed_ids)
        )
 
        if packaged_ids != expected_ids:
            raise ValueError(
                "Assessed and unassessed insight "
                "collections must together contain every "
                "source insight exactly once."
            )
 
        self._validate_assessment_references()
 
    @property
    def context(
        self,
    ) -> EngineeringContext:
        """
        Return the complete engineering context.
        """
 
        return self.intelligence_result.context
 
    @property
    def insights(
        self,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Return all deterministic insights in original order.
        """
 
        return self.intelligence_result.insights
 
    @property
    def assessments(
        self,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Return all deterministic assessments in original
        order.
        """
 
        return self.intelligence_result.assessments
 
    @property
    def passed_assessments(
        self,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Return all assessments whose deterministic rules
        passed.
        """
 
        return (
            self.intelligence_result
            .passed_assessments
        )
 
    @property
    def failed_assessments(
        self,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Return all assessments whose deterministic rules
        did not pass.
        """
 
        return (
            self.intelligence_result
            .failed_assessments
        )
 
    @property
    def assessed_insights(
        self,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Return insights referenced by at least one
        deterministic assessment.
        """
 
        assessed_ids = set(
            self.assessed_insight_ids
        )
 
        return tuple(
            insight
            for insight in self.insights
            if insight.insight_id in assessed_ids
        )
 
    @property
    def unassessed_insights(
        self,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Return insights that are not referenced by any
        deterministic assessment.
        """
 
        unassessed_ids = set(
            self.unassessed_insight_ids
        )
 
        return tuple(
            insight
            for insight in self.insights
            if insight.insight_id in unassessed_ids
        )
 
    @property
    def has_failed_assessments(
        self,
    ) -> bool:
        """
        Return True when at least one assessment failed.
        """
 
        return bool(
            self.failed_assessments
        )
 
    @property
    def has_unassessed_insights(
        self,
    ) -> bool:
        """
        Return True when at least one insight has no
        assessment reference.
        """
 
        return bool(
            self.unassessed_insight_ids
        )
 
    def get_insight(
        self,
        insight_id: str,
    ) -> EngineeringInsight:
        """
        Return one deterministic insight by ID.
        """
 
        normalized_id = (
            self._normalize_lookup_id(
                value=insight_id,
                field_name="insight_id",
            )
        )
 
        try:
            return self.insight_index[
                normalized_id
            ]
 
        except KeyError as exc:
            raise KeyError(
                "Unknown engineering insight ID: "
                f"'{normalized_id}'."
            ) from exc
 
    def get_assessment(
        self,
        assessment_id: str,
    ) -> EngineeringAssessment:
        """
        Return one deterministic assessment by ID.
        """
 
        normalized_id = (
            self._normalize_lookup_id(
                value=assessment_id,
                field_name="assessment_id",
            )
        )
 
        try:
            return self.assessment_index[
                normalized_id
            ]
 
        except KeyError as exc:
            raise KeyError(
                "Unknown engineering assessment ID: "
                f"'{normalized_id}'."
            ) from exc
 
    def insights_for_category(
        self,
        category: EngineeringCategory,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Return all insights belonging to one category.
        """
 
        self._validate_category(
            category
        )
 
        return tuple(
            insight
            for insight in self.insights
            if insight.category == category
        )
 
    def assessments_for_category(
        self,
        category: EngineeringCategory,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Return all assessments belonging to one category.
        """
 
        self._validate_category(
            category
        )
 
        return tuple(
            assessment
            for assessment in self.assessments
            if assessment.category == category
        )
 
    def insights_for_severity(
        self,
        severity: EngineeringSeverity,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Return all insights having one severity.
        """
 
        self._validate_severity(
            severity
        )
 
        return tuple(
            insight
            for insight in self.insights
            if insight.severity == severity
        )
 
    def assessments_for_severity(
        self,
        severity: EngineeringSeverity,
    ) -> tuple[
        EngineeringAssessment,
        ...,
    ]:
        """
        Return all assessments having one severity.
        """
 
        self._validate_severity(
            severity
        )
 
        return tuple(
            assessment
            for assessment in self.assessments
            if assessment.severity == severity
        )
 
    def source_insights_for_assessment(
        self,
        assessment_id: str,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Resolve every insight referenced by one
        assessment.
        """
 
        assessment = self.get_assessment(
            assessment_id
        )
 
        return tuple(
            self.insight_index[
                source_insight_id
            ]
            for source_insight_id
            in assessment.source_insight_ids
        )
 
    def _validate_insight_index(
        self,
    ) -> None:
        """
        Confirm that the insight lookup exactly preserves
        the source insight population.
        """
 
        if not isinstance(
            self.insight_index,
            dict,
        ):
            raise ValueError(
                "'insight_index' must be a dictionary."
            )
 
        if (
            len(self.insight_index)
            != len(self.insights)
        ):
            raise ValueError(
                "Insight index size does not match the "
                "source insight population."
            )
 
        for insight in self.insights:
            indexed_insight = (
                self.insight_index.get(
                    insight.insight_id
                )
            )
 
            if indexed_insight is not insight:
                raise ValueError(
                    "Insight index does not preserve the "
                    "original source insight for ID "
                    f"'{insight.insight_id}'."
                )
 
    def _validate_assessment_index(
        self,
    ) -> None:
        """
        Confirm that the assessment lookup exactly preserves
        the source assessment population.
        """
 
        if not isinstance(
            self.assessment_index,
            dict,
        ):
            raise ValueError(
                "'assessment_index' must be a dictionary."
            )
 
        if (
            len(self.assessment_index)
            != len(self.assessments)
        ):
            raise ValueError(
                "Assessment index size does not match the "
                "source assessment population."
            )
 
        for assessment in self.assessments:
            indexed_assessment = (
                self.assessment_index.get(
                    assessment.assessment_id
                )
            )
 
            if indexed_assessment is not assessment:
                raise ValueError(
                    "Assessment index does not preserve "
                    "the original source assessment for "
                    "ID "
                    f"'{assessment.assessment_id}'."
                )
 
    def _validate_assessment_references(
        self,
    ) -> None:
        """
        Confirm that every assessment-to-insight reference
        resolves successfully.
        """
 
        for assessment in self.assessments:
            for source_insight_id in (
                assessment.source_insight_ids
            ):
                if (
                    source_insight_id
                    not in self.insight_index
                ):
                    raise ValueError(
                        "Engineering assessment "
                        f"'{assessment.assessment_id}' "
                        "references unknown insight ID "
                        f"'{source_insight_id}'."
                    )
 
    def _validate_insight_id_collection(
        self,
        insight_ids,
        field_name: str,
    ) -> tuple[str, ...]:
        """
        Validate one insight-ID collection.
        """
 
        if not isinstance(
            insight_ids,
            tuple,
        ):
            raise ValueError(
                f"'{field_name}' must be a tuple."
            )
 
        normalized_ids: list[str] = []
 
        for insight_id in insight_ids:
            normalized_id = (
                self._normalize_lookup_id(
                    value=insight_id,
                    field_name=field_name,
                )
            )
 
            if (
                normalized_id
                not in self.insight_index
            ):
                raise ValueError(
                    f"'{field_name}' references unknown "
                    "engineering insight ID "
                    f"'{normalized_id}'."
                )
 
            normalized_ids.append(
                normalized_id
            )
 
        if (
            len(normalized_ids)
            != len(set(normalized_ids))
        ):
            raise ValueError(
                f"IDs in '{field_name}' must be unique."
            )
 
        return tuple(
            normalized_ids
        )
 
    @staticmethod
    def _normalize_lookup_id(
        value,
        field_name: str,
    ) -> str:
        """
        Validate and normalize one source identifier.
        """
 
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"'{field_name}' must be a string."
            )
 
        normalized_value = value.strip()
 
        if not normalized_value:
            raise ValueError(
                f"'{field_name}' cannot be empty."
            )
 
        return normalized_value
 
    @staticmethod
    def _validate_category(
        category,
    ) -> None:
        """
        Validate one category argument.
        """
 
        if not isinstance(
            category,
            EngineeringCategory,
        ):
            raise ValueError(
                "'category' must be an "
                "EngineeringCategory value."
            )
 
    @staticmethod
    def _validate_severity(
        severity,
    ) -> None:
        """
        Validate one severity argument.
        """
 
        if not isinstance(
            severity,
            EngineeringSeverity,
        ):
            raise ValueError(
                "'severity' must be an "
                "EngineeringSeverity value."
            )