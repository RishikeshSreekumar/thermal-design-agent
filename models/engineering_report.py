"""
engineering_report.py
 
Provider-neutral and renderer-neutral engineering report
models.
 
The report consumes the complete
EngineeringRecommendationResult produced by the existing
engineering workflow.
 
It does not:
 
- perform engineering calculations;
- modify deterministic engineering status;
- generate recommendations;
- invoke an LLM;
- render PDF, DOCX, HTML, or Streamlit output.
 
Rendering is intentionally kept separate from report
content.
"""
 
from dataclasses import dataclass
 
from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from models.engineering_review_status import (
    EngineeringReviewStatus,
)
 
 
@dataclass(frozen=True)
class EngineeringReportSection:
    """
    One structured engineering-report section.
    """
 
    section_id: str
    title: str
    content: str
 
    def __post_init__(
        self,
    ) -> None:
 
        for field_name, value in {
            "section_id": self.section_id,
            "title": self.title,
            "content": self.content,
        }.items():
 
            if not isinstance(
                value,
                str,
            ):
                raise ValueError(
                    f"'{field_name}' must be a string."
                )
 
            normalized = value.strip()
 
            if not normalized:
                raise ValueError(
                    f"'{field_name}' cannot be empty."
                )
 
            object.__setattr__(
                self,
                field_name,
                normalized,
            )
 
 
@dataclass(frozen=True)
class EngineeringReport:
    """
    Canonical structured engineering report.
 
    The complete recommendation result is preserved so all
    report statements remain traceable to the authoritative
    engineering workflow.
    """
 
    source: EngineeringRecommendationResult
 
    title: str
 
    executive_summary: str
 
    status: EngineeringReviewStatus
 
    sections: tuple[
        EngineeringReportSection,
        ...,
    ]
 
    def __post_init__(
        self,
    ) -> None:
 
        if not isinstance(
            self.source,
            EngineeringRecommendationResult,
        ):
            raise ValueError(
                "'source' must be an "
                "EngineeringRecommendationResult object."
            )
 
        if not isinstance(
            self.title,
            str,
        ):
            raise ValueError(
                "'title' must be a string."
            )
 
        normalized_title = (
            self.title.strip()
        )
 
        if not normalized_title:
            raise ValueError(
                "'title' cannot be empty."
            )
 
        object.__setattr__(
            self,
            "title",
            normalized_title,
        )
 
        if not isinstance(
            self.executive_summary,
            str,
        ):
            raise ValueError(
                "'executive_summary' must be a string."
            )
 
        normalized_summary = (
            self.executive_summary.strip()
        )
 
        if not normalized_summary:
            raise ValueError(
                "'executive_summary' cannot be empty."
            )
 
        object.__setattr__(
            self,
            "executive_summary",
            normalized_summary,
        )
 
        if not isinstance(
            self.status,
            EngineeringReviewStatus,
        ):
            raise ValueError(
                "'status' must be an "
                "EngineeringReviewStatus value."
            )
 
        if not isinstance(
            self.sections,
            tuple,
        ):
            raise ValueError(
                "'sections' must be a tuple."
            )
 
        if not self.sections:
            raise ValueError(
                "Engineering report requires at least "
                "one section."
            )
 
        seen_section_ids: set[str] = set()
 
        for section in self.sections:
 
            if not isinstance(
                section,
                EngineeringReportSection,
            ):
                raise ValueError(
                    "Every report section must be an "
                    "EngineeringReportSection object."
                )
 
            if (
                section.section_id
                in seen_section_ids
            ):
                raise ValueError(
                    "Duplicate engineering-report "
                    "section ID: "
                    f"'{section.section_id}'."
                )
 
            seen_section_ids.add(
                section.section_id
            )
 
        authoritative_status = (
            self.source
            .review_result
            .review
            .status
        )
 
        if self.status != authoritative_status:
            raise ValueError(
                "Engineering-report status must match "
                "the authoritative engineering-review "
                "status."
            )
 
    @property
    def section_count(
        self,
    ) -> int:
        """
        Return the number of report sections.
        """
 
        return len(
            self.sections
        )
 
    @property
    def has_recommendations(
        self,
    ) -> bool:
        """
        Return whether the source workflow produced
        engineering recommendations.
        """
 
        return (
            self.source
            .has_recommendations
        )
 
    def get_section(
        self,
        section_id: str,
    ) -> EngineeringReportSection:
        """
        Return one report section by stable ID.
        """
 
        if not isinstance(
            section_id,
            str,
        ):
            raise ValueError(
                "'section_id' must be a string."
            )
 
        normalized_id = (
            section_id.strip()
        )
 
        for section in self.sections:
 
            if (
                section.section_id
                == normalized_id
            ):
                return section
 
        raise KeyError(
            "Unknown engineering-report section: "
            f"'{normalized_id}'."
        )