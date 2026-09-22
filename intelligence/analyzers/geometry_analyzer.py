"""
geometry_analyzer.py
 
Generate deterministic insights describing the geometry
of selected heat-sink candidates.
 
This analyzer reports calculated and generated geometric
facts. It does not apply manufacturability or compactness
judgments and does not invoke an LLM.
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
 
 
class GeometryAnalyzer(
    EngineeringAnalyzer,
):
    """
    Generate structured geometry insights for the
    candidate or candidates selected by optimization.
    """
 
    def analyze(
        self,
        context: EngineeringContext,
    ) -> tuple[
        EngineeringInsight,
        ...,
    ]:
        """
        Generate geometry insights appropriate to the
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
        Report the geometry of one uniquely selected
        design.
        """
 
        return EngineeringInsight(
            insight_id=(
                "geometry.selected_design_dimensions"
            ),
            severity=EngineeringSeverity.INFO,
            category=EngineeringCategory.GEOMETRY,
            title="Selected-design geometry",
            summary=(
                "The engineering context records the "
                "generated dimensions of the uniquely "
                "selected heat-sink design."
            ),
            evidence=(
                EngineeringEvidence(
                    key="base_thickness",
                    value=candidate.base_thickness,
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="fin_thickness",
                    value=candidate.fin_thickness,
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="fin_height",
                    value=candidate.fin_height,
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="fin_spacing",
                    value=candidate.fin_spacing,
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="fin_count",
                    value=candidate.fin_count,
                ),
                EngineeringEvidence(
                    key="total_height",
                    value=candidate.total_height,
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="gross_frontal_area",
                    value=candidate.gross_frontal_area,
                    unit="m^2",
                ),
                EngineeringEvidence(
                    key="open_flow_area",
                    value=candidate.open_flow_area,
                    unit="m^2",
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
        Report geometry ranges across multiple selected
        Pareto-optimal candidates.
        """
 
        if len(candidates) < 2:
            raise ValueError(
                "Geometry trade-off insight requires at "
                "least two selected candidates."
            )
 
        base_thicknesses = tuple(
            candidate.base_thickness
            for candidate in candidates
        )
 
        fin_thicknesses = tuple(
            candidate.fin_thickness
            for candidate in candidates
        )
 
        fin_heights = tuple(
            candidate.fin_height
            for candidate in candidates
        )
 
        fin_spacings = tuple(
            candidate.fin_spacing
            for candidate in candidates
        )
 
        fin_counts = tuple(
            candidate.fin_count
            for candidate in candidates
        )
 
        total_heights = tuple(
            candidate.total_height
            for candidate in candidates
        )
 
        gross_frontal_areas = tuple(
            candidate.gross_frontal_area
            for candidate in candidates
        )
 
        open_flow_areas = tuple(
            candidate.open_flow_area
            for candidate in candidates
        )
 
        return EngineeringInsight(
            insight_id=(
                "geometry.tradeoff_set_dimensions"
            ),
            severity=EngineeringSeverity.INFO,
            category=EngineeringCategory.GEOMETRY,
            title="Geometry range across trade-off set",
            summary=(
                "The selected Pareto-optimal candidates "
                "span a range of generated heat-sink "
                "dimensions."
            ),
            evidence=(
                EngineeringEvidence(
                    key="selected_candidate_count",
                    value=len(candidates),
                ),
                EngineeringEvidence(
                    key="minimum_base_thickness",
                    value=min(
                        base_thicknesses
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="maximum_base_thickness",
                    value=max(
                        base_thicknesses
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="minimum_fin_thickness",
                    value=min(
                        fin_thicknesses
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="maximum_fin_thickness",
                    value=max(
                        fin_thicknesses
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="minimum_fin_height",
                    value=min(
                        fin_heights
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="maximum_fin_height",
                    value=max(
                        fin_heights
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="minimum_fin_spacing",
                    value=min(
                        fin_spacings
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="maximum_fin_spacing",
                    value=max(
                        fin_spacings
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="minimum_fin_count",
                    value=min(
                        fin_counts
                    ),
                ),
                EngineeringEvidence(
                    key="maximum_fin_count",
                    value=max(
                        fin_counts
                    ),
                ),
                EngineeringEvidence(
                    key="minimum_total_height",
                    value=min(
                        total_heights
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="maximum_total_height",
                    value=max(
                        total_heights
                    ),
                    unit="mm",
                ),
                EngineeringEvidence(
                    key="minimum_gross_frontal_area",
                    value=min(
                        gross_frontal_areas
                    ),
                    unit="m^2",
                ),
                EngineeringEvidence(
                    key="maximum_gross_frontal_area",
                    value=max(
                        gross_frontal_areas
                    ),
                    unit="m^2",
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
            ),
            source="selected_pareto_candidates",
        )