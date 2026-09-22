"""
app.py

Complete Streamlit product interface for Thermal Design Agent.

This UI exposes the current application-facing V2 backend:
- natural and forced convection;
- fixed-velocity and fan-coupled forced convection;
- minimum-Rth, weighted and Pareto selection;
- thermal, airflow, mass and material-cost state;
- engineering limits and material-cost budget;
- deterministic engineering intelligence and assessments;
- deterministic / grounded-AI engineering review;
- grounded engineering recommendations;
- HTML engineering report;
- geometry planning, CAD generation and STEP output.

Deterministic engineering calculations remain authoritative.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from config import LOGO_FILE
from core.cad_generator import CADGenerator
from core.candidate_selector import select_candidates
from core.engineering_recommendation_service import (
    EngineeringRecommendationService,
)
from core.engineering_report_builder import (
    EngineeringReportBuilder,
)
from core.engineering_report_html_renderer import (
    EngineeringReportHTMLRenderer,
)
from core.engineering_review_service import (
    EngineeringReviewService,
)
from core.geometry_planner import GeometryPlanner
from core.llm import extract_requirements, get_provider_name
from core.objective_registry import get_optimization_objective
from core.parser import parse_requirements
from core.thermal_optimizer import ThermalOptimizer
from core.validator import review_requirements

from fan.fan_curve import FanCurve, FanCurvePoint

from intelligence.engineering_assessment_engine import (
    EngineeringAssessmentEngine,
)
from intelligence.engineering_intelligence_pipeline import (
    EngineeringIntelligencePipeline,
)
from intelligence.evaluators.airflow_performance_evaluator import (
    AirflowPerformanceEvaluator,
)
from intelligence.evaluators.manufacturability_evaluator import (
    ManufacturabilityEvaluator,
)
from intelligence.evaluators.thermal_margin_evaluator import (
    ThermalMarginEvaluator,
)

from manufacturing.extrusion_capability import AL6063_EXTRUSION

from models.engineering_recommendation_result import (
    EngineeringRecommendationResult,
)
from models.optimization_result import OptimizationResult
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.requirements import (
    FanSpecification,
    MaterialCostBudget,
    NaturalConvectionSpecification,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)


# ==========================================================
# Page Configuration
# ==========================================================
 
st.set_page_config(
    page_title="Thermal Design Agent",
    layout="wide",
)
 
 
# ==========================================================
# Final V2 UI Theme
#
# IMPORTANT:
# Do not append previous experimental CSS blocks below this.
# This is the single UI colour/layout contract.
# ==========================================================
 
st.markdown(
    """
<style>
 
/* =========================================================
   DESIGN TOKENS
   ========================================================= */
 
:root {
    --tda-red: #d71920;
    --tda-red-dark: #b5151b;
 
    --tda-black: #0e1117;
 
    --tda-text: #202124;
    --tda-muted: #697078;
 
    --tda-page: #f4f5f7;
    --tda-surface: #ffffff;
 
    --tda-border: #d9dde2;
    --tda-border-dark: #292f38;
}
 
 
/* =========================================================
   APPLICATION SHELL
   ========================================================= */
 
.stApp {
    background: var(--tda-page);
    color: var(--tda-text);
}
 
.block-container {
    max-width: 1180px;
 
    padding-top: 1rem;
    padding-bottom: 3rem;
}
 
html,
body,
[class*="css"] {
    font-family:
        "Segoe UI",
        Arial,
        Helvetica,
        sans-serif;
}
 
 
/* Hide standard Streamlit footer/menu */
 
#MainMenu {
    visibility: hidden;
}
 
footer {
    visibility: hidden;
}
 
 
/* =========================================================
   STREAMLIT TOP BAR
   ========================================================= */
 
[data-testid="stHeader"] {
    background: var(--tda-black) !important;
}
 
[data-testid="stHeader"] button,
[data-testid="stHeader"] svg {
    color: #f5f6f7 !important;
}
 
 
/* =========================================================
   STICKY PRODUCT HEADER
   ========================================================= */
 
/*
The Streamlit element container containing .tda-header is
made sticky.
 
This is intentional. Making only .tda-header sticky is not
reliable because Streamlit inserts wrapper containers around
Markdown elements.
*/
 
div[data-testid="stElementContainer"]:has(.tda-header) {
    position: sticky !important;
 
    top: 3rem;
 
    z-index: 950;
 
    background: var(--tda-page);
 
    /*
    Extend the same application background horizontally so
    the header does not look like a card pasted on the page.
    */
    box-shadow:
        100vmax 0 0 100vmax var(--tda-page);
 
    clip-path:
        inset(0 -100vmax);
 
    margin-bottom: 1.35rem;
}
 
 
/* Thin full-width separation line */
 
div[data-testid="stElementContainer"]:has(.tda-header)::after {
    content: "";
 
    position: absolute;
 
    left: -100vw;
    right: -100vw;
 
    bottom: 0;
 
    height: 1px;
 
    background: var(--tda-border);
}
 
 
.tda-header {
    display: flex;
 
    align-items: center;
    justify-content: space-between;
 
    gap: 2rem;
 
    width: 100%;
 
    background: transparent;
 
    border: none;
 
    padding:
        1.15rem
        1.10rem
        1.10rem
        1.10rem;
    
    min-height: 96px;
 
    margin: 0;
}
 
 
.tda-brand {
    display: flex;
    align-items: center;
}
 
 
.tda-logo {
    height: 48px;
    width: auto;
 
    max-width: 190px;
 
    object-fit: contain;
 
    display: block;
}
 
 
.tda-logo-fallback {
    color: var(--tda-red);
 
    font-size: 1.05rem;
    font-weight: 700;
}
 
 
.tda-product {
    text-align: right;
}
 
 
.tda-product-name {
    color: var(--tda-text) !important;
 
    font-size: 1.16rem;
    font-weight: 700;
 
    line-height: 1.2;
}
 
 
.tda-product-subtitle {
    color: var(--tda-muted) !important;
 
    margin-top: 0.18rem;
 
    font-size: 0.76rem;
    font-weight: 400;
}
 
 
/* =========================================================
   SINGLE HEADING SYSTEM
   ========================================================= */
 
/*
LEVEL 1:
Major application sections.
 
Examples:
Current Design Request
Requirement Review
Engineering Design Result
Design Space Evaluation
Engineering Review
Engineering Recommendations
Engineering Outputs
*/
 
.tda-major-heading {
    color: var(--tda-text) !important;
 
    font-size: 1.06rem;
    font-weight: 700 !important;
 
    line-height: 1.35;
 
    letter-spacing: 0;
 
    margin-top: 1.45rem;
    margin-bottom: 0.70rem;
}
 
 
/*
LEVEL 2:
Subsections within a major section.
 
Examples:
Engineering Requirements
Engineering Status
Performance
Selected Geometry
*/
 
.tda-sub-heading {
    color: var(--tda-text) !important;
 
    font-size: 0.88rem;
    font-weight: 700 !important;
 
    line-height: 1.35;
 
    letter-spacing: 0;
 
    margin-top: 0.95rem;
    margin-bottom: 0.50rem;
}
 
 
/* Normal text */
 
[data-testid="stAppViewContainer"]
[data-testid="stMarkdownContainer"] p {
    color: var(--tda-text);
}
 
 
/* Genuine secondary/helper text only */
 
[data-testid="stCaptionContainer"] p {
    color: var(--tda-muted) !important;
 
    font-size: 0.78rem;
}
 
 
/* =========================================================
   METRIC / DATA CARDS
   ========================================================= */
 
[data-testid="stMetric"] {
    background: var(--tda-surface) !important;
 
    border: 1px solid var(--tda-border) !important;
 
    border-radius: 4px !important;
 
    padding:
        0.70rem
        0.82rem !important;
 
    min-height: 78px;
 
    box-shadow: none !important;
}
 
 
/* Metric title */
 
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #5d646c !important;
 
    font-size: 0.72rem !important;
    font-weight: 600 !important;
 
    line-height: 1.2 !important;
}
 
 
/* Metric value */
 
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div,
[data-testid="stMetricValue"] span {
    color: var(--tda-text) !important;
 
    font-size: 1.15rem !important;
    font-weight: 650 !important;
 
    line-height: 1.22 !important;
}
 
 
/* Space between metric rows */
 
div[data-testid="stHorizontalBlock"] {
    row-gap: 0.65rem;
}
/* =========================================================
   INPUTS
   ========================================================= */
 
[data-testid="stTextArea"] textarea {
    background: var(--tda-surface) !important;
 
    color: var(--tda-text) !important;
 
    -webkit-text-fill-color:
        var(--tda-text) !important;
 
    caret-color:
        var(--tda-text) !important;
 
    border:
        1px solid
        #c9ced4 !important;
 
    border-radius: 4px !important;
}
 
 
[data-testid="stTextArea"] textarea::placeholder {
    color: #8a9097 !important;
 
    -webkit-text-fill-color:
        #8a9097 !important;
 
    opacity: 1 !important;
}
 
 
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: var(--tda-surface) !important;
 
    color: var(--tda-text) !important;
 
    -webkit-text-fill-color:
        var(--tda-text) !important;
}
 
 
[data-baseweb="select"] > div {
    background: var(--tda-surface) !important;
 
    color: var(--tda-text) !important;
}
 
 
[data-baseweb="select"] span {
    color: var(--tda-text) !important;
}
 
 
/* =========================================================
   BUTTONS
   ========================================================= */
 
.stButton > button,
.stDownloadButton > button {
    min-height: 2.50rem;
 
    border-radius: 4px !important;
 
    font-weight: 600 !important;
 
    box-shadow: none !important;
}
 
 
/* Primary */
 
.stButton > button[kind="primary"] {
    background: var(--tda-red) !important;
 
    border:
        1px solid
        var(--tda-red) !important;
 
    color: #ffffff !important;
}
 
 
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span {
    color: #ffffff !important;
}
 
 
.stButton > button[kind="primary"]:hover {
    background:
        var(--tda-red-dark) !important;
 
    border-color:
        var(--tda-red-dark) !important;
}
 
 
/* Secondary */
 
.stButton > button:not([kind="primary"]) {
    background:
        var(--tda-surface) !important;
 
    border:
        1px solid
        #c9ced4 !important;
 
    color:
        var(--tda-text) !important;
}
 
 
.stButton > button:not([kind="primary"]) p,
.stButton > button:not([kind="primary"]) span {
    color:
        var(--tda-text) !important;
}
 
 
/* Downloads */
 
.stDownloadButton > button {
    background:
        var(--tda-surface) !important;
 
    border:
        1px solid
        #c9ced4 !important;
 
    color:
        var(--tda-text) !important;
}
 
 
.stDownloadButton > button p,
.stDownloadButton > button span {
    color:
        var(--tda-text) !important;
}
 
 
/* =========================================================
   ENGINEERING STATUS
   ========================================================= */
 
.tda-status {
    display: inline-block;
 
    background:
        var(--tda-surface);
 
    border:
        1px solid
        var(--tda-border);
 
    border-left:
        3px solid
        var(--tda-red);
 
    border-radius: 3px;
 
    padding:
        0.38rem
        0.68rem;
 
    color:
        var(--tda-text) !important;
 
    font-size: 0.76rem;
    font-weight: 700;
 
    letter-spacing: 0.02em;
 
    margin-bottom: 0.30rem;
}
 
 
/* =========================================================
   EXPANDERS
   ========================================================= */
 
[data-testid="stExpander"] {
    background:
        var(--tda-surface) !important;
 
    border:
        1px solid
        var(--tda-border) !important;
 
    border-radius:
        4px !important;
 
    box-shadow:
        none !important;
}
 
 
[data-testid="stExpander"] summary {
    color:
        var(--tda-text) !important;
}
 
 
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] p {
    color:
        var(--tda-text) !important;
}
 
 
/* =========================================================
   SIDEBAR — FIXED DARK SHELL
   ========================================================= */
 
/*
Both selectors are intentional because Streamlit versions
can place the background on different sidebar wrappers.
*/
 
section[data-testid="stSidebar"],
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background:
        var(--tda-black) !important;
}
 
 
section[data-testid="stSidebar"],
[data-testid="stSidebar"] {
    border-right:
        1px solid
        var(--tda-border-dark) !important;
}
 
 
/* Sidebar inner spacing */
 
[data-testid="stSidebar"]
[data-testid="stSidebarContent"] {
    padding-top: 1.15rem;
}
 
 
/* Main sidebar group heading */
 
.tda-sidebar-heading {
    color:
        #ffffff !important;
 
    font-size:
        0.75rem;
 
    font-weight:
        700;
 
    letter-spacing:
        0.065em;
 
    text-transform:
        uppercase;
 
    margin-top:
        0.15rem;
 
    margin-bottom:
        0.70rem;
}
 
 
/* Workflow rows */
 
.tda-workflow-row {
    display:
        grid;
 
    grid-template-columns:
        1.65rem
        1fr;
 
    align-items:
        center;
 
    column-gap:
        0.15rem;
 
    padding:
        0.28rem
        0;
 
    color:
        #f3f4f5 !important;
 
    font-size:
        0.82rem;
 
    line-height:
        1.35;
}
 
 
.tda-workflow-number {
    color:
        #858c95 !important;
 
    font-size:
        0.70rem;
 
    font-weight:
        500;
}
 
 
.tda-workflow-text {
    color:
        #f3f4f5 !important;
 
    font-size:
        0.82rem;
 
    font-weight:
        500;
}
 
 
/* System labels */
 
.tda-system-label {
    color:
        #858c95 !important;
 
    font-size:
        0.68rem;
 
    font-weight:
        600;
 
    letter-spacing:
        0.055em;
 
    text-transform:
        uppercase;
 
    margin-top:
        0.65rem;
 
    margin-bottom:
        0.10rem;
}
 
 
/* System values */
 
.tda-system-value {
    color:
        #f3f4f5 !important;
 
    font-size:
        0.80rem;
 
    font-weight:
        500;
 
    line-height:
        1.35;
}
 
 
/* Sidebar separator */
 
[data-testid="stSidebar"] hr {
    border-color:
        #343a44 !important;
 
    margin:
        1.25rem
        0 !important;
}
 
 
/* Prevent light-theme text rules from changing our sidebar */
 
[data-testid="stSidebar"] .tda-sidebar-heading,
[data-testid="stSidebar"] .tda-workflow-row,
[data-testid="stSidebar"] .tda-workflow-text,
[data-testid="stSidebar"] .tda-system-value {
    color:
        #f3f4f5 !important;
}
 
 
[data-testid="stSidebar"] .tda-workflow-number,
[data-testid="stSidebar"] .tda-system-label {
    color:
        #858c95 !important;
}
 
 
/* =========================================================
   DIVIDERS
   ========================================================= */
 
[data-testid="stAppViewContainer"] hr {
    border-color:
        var(--tda-border) !important;
}
 
 
/* =========================================================
   RESPONSIVE
   ========================================================= */
 
@media (max-width: 900px) {
 
    .tda-header {
        gap: 1rem;
 
        padding-left: 0.4rem;
        padding-right: 0.4rem;
    }
 
    .tda-logo {
        height: 42px;
    }
 
    .tda-product-name {
        font-size: 1rem;
    }
 
}

/* =========================================================
   SIDEBAR COLLAPSE CONTROL — VISIBILITY ONLY
   ========================================================= */
 
[data-testid="stSidebarCollapseButton"] {
    opacity: 1 !important;
    visibility: visible !important;
}
 
[data-testid="stSidebarCollapseButton"] button {
    background: #1b2028 !important;
    border: 1px solid #343a44 !important;
    color: #ffffff !important;
 
    opacity: 1 !important;
    visibility: visible !important;
}
 
[data-testid="stSidebarCollapseButton"] button:hover {
    background: #2b313b !important;
    border-color: #4a515c !important;
    color: #ffffff !important;
}
 
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapseButton"] svg *,
[data-testid="stSidebarCollapseButton"] path {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
 
    opacity: 1 !important;
}
 
 
/* Also keep the control visible after the sidebar is collapsed */
 
[data-testid="stSidebarCollapsedControl"] {
    opacity: 1 !important;
    visibility: visible !important;
}
 
[data-testid="stSidebarCollapsedControl"] button {
    background: #1b2028 !important;
    border: 1px solid #343a44 !important;
    color: #ffffff !important;
}
 
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg *,
[data-testid="stSidebarCollapsedControl"] path {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
 
    opacity: 1 !important;
}
 
/* Sidebar collapse / expand arrows — white only */
[data-testid="stSidebarCollapseButton"] button *,
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapsedControl"] button *,
[data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"] {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarCollapseButton"] svg *,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg * {
    stroke: #ffffff !important;
    color: #ffffff !important;
}
 
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# Session State
# ==========================================================

SESSION_DEFAULTS = {
    "engineering_requirements": None,
    "requirements_review": None,
    "original_prompt": "",
    "design_requested": False,
    "analysis_result": None,
    "fixed_air_velocity_backup": None,
    "pareto_exploration_result": None,
    "pareto_selection_configuration": None,
    "pareto_use_ai": True,
}

for key, default_value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# ==========================================================
# Application-Facing Result
# ==========================================================

@dataclass
class ConfiguredEngineeringRun:
    """
    UI-facing aggregate for one configured engineering run.

    The object preserves the existing backend result objects.
    Geometry and STEP output are populated immediately for
    uniquely selected designs. Pareto-front runs keep the full
    trade-off set and generate CAD only after the engineer
    chooses one Pareto candidate.
    """

    requirements: object
    optimization_result: object
    intelligence_result: object
    review_result: object
    recommendation_result: object
    report: object
    geometry: object | None = None
    step_file: Path | None = None
    pareto_exploration_result: object | None = None

    @property
    def selected_candidate(self):
        return self.optimization_result.selected_candidate

    @property
    def engineering_status(self):
        return self.review_result.review.status

    @property
    def has_ai_review(self) -> bool:
        return self.review_result.ai_enriched

    @property
    def has_recommendations(self) -> bool:
        return self.recommendation_result.has_recommendations

    @property
    def uses_pareto_selection(self) -> bool:
        selection_result = self.optimization_result.selection_result
        return bool(
            selection_result is not None
            and selection_result.uses_pareto_selection
        )


# ==========================================================
# UI Helpers
# ==========================================================

def major_heading(text: str) -> None:
    """Render one Level-1 application section heading."""

    st.markdown(
        (
            '<div class="tda-major-heading">'
            f"{text}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def sub_heading(text: str) -> None:
    """Render one Level-2 application subsection heading."""

    st.markdown(
        (
            '<div class="tda-sub-heading">'
            f"{text}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def format_optional_value(
    value: float | None,
    unit: str,
) -> str:
    """Format an optional numerical engineering value."""

    if value is None:
        return "Not provided"

    return f"{value:g} {unit}"


def display_enum_value(value: str | None) -> str:
    """Convert machine-readable identifiers to UI text."""

    if value is None:
        return "Not identified"

    return value.strip().replace("_", " ").title()

NATURAL_ORIENTATION_LABELS = {
    "vertical": "Vertical",
    "horizontal_fins_up": (
        "Horizontal — Fins Upward"
    ),
    "horizontal_fins_down": (
        "Horizontal — Fins Downward"
    ),
}
 
 
def display_natural_orientation(
    orientation: str | None,
) -> str:
    """
    Convert the canonical natural-convection orientation
    into engineer-readable UI text.
    """
 
    if orientation is None:
        return "Not specified"
 
    return NATURAL_ORIENTATION_LABELS.get(
        orientation,
        display_enum_value(orientation),
    )


def format_objective_value(
    objective_key: str,
    value: float,
) -> str:
    """Format one objective value for compact UI display."""

    if objective_key == "thermal_resistance":
        return f"{value:.4f} °C/W"

    if objective_key == "pressure_drop":
        return f"{value:.3f} Pa"

    if objective_key == "pumping_power":
        return f"{value:.5f} W"

    if objective_key == "mass":
        return f"{value * 1000.0:.1f} g"

    return f"{value:g}"


def reset_design_session() -> None:
    """Clear the complete design session and UI configuration."""

    for key in tuple(SESSION_DEFAULTS):
        st.session_state[key] = SESSION_DEFAULTS[key]

    widget_keys = (
        "analysis_airflow_mode",
        "analysis_natural_orientation",
        "analysis_include_radiation",
        "analysis_surface_emissivity",
        "analysis_fan_source",
        "analysis_builtin_fan",
        "analysis_custom_fan_curve",
        "analysis_strategy",
        "analysis_ai_enabled",
        "analysis_apply_temperature_limit",
        "analysis_temperature_limit",
        "analysis_apply_pressure_limit",
        "analysis_pressure_limit",
        "analysis_apply_power_limit",
        "analysis_power_limit",
        "analysis_apply_material_budget",
        "analysis_material_budget",
        "analysis_material_budget_currency",
        "analysis_weight_thermal_resistance",
        "analysis_weight_pressure_drop",
        "analysis_weight_pumping_power",
        "analysis_weight_mass",
        "analysis_pareto_objectives",
        "pareto_candidate_selector",
    )

    for key in widget_keys:
        st.session_state.pop(key, None)


# ==========================================================
# Branding
# ==========================================================

def get_logo_data_uri() -> str:
    """Embed the official Havells logo."""

    logo_path = LOGO_FILE

    if not logo_path.is_file():
        return ""

    encoded = base64.b64encode(
        logo_path.read_bytes()
    ).decode("ascii")

    return "data:image/png;base64," + encoded


def display_application_header() -> None:
    """Render the sticky product header."""

    logo_uri = get_logo_data_uri()

    if logo_uri:
        logo_html = (
            '<img class="tda-logo" alt="Havells" '
            f'src="{logo_uri}">'
        )
    else:
        logo_html = (
            '<div class="tda-logo-fallback">'
            "HAVELLS"
            "</div>"
        )

    header_html = (
        '<div class="tda-header">'
        '<div class="tda-brand">'
        f"{logo_html}"
        "</div>"
        '<div class="tda-product">'
        '<div class="tda-product-name">'
        "Thermal Design Agent"
        "</div>"
        '<div class="tda-product-subtitle">'
        "Engineering Design &amp; Analysis"
        "</div>"
        "</div>"
        "</div>"
    )

    st.markdown(
        header_html,
        unsafe_allow_html=True,
    )


# ==========================================================
# Sidebar
# ==========================================================

def display_sidebar() -> None:
    """Render the engineering workflow sidebar."""

    workflow_steps = (
        "Requirement Extraction",
        "Requirement Review",
        "Interactive Clarification",
        "Analysis Configuration",
        "Thermal Optimization",
        "Engineering Intelligence",
        "Engineering Review",
        "Recommendations",
        "Geometry & CAD",
        "Engineering Outputs",
    )

    with st.sidebar:
        st.markdown(
            (
                '<div class="tda-sidebar-heading">'
                "Engineering Workflow"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        for index, step in enumerate(
            workflow_steps,
            start=1,
        ):
            st.markdown(
                (
                    '<div class="tda-workflow-row">'
                    '<span class="tda-workflow-number">'
                    f"{index:02d}"
                    "</span>"
                    '<span class="tda-workflow-text">'
                    f"{step}"
                    "</span>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

        st.divider()

        st.markdown(
            (
                '<div class="tda-sidebar-heading">'
                "System"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        sidebar_items = (
            ("LLM Provider", get_provider_name()),
            ("Current Topology", "Plate-Fin Heat Sink"),
            (
                "Engineering Modes",
                "Natural / Forced Convection",
            ),
            (
                "Optimization",
                "Minimum Rth / Weighted / Pareto",
            ),
            ("Current Material", "Aluminium 6063-T5"),
            ("CAD Engine", "CadQuery"),
        )

        for label, value in sidebar_items:
            st.markdown(
                (
                    '<div class="tda-system-label">'
                    f"{label}"
                    "</div>"
                    '<div class="tda-system-value">'
                    f"{value}"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


# ==========================================================
# Requirement Review
# ==========================================================

def display_requirements_review(review) -> None:
    """Display extracted engineering requirements."""

    engineering = review.engineering_requirements
    requirements = engineering.requirements
    constraints = engineering.constraints

    major_heading("Requirement Review")
    sub_heading("Engineering Requirements")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Heat Load",
        format_optional_value(
            requirements.heat_load,
            "W",
        ),
    )

    c2.metric(
        "Ambient Temperature",
        format_optional_value(
            requirements.ambient_temperature,
            "°C",
        ),
    )

    c3.metric(
        "Maximum Base Temperature",
        format_optional_value(
            requirements.maximum_base_temperature,
            "°C",
        ),
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Base Length",
        format_optional_value(
            constraints.base_length,
            "mm",
        ),
    )

    c5.metric(
        "Base Width",
        format_optional_value(
            constraints.base_width,
            "mm",
        ),
    )

    c6.metric(
        "Maximum Total Height",
        format_optional_value(
            constraints.max_height,
            "mm",
        ),
    )

    c7, c8, c9 = st.columns(3)

    c7.metric(
        "Component Type",
        display_enum_value(engineering.component_type),
    )

    if engineering.convection_mode == "natural":
        cooling_mode = "Natural Convection"
    elif engineering.convection_mode == "forced":
        cooling_mode = "Forced Convection"
    else:
        cooling_mode = "Not identified"

    c8.metric("Cooling Mode", cooling_mode)

    if engineering.convection_mode == "forced":
        if engineering.fan is not None:
            airflow_value = "Fan coupled"
        else:
            airflow_value = format_optional_value(
                requirements.air_velocity,
                "m/s",
            )
    else:
        airflow_value = "Not applicable"

    c9.metric("Airflow Definition", airflow_value)

    if engineering.convection_mode == "natural":
        natural_specification = (
            engineering.natural_convection
        )
 
        if natural_specification is not None:
            sub_heading(
                "Natural-Convection Definition"
            )
 
            n1, n2, n3 = st.columns(3)
 
            n1.metric(
                "Orientation",
                display_natural_orientation(
                    natural_specification.orientation
                ),
            )
 
            n2.metric(
                "Thermal Radiation",
                (
                    "Included"
                    if natural_specification
                    .include_radiation
                    else "Excluded"
                ),
            )
 
            n3.metric(
                "Surface Emissivity",
                (
                    f"{natural_specification.surface_emissivity:.2f}"
                    if (
                        natural_specification
                        .surface_emissivity
                        is not None
                    )
                    else "Not applicable"
                ),
            )

    optional_limits = []

    if requirements.maximum_pressure_drop is not None:
        optional_limits.append(
            (
                "Maximum Pressure Drop",
                format_optional_value(
                    requirements.maximum_pressure_drop,
                    "Pa",
                ),
            )
        )

    if requirements.maximum_pumping_power is not None:
        optional_limits.append(
            (
                "Maximum Pumping Power",
                format_optional_value(
                    requirements.maximum_pumping_power,
                    "W",
                ),
            )
        )

    if optional_limits:
        sub_heading("Additional Engineering Limits")
        limit_columns = st.columns(len(optional_limits))

        for column, (label, value) in zip(
            limit_columns,
            optional_limits,
            strict=True,
        ):
            column.metric(label, value)

    if engineering.allowed_materials:
        st.caption(
            "Allowed materials: "
            + ", ".join(engineering.allowed_materials)
        )
    else:
        st.caption(
            "Current V2 design path: Aluminium 6063-T5 "
            "extrusion. Broad multi-material optimization "
            "is not implemented."
        )

    if review.assumptions:
        with st.expander("Engineering assumptions"):
            for assumption in review.assumptions:
                st.write(f"- {assumption}")

    if review.validation_errors:
        st.error(
            "Some supplied engineering values are invalid."
        )

        for error in review.validation_errors:
            st.write(f"- {error}")


# ==========================================================
# Forced-Convection Airflow Definition
# ==========================================================

def display_airflow_definition(engineering) -> str:
    """
    Resolve whether forced convection uses prescribed
    approach velocity or the fan-coupled backend path.
    """

    if engineering.convection_mode != "forced":
        engineering.fan = None
        return "natural"

    major_heading("Analysis Configuration")
    sub_heading("Forced-Convection Airflow Definition")

    default_index = 0

    if engineering.fan is not None:
        default_index = 1

    airflow_mode = st.radio(
        "Airflow model",
        options=(
            "Fixed Approach Velocity",
            "Fan-Coupled",
        ),
        index=default_index,
        horizontal=True,
        key="analysis_airflow_mode",
    )

    requirements = engineering.requirements

    if airflow_mode == "Fan-Coupled":
        if requirements.air_velocity is not None:
            st.session_state.fixed_air_velocity_backup = (
                requirements.air_velocity
            )

        requirements.air_velocity = None

        # Temporary valid fan specification so the UI
        # requirement boundary knows prescribed velocity is
        # no longer required. The final fan source is applied
        # immediately before optimization.
        engineering.fan = FanSpecification(
            fan_name="demo_120mm",
            fan_count=1,
            speed_fraction=1.0,
        )

        st.caption(
            "Fan-coupled mode solves the fan curve and "
            "heat-sink system resistance together. The "
            "current optimizer supports one fan at 100% "
            "speed."
        )

        return "fan_coupled"

    engineering.fan = None

    if (
        requirements.air_velocity is None
        and st.session_state.fixed_air_velocity_backup
        is not None
    ):
        requirements.air_velocity = (
            st.session_state.fixed_air_velocity_backup
        )

    st.caption(
        "Fixed-velocity mode evaluates the heat sink at "
        "the prescribed approach air velocity."
    )

    return "fixed_velocity"


def review_requirements_for_active_airflow(
    engineering,
    airflow_mode: str,
):
    """
    Apply the existing deterministic requirement review while
    respecting fan-coupled operation.

    core.validator predates the UI fan selector and therefore
    always asks for air velocity in forced convection. The
    optimizer itself correctly accepts FanSpecification in
    place of prescribed velocity. For fan-coupled UI runs, the
    single obsolete air-velocity clarification is removed here;
    every other deterministic validation result is preserved.
    """

    review = review_requirements(engineering)

    if (
        engineering.convection_mode == "forced"
        and airflow_mode == "fan_coupled"
        and engineering.fan is not None
    ):
        review.clarification_questions[:] = [
            question
            for question in review.clarification_questions
            if question.field_name != "air_velocity"
        ]

    return review


# ==========================================================
# Clarification
# ==========================================================

def apply_clarification_answers(
    engineering,
    answers: dict,
) -> None:
    """Apply clarification answers to requirements."""

    requirements = engineering.requirements
    constraints = engineering.constraints

    if "convection_mode" in answers:
        engineering.convection_mode = answers[
            "convection_mode"
        ]

    if "heat_load" in answers:
        requirements.heat_load = answers["heat_load"]

    if "ambient_temperature" in answers:
        requirements.ambient_temperature = answers[
            "ambient_temperature"
        ]

    if "air_velocity" in answers:
        requirements.air_velocity = answers["air_velocity"]
        st.session_state.fixed_air_velocity_backup = (
            answers["air_velocity"]
        )

    if "base_length" in answers:
        constraints.base_length = answers["base_length"]

    if "base_width" in answers:
        constraints.base_width = answers["base_width"]

    if "max_height" in answers:
        constraints.max_height = answers["max_height"]

    if (
        "natural_convection_orientation"
        in answers
    ):
        if engineering.natural_convection is None:
            engineering.natural_convection = (
                NaturalConvectionSpecification()
            )
 
        engineering.natural_convection.orientation = (
            answers[
                "natural_convection_orientation"
            ]
        )
 
    if "surface_emissivity" in answers:
        if engineering.natural_convection is None:
            engineering.natural_convection = (
                NaturalConvectionSpecification()
            )
 
        engineering.natural_convection.include_radiation = (
            True
        )
 
        engineering.natural_convection.surface_emissivity = (
            answers["surface_emissivity"]
        )


def collect_clarification_answers(review) -> dict | None:
    """Display interactive clarification questions."""

    question_map = {
        question.field_name: question
        for question in review.clarification_questions
    }

    major_heading("Additional Information Required")

    st.caption(
        "Complete the missing engineering requirements "
        "before analysis continues."
    )

    answers: dict = {}

    with st.form("clarification_form"):
        if "convection_mode" in question_map:
            question = question_map["convection_mode"]
            sub_heading(question.question)

            answers["convection_mode"] = st.selectbox(
                "Cooling mode",
                options=["natural", "forced"],
                format_func=(
                    lambda value: (
                        "Natural Convection"
                        if value == "natural"
                        else "Forced Convection"
                    )
                ),
            )

            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        if "heat_load" in question_map:
            question = question_map["heat_load"]
            sub_heading(question.question)

            answers["heat_load"] = st.number_input(
                "Heat load (W)",
                min_value=0.01,
                value=100.0,
                step=1.0,
            )

            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        if "ambient_temperature" in question_map:
            question = question_map["ambient_temperature"]
            sub_heading(question.question)

            answers["ambient_temperature"] = st.number_input(
                "Ambient temperature (°C)",
                value=25.0,
                step=1.0,
            )

            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        if "base_length" in question_map:
            question = question_map["base_length"]
            sub_heading(question.question)

            answers["base_length"] = st.number_input(
                "Base length (mm)",
                min_value=0.01,
                value=50.0,
                step=1.0,
            )

            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        if "base_width" in question_map:
            question = question_map["base_width"]
            sub_heading(question.question)

            answers["base_width"] = st.number_input(
                "Base width (mm)",
                min_value=0.01,
                value=50.0,
                step=1.0,
            )

            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        if "max_height" in question_map:
            question = question_map["max_height"]
            sub_heading(question.question)

            answers["max_height"] = st.number_input(
                "Maximum total height (mm)",
                min_value=0.01,
                value=25.0,
                step=1.0,
            )

            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        if "air_velocity" in question_map:
            question = question_map["air_velocity"]
            sub_heading(question.question)

            answers["air_velocity"] = st.number_input(
                "Inlet air velocity (m/s)",
                min_value=0.01,
                value=5.0,
                step=0.1,
            )

            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        if (
            "natural_convection_orientation"
            in question_map
        ):
            question = question_map[
                "natural_convection_orientation"
            ]
 
            sub_heading(question.question)
 
            answers[
                "natural_convection_orientation"
            ] = st.selectbox(
                "Horizontal orientation",
                options=(
                    "horizontal_fins_up",
                    "horizontal_fins_down",
                ),
                format_func=lambda value: (
                    "Horizontal — Fins Upward"
                    if value == "horizontal_fins_up"
                    else "Horizontal — Fins Downward"
                ),
            )
 
            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )
 
        if "surface_emissivity" in question_map:
            question = question_map[
                "surface_emissivity"
            ]
 
            sub_heading(question.question)
 
            answers["surface_emissivity"] = (
                st.number_input(
                    "Surface emissivity",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.85,
                    step=0.05,
                    format="%.2f",
                )
            )
 
            st.caption(
                "Why this is required: "
                f"{question.reason}"
            )

        submitted = st.form_submit_button(
            "Continue",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        return answers

    return None


# ==========================================================
# Known Model Limitations
# ==========================================================

def get_known_limitations(
    requirements,
) -> tuple[str, ...]:
    """
    Return model limitations appropriate to the active
    convection configuration.
    """
 
    if requirements.convection_mode == "natural":
 
        specification = (
            requirements.natural_convection
        )
 
        orientation = "vertical"
        radiation_enabled = False
 
        if specification is not None:
            if specification.orientation is not None:
                orientation = specification.orientation
 
            radiation_enabled = (
                specification.include_radiation
            )
 
        limitations = [
            (
                "Natural-convection predictions use "
                "reduced-order engineering correlations "
                "and require experimental or CFD validation "
                "before design release."
            ),
            (
                "Intermediate inclined orientations are "
                "not modeled. The current natural-convection "
                "model supports vertical, horizontal fins "
                "upward, and horizontal fins downward."
            ),
        ]
 
        if orientation == "vertical":
            limitations.append(
                (
                    "The vertical natural-convection path "
                    "uses the current Churchill-Chu-based "
                    "reduced-order convection model."
                )
            )
 
        elif orientation in {
            "horizontal_fins_up",
            "horizontal_fins_down",
        }:
            limitations.append(
                (
                    "Horizontal plate-fin performance uses "
                    "orientation-specific Tari-Mehrtash "
                    "reduced-order correlations. Correlation "
                    "applicability should be validated for "
                    "the final heat-sink geometry."
                )
            )
 
        if radiation_enabled:
            limitations.append(
                (
                    "Thermal radiation is represented using "
                    "a gray-diffuse surface exchanging with "
                    "large surroundings at ambient "
                    "temperature. Detailed inter-fin "
                    "surface-to-surface view factors are "
                    "not resolved."
                )
            )
 
        else:
            limitations.append(
                (
                    "Thermal radiation is disabled for this "
                    "analysis."
                )
            )
 
        return tuple(limitations)
 
    return (
        (
            "Radiation heat transfer is not included in "
            "the current forced-convection model."
        ),
        (
            "Fan-related prediction accuracy depends on "
            "the supplied fan curve when fan-coupled "
            "operation is used."
        ),
    )


# ==========================================================
# Optimization / Fan Configuration
# ==========================================================

OBJECTIVE_LABEL_TO_KEY = {
    "Thermal Resistance": "thermal_resistance",
    "Pressure Drop": "pressure_drop",
    "Pumping Power": "pumping_power",
    "Mass": "mass",
}

OBJECTIVE_KEY_TO_LABEL = {
    value: key
    for key, value in OBJECTIVE_LABEL_TO_KEY.items()
}


def available_objective_labels(requirements) -> tuple[str, ...]:
    """Return objectives that are meaningful for the mode."""

    if requirements.convection_mode == "natural":
        return (
            "Thermal Resistance",
            "Mass",
        )

    return (
        "Thermal Resistance",
        "Pressure Drop",
        "Pumping Power",
        "Mass",
    )


def parse_custom_fan_curve(text: str) -> FanCurve:
    """
    Parse custom fan data supplied as one Q, dP pair per line.

    Accepted examples:
        0.00, 120
        0.02, 108
    """

    points: list[FanCurvePoint] = []

    for line_number, raw_line in enumerate(
        text.splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line:
            continue

        normalized = line.replace(";", ",")
        parts = [
            item.strip()
            for item in normalized.split(",")
            if item.strip()
        ]

        if len(parts) != 2:
            raise ValueError(
                "Custom fan curve line "
                f"{line_number} must contain exactly "
                "two comma-separated values: flow rate "
                "in m³/s and static pressure in Pa."
            )

        try:
            flow_rate = float(parts[0])
            pressure = float(parts[1])
        except ValueError as exc:
            raise ValueError(
                "Custom fan curve line "
                f"{line_number} contains a non-numerical "
                "value."
            ) from exc

        points.append(
            FanCurvePoint(
                volumetric_flow_rate=flow_rate,
                static_pressure=pressure,
            )
        )

    if len(points) < 2:
        raise ValueError(
            "A custom fan curve requires at least two "
            "valid flow/pressure points."
        )

    return FanCurve(points=tuple(points))


def build_selection_configuration(
    requirements,
    strategy_label: str,
):
    """Build the existing backend selection configuration."""

    if strategy_label == "Minimum Thermal Resistance":
        return OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .MINIMUM_THERMAL_RESISTANCE
            )
        )

    if strategy_label == "Weighted Multi-Objective":
        available_labels = available_objective_labels(
            requirements
        )

        weights = []
        objectives = []

        for label in available_labels:
            key = OBJECTIVE_LABEL_TO_KEY[label]
            widget_key = f"analysis_weight_{key}"
            weight = float(st.session_state[widget_key])

            if weight <= 0.0:
                continue

            weights.append(
                ObjectiveWeight(
                    objective_key=key,
                    weight=weight,
                )
            )

            objectives.append(
                get_optimization_objective(key)
            )

        if not weights:
            raise ValueError(
                "Weighted optimization requires at least "
                "one objective with a weight greater "
                "than zero."
            )

        return OptimizationSelectionConfiguration(
            mode=OptimizationSelectionMode.WEIGHTED_SCORE,
            scoring_configuration=ScoringConfiguration(
                objective_weights=tuple(weights)
            ),
            objectives=tuple(objectives),
        )

    if strategy_label == "Pareto Front":
        selected_labels = st.session_state[
            "analysis_pareto_objectives"
        ]

        if len(selected_labels) < 2:
            raise ValueError(
                "Pareto analysis requires at least two "
                "engineering objectives in the product UI."
            )

        objectives = tuple(
            get_optimization_objective(
                OBJECTIVE_LABEL_TO_KEY[label]
            )
            for label in selected_labels
        )

        return OptimizationSelectionConfiguration(
            mode=OptimizationSelectionMode.PARETO_FRONT,
            objectives=objectives,
        )

    raise ValueError(
        f"Unsupported optimization strategy: {strategy_label}"
    )


def apply_analysis_constraints(requirements) -> None:
    """Apply optional engineering/commercial limits from UI."""

    thermal = requirements.requirements
    constraints = requirements.constraints

    if st.session_state[
        "analysis_apply_temperature_limit"
    ]:
        thermal.maximum_base_temperature = float(
            st.session_state[
                "analysis_temperature_limit"
            ]
        )
    else:
        thermal.maximum_base_temperature = None

    if requirements.convection_mode == "forced":
        if st.session_state[
            "analysis_apply_pressure_limit"
        ]:
            thermal.maximum_pressure_drop = float(
                st.session_state[
                    "analysis_pressure_limit"
                ]
            )
        else:
            thermal.maximum_pressure_drop = None

        if st.session_state[
            "analysis_apply_power_limit"
        ]:
            thermal.maximum_pumping_power = float(
                st.session_state[
                    "analysis_power_limit"
                ]
            )
        else:
            thermal.maximum_pumping_power = None
    else:
        thermal.maximum_pressure_drop = None
        thermal.maximum_pumping_power = None

    if st.session_state[
        "analysis_apply_material_budget"
    ]:
        constraints.material_cost_budget = MaterialCostBudget(
            maximum_amount=float(
                st.session_state[
                    "analysis_material_budget"
                ]
            ),
            currency_code=str(
                st.session_state[
                    "analysis_material_budget_currency"
                ]
            ),
        )
    else:
        constraints.material_cost_budget = None

def apply_natural_convection_configuration(
    requirements,
) -> None:
    """
    Apply the natural-convection configuration selected
    in the product UI.
 
    Orientation is a run-level engineering boundary
    condition. Radiation uses the explicitly displayed
    emissivity and ambient temperature as the current
    radiative-surroundings temperature.
    """
 
    if requirements.convection_mode != "natural":
        return
 
    specification = (
        requirements.natural_convection
    )
 
    if specification is None:
        specification = (
            NaturalConvectionSpecification()
        )
 
        requirements.natural_convection = (
            specification
        )
 
    specification.orientation = str(
        st.session_state[
            "analysis_natural_orientation"
        ]
    )
 
    specification.include_radiation = bool(
        st.session_state[
            "analysis_include_radiation"
        ]
    )
 
    if specification.include_radiation:
        specification.surface_emissivity = float(
            st.session_state[
                "analysis_surface_emissivity"
            ]
        )
 
        specification.surroundings_temperature = (
            requirements
            .requirements
            .ambient_temperature
        )
 
    else:
        specification.surface_emissivity = None
 
        specification.surroundings_temperature = None


def apply_fan_configuration(
    requirements,
    airflow_mode: str,
) -> None:
    """Apply the selected existing fan backend configuration."""

    if requirements.convection_mode != "forced":
        requirements.fan = None
        return

    if airflow_mode != "fan_coupled":
        requirements.fan = None

        if (
            requirements.requirements.air_velocity is None
            and st.session_state.fixed_air_velocity_backup
            is not None
        ):
            requirements.requirements.air_velocity = (
                st.session_state.fixed_air_velocity_backup
            )

        return

    fan_source = st.session_state[
        "analysis_fan_source"
    ]

    if fan_source == "Built-in Demo Fan":
        requirements.fan = FanSpecification(
            fan_name=st.session_state[
                "analysis_builtin_fan"
            ],
            fan_count=1,
            speed_fraction=1.0,
        )
    else:
        fan_curve = parse_custom_fan_curve(
            st.session_state[
                "analysis_custom_fan_curve"
            ]
        )

        requirements.fan = FanSpecification(
            fan_curve=fan_curve,
            fan_count=1,
            speed_fraction=1.0,
        )

    requirements.requirements.air_velocity = None


# ==========================================================
# Configured Backend Orchestration
# ==========================================================
class NoFeasibleDesignError(ValueError):
    """
    Expected engineering outcome raised when the active
    requirements and constraints leave no feasible design.
    """

def build_downstream_engineering_run(
    requirements,
    optimization_result,
    *,
    use_ai: bool,
    pareto_exploration_result=None,
) -> ConfiguredEngineeringRun:
    """Run intelligence, review, report and CAD downstream."""

    if not optimization_result.has_feasible_design:
        raise NoFeasibleDesignError(
            "No feasible heat-sink design was found within "
            "the supplied engineering requirements."
        )

    if not optimization_result.has_single_selected_design:
        raise ValueError(
            "Downstream engineering review and CAD require "
            "one selected design. For Pareto optimization, "
            "select one non-dominated design first."
        )

    assessment_engine = EngineeringAssessmentEngine(
        evaluators=(
            ManufacturabilityEvaluator(
                capability=AL6063_EXTRUSION,
            ),
            ThermalMarginEvaluator(
                warning_margin_temperature=10.0,
            ),
            AirflowPerformanceEvaluator(),
        )
    )

    intelligence_pipeline = EngineeringIntelligencePipeline(
        assessment_engine=assessment_engine
    )

    intelligence_result = intelligence_pipeline.run(
        requirements=requirements,
        optimization_result=optimization_result,
        known_limitations=get_known_limitations(requirements),
    )

    review_result = EngineeringReviewService.build(
        intelligence_result,
        use_ai=use_ai,
        provider=None,
        fallback_to_deterministic=True,
    )

    if use_ai:
        recommendation_result = (
            EngineeringRecommendationService.build(
                review_result,
                provider=None,
                fallback_to_empty=True,
            )
        )
    else:
        recommendation_result = EngineeringRecommendationResult(
            review_result=review_result,
            recommendations=(),
        )

    report = EngineeringReportBuilder.build(
        recommendation_result
    )

    thermal_result = optimization_result.best_result

    if thermal_result is None:
        raise RuntimeError(
            "A uniquely selected design did not provide "
            "the expected thermal result."
        )

    geometry = GeometryPlanner().create_geometry(
        requirements,
        thermal_result,
    )

    step_file = CADGenerator().generate(geometry)

    return ConfiguredEngineeringRun(
        requirements=requirements,
        optimization_result=optimization_result,
        intelligence_result=intelligence_result,
        review_result=review_result,
        recommendation_result=recommendation_result,
        report=report,
        geometry=geometry,
        step_file=step_file,
        pareto_exploration_result=pareto_exploration_result,
    )


def run_configured_engineering_workflow(
    requirements,
    selection_configuration,
    *,
    use_ai: bool,
) -> ConfiguredEngineeringRun:
    """
    Run one uniquely selecting backend workflow.

    EngineeringOrchestrator in codebase 14 owns the canonical
    default application path but does not accept an explicit
    OptimizationSelectionConfiguration. This UI helper invokes
    the same public backend services in the same order so the
    existing weighted-selection capability can be exposed
    without altering deterministic calculations.
    """

    optimization_result = (
        ThermalOptimizer()
        .optimize_with_details(
            requirements,
            selection_configuration=selection_configuration,
        )
    )

    return build_downstream_engineering_run(
        requirements,
        optimization_result,
        use_ai=use_ai,
    )


def run_pareto_exploration(
    requirements,
    selection_configuration,
):
    """Run only the existing multi-candidate Pareto optimizer."""

    optimization_result = (
        ThermalOptimizer()
        .optimize_with_details(
            requirements,
            selection_configuration=selection_configuration,
        )
    )

    if not optimization_result.has_feasible_design:
        raise NoFeasibleDesignError(
            "No feasible heat-sink design was found within "
            "the supplied engineering requirements."
        )

    selection_result = optimization_result.selection_result

    if (
        selection_result is None
        or not selection_result.uses_pareto_selection
    ):
        raise RuntimeError(
            "Pareto exploration did not return a Pareto "
            "selection result."
        )

    return optimization_result


def finalize_pareto_engineering_workflow(
    requirements,
    pareto_exploration_result,
    selection_configuration,
    selected_index: int,
    *,
    use_ai: bool,
) -> ConfiguredEngineeringRun:
    """
    Continue the full workflow for one engineer-selected
    member of an already-computed Pareto front.

    The original multi-candidate Pareto result is preserved
    separately for UI trade-off display. The existing selector
    is then applied to the chosen candidate alone using the same
    Pareto configuration, yielding a valid single-candidate
    Pareto selection for downstream intelligence, review,
    reporting and CAD.
    """

    pareto_candidates = (
        pareto_exploration_result.selected_candidates
    )

    if not pareto_candidates:
        raise ValueError(
            "The Pareto exploration contains no selected "
            "candidates."
        )

    if not 0 <= selected_index < len(pareto_candidates):
        raise ValueError(
            "Selected Pareto candidate index is out of range."
        )

    selected_candidate = pareto_candidates[selected_index]

    final_selection_result = select_candidates(
        (selected_candidate,),
        selection_configuration,
    )

    best_result = (
        ThermalOptimizer._candidate_to_thermal_results(
            selected_candidate,
            pareto_exploration_result.selected_material,
        )
    )

    final_optimization_result = OptimizationResult(
        best_result=best_result,
        candidates=pareto_exploration_result.candidates,
        feasible_candidate_count=(
            pareto_exploration_result.feasible_candidate_count
        ),
        rejected_candidate_count=(
            pareto_exploration_result.rejected_candidate_count
        ),
        selected_material=(
            pareto_exploration_result.selected_material
        ),
        selected_process=(
            pareto_exploration_result.selected_process
        ),
        selection_result=final_selection_result,
    )

    return build_downstream_engineering_run(
        requirements,
        final_optimization_result,
        use_ai=use_ai,
        pareto_exploration_result=(
            pareto_exploration_result
        ),
    )


# ==========================================================
# Analysis Configuration UI
# ==========================================================

def display_analysis_configuration(
    requirements,
    airflow_mode: str,
) -> None:
    """Expose the application-facing V2 backend configuration."""

    if requirements.convection_mode != "forced":
        major_heading("Analysis Configuration")

    if (
        requirements.convection_mode == "forced"
        and airflow_mode == "fan_coupled"
    ):
        sub_heading("Fan Definition")

        fan_source = st.selectbox(
            "Fan source",
            options=(
                "Built-in Demo Fan",
                "Custom Fan Curve",
            ),
            key="analysis_fan_source",
        )

        if fan_source == "Built-in Demo Fan":
            st.selectbox(
                "Fan",
                options=("demo_120mm",),
                key="analysis_builtin_fan",
            )

            st.caption(
                "The current internal fan database contains "
                "the demonstration 120 mm fan curve."
            )
        else:
            st.text_area(
                "Fan curve points — flow rate (m³/s), "
                "static pressure (Pa)",
                value=(
                    "0.00, 120\n"
                    "0.02, 108\n"
                    "0.04, 90\n"
                    "0.06, 68\n"
                    "0.08, 42\n"
                    "0.10, 0"
                ),
                height=150,
                key="analysis_custom_fan_curve",
            )

            st.caption(
                "Provide points in strictly increasing "
                "volumetric-flow order. The current fan-coupled "
                "optimizer supports one fan at 100% speed."
            )
    if requirements.convection_mode == "natural":
        sub_heading(
            "Natural-Convection Configuration"
        )
 
        natural_specification = (
            requirements.natural_convection
        )
 
        if natural_specification is None:
            natural_specification = (
                NaturalConvectionSpecification(
                    orientation="vertical",
                    include_radiation=False,
                )
            )
 
        orientation_options = (
            "vertical",
            "horizontal_fins_up",
            "horizontal_fins_down",
        )
 
        current_orientation = (
            natural_specification.orientation
        )
 
        if (
            current_orientation
            not in orientation_options
        ):
            current_orientation = "vertical"
 
        orientation_index = (
            orientation_options.index(
                current_orientation
            )
        )
 
        st.selectbox(
            "Heat-sink orientation",
            options=orientation_options,
            index=orientation_index,
            format_func=display_natural_orientation,
            key="analysis_natural_orientation",
        )
 
        include_radiation = st.checkbox(
            "Include thermal radiation",
            value=(
                natural_specification
                .include_radiation
            ),
            key="analysis_include_radiation",
        )
 
        emissivity_default = (
            natural_specification
            .surface_emissivity
        )
 
        if emissivity_default is None:
            emissivity_default = 0.85
 
        st.number_input(
            "Surface emissivity",
            min_value=0.0,
            max_value=1.0,
            value=float(
                emissivity_default
            ),
            step=0.05,
            format="%.2f",
            disabled=not include_radiation,
            key="analysis_surface_emissivity",
        )
 
        st.caption(
            "Radiative surroundings are currently assumed "
            "to be at ambient-air temperature. Surface "
            "emissivity must represent the intended heat-sink "
            "surface finish; 0.85 is only a visible starting "
            "value when no emissivity was supplied."
        )

    sub_heading("Optimization Strategy")

    strategy_label = st.selectbox(
        "Candidate selection method",
        options=(
            "Minimum Thermal Resistance",
            "Weighted Multi-Objective",
            "Pareto Front",
        ),
        key="analysis_strategy",
    )

    available_labels = available_objective_labels(
        requirements
    )

    if strategy_label == "Weighted Multi-Objective":
        st.caption(
            "Lower weighted scores are preferred. Set an "
            "objective weight to zero to exclude that "
            "objective from ranking."
        )

        default_weights = {
            "thermal_resistance": 40.0,
            "pressure_drop": 30.0,
            "pumping_power": 20.0,
            "mass": 10.0,
        }

        if requirements.convection_mode == "natural":
            default_weights = {
                "thermal_resistance": 70.0,
                "mass": 30.0,
            }

        weight_columns = st.columns(
            len(available_labels)
        )

        for column, label in zip(
            weight_columns,
            available_labels,
            strict=True,
        ):
            key = OBJECTIVE_LABEL_TO_KEY[label]

            with column:
                st.number_input(
                    f"{label} weight",
                    min_value=0.0,
                    value=float(
                        default_weights.get(key, 0.0)
                    ),
                    step=5.0,
                    key=f"analysis_weight_{key}",
                )

    elif strategy_label == "Pareto Front":
        if requirements.convection_mode == "natural":
            pareto_default = list(available_labels)
        else:
            pareto_default = [
                "Thermal Resistance",
                "Pressure Drop",
                "Pumping Power",
                "Mass",
            ]

        st.multiselect(
            "Pareto objectives",
            options=available_labels,
            default=pareto_default,
            key="analysis_pareto_objectives",
        )

        st.caption(
            "Pareto analysis returns all non-dominated "
            "designs. The software does not silently choose "
            "one trade-off solution; the engineer selects a "
            "Pareto candidate for CAD output."
        )

    else:
        st.caption(
            "Select the feasible candidate with the lowest "
            "calculated thermal resistance."
        )

    sub_heading("Engineering Limits")

    thermal = requirements.requirements

    c1, c2 = st.columns(2)

    with c1:
        apply_temperature_limit = st.checkbox(
            "Apply maximum base-temperature limit",
            value=(
                thermal.maximum_base_temperature
                is not None
            ),
            key="analysis_apply_temperature_limit",
        )

        st.number_input(
            "Maximum base temperature (°C)",
            value=float(
                thermal.maximum_base_temperature
                if thermal.maximum_base_temperature
                is not None
                else 120.0
            ),
            step=1.0,
            disabled=not apply_temperature_limit,
            key="analysis_temperature_limit",
        )

    with c2:
        apply_material_budget = st.checkbox(
            "Apply material-cost budget",
            value=(
                requirements.constraints.material_cost_budget
                is not None
            ),
            key="analysis_apply_material_budget",
        )

        budget_columns = st.columns([2, 1])

        with budget_columns[0]:
            st.number_input(
                "Maximum material cost",
                min_value=0.01,
                value=100.0,
                step=10.0,
                disabled=not apply_material_budget,
                key="analysis_material_budget",
            )

        with budget_columns[1]:
            st.text_input(
                "Currency",
                value="INR",
                max_chars=3,
                disabled=not apply_material_budget,
                key="analysis_material_budget_currency",
            )

    if requirements.convection_mode == "forced":
        c3, c4 = st.columns(2)

        with c3:
            apply_pressure_limit = st.checkbox(
                "Apply maximum pressure-drop limit",
                value=(
                    thermal.maximum_pressure_drop
                    is not None
                ),
                key="analysis_apply_pressure_limit",
            )

            st.number_input(
                "Maximum pressure drop (Pa)",
                min_value=0.01,
                value=float(
                    thermal.maximum_pressure_drop
                    if thermal.maximum_pressure_drop
                    is not None
                    else 100.0
                ),
                step=1.0,
                disabled=not apply_pressure_limit,
                key="analysis_pressure_limit",
            )

        with c4:
            apply_power_limit = st.checkbox(
                "Apply maximum pumping-power limit",
                value=(
                    thermal.maximum_pumping_power
                    is not None
                ),
                key="analysis_apply_power_limit",
            )

            st.number_input(
                "Maximum pumping power (W)",
                min_value=0.0001,
                value=float(
                    thermal.maximum_pumping_power
                    if thermal.maximum_pumping_power
                    is not None
                    else 0.25
                ),
                step=0.01,
                format="%.4f",
                disabled=not apply_power_limit,
                key="analysis_power_limit",
            )

    st.caption(
        "Material cost uses illustrative development pricing. "
        "Currencies are never converted silently; a budget "
        "currency must match the candidate cost currency."
    )

    sub_heading("AI Engineering Assistance")

    st.checkbox(
        "Enable grounded AI review narrative and recommendations",
        value=True,
        key="analysis_ai_enabled",
    )

    st.caption(
        "Deterministic calculations, feasibility, assessments "
        "and engineering-review status remain authoritative. "
        "If AI synthesis fails, the deterministic review is "
        "preserved."
    )

    run_clicked = st.button(
        "Run Engineering Analysis",
        type="primary",
        use_container_width=True,
    )

    if not run_clicked:
        return

    st.session_state.analysis_result = None

    try:
        apply_analysis_constraints(requirements)
 
        apply_natural_convection_configuration(
            requirements
        )
 
        apply_fan_configuration(
            requirements,
            airflow_mode,
        )

        final_review = review_requirements_for_active_airflow(
            requirements,
            airflow_mode,
        )

        if final_review.needs_clarification:
            missing = ", ".join(
                question.field_name
                for question in final_review.clarification_questions
            )

            raise ValueError(
                "Required engineering information is still "
                f"missing: {missing}."
            )

        if final_review.has_validation_errors:
            raise ValueError(
                "Engineering requirements are invalid: "
                + " | ".join(final_review.validation_errors)
            )

        selection_configuration = (
            build_selection_configuration(
                requirements,
                strategy_label,
            )
        )

        use_ai = bool(
            st.session_state[
                "analysis_ai_enabled"
            ]
        )

        progress = st.progress(10)

        if (
            selection_configuration.mode
            == OptimizationSelectionMode.PARETO_FRONT
        ):
            with st.spinner(
                "Exploring the Pareto trade-off set..."
            ):
                pareto_result = run_pareto_exploration(
                    requirements,
                    selection_configuration,
                )

            st.session_state.pareto_exploration_result = (
                pareto_result
            )
            st.session_state.pareto_selection_configuration = (
                selection_configuration
            )
            st.session_state.pareto_use_ai = use_ai
            st.session_state.analysis_result = None

        else:
            with st.spinner(
                "Running deterministic design exploration, "
                "engineering intelligence and review..."
            ):
                result = run_configured_engineering_workflow(
                    requirements,
                    selection_configuration,
                    use_ai=use_ai,
                )

            st.session_state.analysis_result = result
            st.session_state.pareto_exploration_result = None
            st.session_state.pareto_selection_configuration = None

        progress.progress(100)
        progress.empty()

    except NoFeasibleDesignError as exc:
        progress.empty()
 
        st.session_state.analysis_result = None
        st.session_state.pareto_exploration_result = None
        st.session_state.pareto_selection_configuration = None
 
        st.warning(
            "No feasible design was found within the active "
            "engineering requirements and constraints."
        )
 
        st.info(
            "The design space was evaluated successfully, but "
            "every candidate violated one or more active limits. "
            "Review and relax the relevant geometry, thermal, "
            "airflow, material, or material-cost constraints "
            "before running the analysis again."
        )
 
        st.caption(
            f"Engineering outcome: {exc}"
        )
 
    except Exception as exc:
        if "progress" in locals():
            progress.empty()
 
        st.error(
            "The configured engineering analysis could "
            "not be completed because of an unexpected "
            "application error."
        )
 
        st.exception(exc)


# ==========================================================
# Engineering Result Presentation
# ==========================================================

def display_engineering_status(result) -> None:
    """Display authoritative engineering status."""

    status_text = (
        result.engineering_status.value
        .replace("_", " ")
        .upper()
    )

    sub_heading("Engineering Status")

    st.markdown(
        (
            '<div class="tda-status">'
            f"{status_text}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def display_candidate_performance(candidate) -> None:
    """Render thermal/physical performance for one candidate."""

    if candidate.convection_mode == "natural":
        htc_label = "Effective HTC"
    else:
        htc_label = "Heat Transfer Coefficient"

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Thermal Resistance",
        f"{candidate.thermal_resistance:.3f} °C/W",
    )

    c2.metric(
        "Base Temperature",
        (
            f"{candidate.estimated_base_temperature:.1f} "
            "°C"
        ),
    )

    c3.metric(
        htc_label,
        (
            f"{candidate.heat_transfer_coefficient:.1f} "
            "W/m²K"
        ),
    )

    c4.metric(
        "Mass",
        f"{candidate.mass * 1000.0:.1f} g",
    )

def display_natural_convection_model(
    result,
    candidate,
) -> None:
    """
    Display orientation and the separated convection /
    radiation thermal state for natural-convection runs.
    """
 
    if (
        result.requirements.convection_mode
        != "natural"
    ):
        return
 
    specification = (
        result.requirements
        .natural_convection
    )
 
    orientation = "vertical"
    radiation_enabled = False
    emissivity = None
    surroundings_temperature = None
 
    if specification is not None:
        if specification.orientation is not None:
            orientation = (
                specification.orientation
            )
 
        radiation_enabled = (
            specification.include_radiation
        )
 
        emissivity = (
            specification.surface_emissivity
        )
 
        surroundings_temperature = (
            specification
            .surroundings_temperature
        )
 
    sub_heading(
        "Natural-Convection Model"
    )
 
    c1, c2, c3 = st.columns(3)
 
    c1.metric(
        "Orientation",
        display_natural_orientation(
            orientation
        ),
    )
 
    c2.metric(
        "Thermal Radiation",
        (
            "Included"
            if radiation_enabled
            else "Excluded"
        ),
    )
 
    c3.metric(
        "Surface Emissivity",
        (
            f"{emissivity:.2f}"
            if (
                radiation_enabled
                and emissivity is not None
            )
            else "Not applicable"
        ),
    )
 
    c4, c5, c6 = st.columns(3)
 
    c4.metric(
        "Convective HTC",
        (
            f"{candidate.convective_heat_transfer_coefficient:.2f} "
            "W/m²K"
        ),
    )
 
    c5.metric(
        "Radiative HTC",
        (
            f"{candidate.radiative_heat_transfer_coefficient:.2f} "
            "W/m²K"
        ),
    )
 
    c6.metric(
        "Effective HTC",
        (
            f"{candidate.effective_heat_transfer_coefficient:.2f} "
            "W/m²K"
        ),
    )
 
    if (
        radiation_enabled
        and surroundings_temperature
        is not None
    ):
        st.caption(
            "Radiative surroundings temperature: "
            f"{surroundings_temperature:g} °C. "
            "Nusselt number and Convective HTC represent "
            "convection only; Effective HTC is the combined "
            "coefficient used for fin efficiency and thermal "
            "resistance."
        )
    else:
        st.caption(
            "Nusselt number and Convective HTC represent "
            "the natural-convection correlation. Radiation "
            "is not contributing to this result."
        )


def display_candidate_geometry(
    candidate,
    optimization,
) -> None:
    """Render geometry/material/process for one candidate."""

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Base Thickness",
        f"{candidate.base_thickness:g} mm",
    )

    c2.metric(
        "Fin Height",
        f"{candidate.fin_height:g} mm",
    )

    c3.metric(
        "Fin Thickness",
        f"{candidate.fin_thickness:g} mm",
    )

    c4.metric(
        "Fin Spacing",
        f"{candidate.fin_spacing:g} mm",
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Fin Count", candidate.fin_count)
    c6.metric(
        "Total Height",
        f"{candidate.total_height:g} mm",
    )
    c7.metric("Material", optimization.selected_material)
    c8.metric(
        "Manufacturing Process",
        optimization.selected_process,
    )

    if candidate.has_material_cost:
        st.caption(
            "Illustrative material cost: "
            f"{candidate.material_cost_currency} "
            f"{candidate.material_cost:.2f}. Development "
            "pricing only; not an approved procurement value."
        )


def display_selected_design(result) -> None:
    """Display the uniquely selected design."""

    candidate = result.selected_candidate

    if candidate is None:
        return

    major_heading("Engineering Design Result")
    display_engineering_status(result)

    sub_heading("Performance")
    display_candidate_performance(candidate)
 
    display_natural_convection_model(
        result,
        candidate,
    )
 
    sub_heading("Selected Geometry")
    display_candidate_geometry(
        candidate,
        result.optimization_result,
    )


def pareto_objective_keys_from_optimization(
    optimization_result,
) -> tuple[str, ...]:
    """Return objective keys used by one Pareto exploration."""

    selection_result = optimization_result.selection_result

    if selection_result is None:
        return ()

    objectives = selection_result.configuration.objectives

    if objectives is None:
        return (
            "thermal_resistance",
            "pressure_drop",
            "pumping_power",
        )

    return tuple(
        objective.candidate_attribute
        for objective in objectives
    )


def display_pareto_front_table(
    pareto_exploration_result,
) -> int:
    """Display the full Pareto front and return selected index."""

    selection_result = pareto_exploration_result.selection_result

    if (
        selection_result is None
        or not selection_result.uses_pareto_selection
        or selection_result.pareto_result is None
    ):
        raise ValueError(
            "A valid Pareto exploration result is required."
        )

    pareto_result = selection_result.pareto_result

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Pareto Designs",
        pareto_result.pareto_candidate_count,
    )
    c2.metric(
        "Dominated Designs",
        pareto_result.dominated_candidate_count,
    )
    c3.metric(
        "Analyzed Feasible Designs",
        pareto_result.total_candidate_count,
    )

    objective_keys = pareto_objective_keys_from_optimization(
        pareto_exploration_result
    )

    rows = []

    for index, analysis in enumerate(
        pareto_result.pareto_candidates,
        start=1,
    ):
        candidate = analysis.candidate

        row = {
            "Design": f"P{index:03d}",
            "Base (mm)": candidate.base_thickness,
            "Fin H (mm)": candidate.fin_height,
            "Fin T (mm)": candidate.fin_thickness,
            "Spacing (mm)": candidate.fin_spacing,
            "Fins": candidate.fin_count,
        }

        for objective_key in objective_keys:
            label = OBJECTIVE_KEY_TO_LABEL.get(
                objective_key,
                objective_key,
            )

            row[label] = format_objective_value(
                objective_key,
                analysis.raw_report.get_value(objective_key),
            )

        rows.append(row)

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Every design shown above is non-dominated for the "
        "selected objectives. The optimizer intentionally does "
        "not declare one trade-off solution universally best."
    )

    candidates = selection_result.selected_candidates

    def candidate_label(index: int) -> str:
        candidate = candidates[index]
        return (
            f"P{index + 1:03d} — "
            f"Rth {candidate.thermal_resistance:.3f} °C/W · "
            f"ΔP {candidate.pressure_drop:.2f} Pa · "
            f"Mass {candidate.mass * 1000.0:.1f} g"
        )

    selected_index = st.selectbox(
        "Select Pareto design",
        options=tuple(range(len(candidates))),
        format_func=candidate_label,
        key="pareto_candidate_selector",
    )

    return int(selected_index)


def display_pareto_exploration_for_selection(
    requirements,
) -> None:
    """Display the raw Pareto front before downstream review."""

    exploration = st.session_state.pareto_exploration_result
    configuration = st.session_state.pareto_selection_configuration

    if exploration is None or configuration is None:
        return

    major_heading("Pareto Front Selection")
    sub_heading("Non-Dominated Design Set")

    selected_index = display_pareto_front_table(exploration)

    candidate = exploration.selected_candidates[selected_index]

    sub_heading("Candidate Preview")
    display_candidate_performance(candidate)
    display_candidate_geometry(candidate, exploration)

    st.caption(
        "Choose the trade-off design you want to progress. "
        "Engineering intelligence, review, recommendations, "
        "reporting and CAD will then be generated for that "
        "engineer-selected Pareto design while the original "
        "Pareto set remains visible for traceability."
    )

    if st.button(
        "Continue with Selected Pareto Design",
        type="primary",
        use_container_width=True,
    ):
        progress = st.progress(35)

        try:
            with st.spinner(
                "Running engineering intelligence, review, "
                "recommendations, report and CAD for the "
                "selected Pareto design..."
            ):
                result = finalize_pareto_engineering_workflow(
                    requirements,
                    exploration,
                    configuration,
                    selected_index,
                    use_ai=bool(
                        st.session_state.pareto_use_ai
                    ),
                )

            progress.progress(100)
            progress.empty()

            st.session_state.analysis_result = result
            st.rerun()

        except Exception as exc:
            progress.empty()
            st.error(
                "The selected Pareto design could not be "
                "progressed through the engineering workflow."
            )
            st.exception(exc)


def display_pareto_design_set(result) -> None:
    """Display original Pareto exploration and final design."""

    exploration = result.pareto_exploration_result

    if exploration is None:
        return

    major_heading("Engineering Design Result")
    display_engineering_status(result)

    sub_heading("Original Pareto Trade-Off Set")
    selected_index = display_pareto_front_table(exploration)

    final_candidate = result.selected_candidate

    if final_candidate is None:
        raise ValueError(
            "Finalized Pareto workflow has no selected design."
        )

    # Keep the selector aligned with the actual final design
    # even if a user changes the displayed dropdown after the
    # downstream run. The engineering result remains locked to
    # the design that was explicitly progressed.
    displayed_candidate = exploration.selected_candidates[
        selected_index
    ]

    sub_heading("Finalized Pareto Design")
    display_candidate_performance(final_candidate)
 
    display_natural_convection_model(
        result,
        final_candidate,
    )
    display_candidate_geometry(
        final_candidate,
        result.optimization_result,
    )

    if displayed_candidate is not final_candidate:
        st.caption(
            "The dropdown above is currently previewing a "
            "different Pareto design. The engineering review, "
            "report and STEP file below remain locked to the "
            "Pareto design that was previously finalized. Run "
            "the Pareto workflow again to progress a different "
            "candidate."
        )
    else:
        st.caption(
            "This design was explicitly selected by the engineer "
            "from the original non-dominated Pareto set."
        )


def display_design_space(result) -> None:
    """Display optimization-space statistics and strategy."""

    optimization = result.optimization_result

    major_heading("Design Space Evaluation")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Candidates Explored",
        optimization.total_candidate_count,
    )
    c2.metric(
        "Feasible Candidates",
        optimization.feasible_candidate_count,
    )
    c3.metric(
        "Rejected Candidates",
        optimization.rejected_candidate_count,
    )
    c4.metric(
        "Feasibility Rate",
        f"{optimization.feasibility_rate:.1f}%",
    )

    selection_result = optimization.selection_result

    if selection_result is None:
        return

    selection_mode = (
        selection_result.mode.value
        .replace("_", " ")
        .title()
    )

    st.caption(
        "Selection strategy: "
        f"{selection_mode}"
    )

    configuration = selection_result.configuration

    if configuration.objectives:
        st.caption(
            "Objectives: "
            + ", ".join(
                objective.name
                for objective in configuration.objectives
            )
        )

    budget = result.requirements.constraints.material_cost_budget

    if budget is not None:
        st.caption(
            "Material-cost budget applied during candidate "
            f"screening: {budget.currency_code} "
            f"{budget.maximum_amount:.2f}."
        )


def display_weighted_optimization_details(result) -> None:
    """Display weighted ranking and objective contributions."""

    selection_result = (
        result.optimization_result.selection_result
    )

    if (
        selection_result is None
        or not selection_result.uses_weighted_selection
    ):
        return

    weighted_result = selection_result.weighted_result

    if weighted_result is None:
        return

    major_heading("Weighted Optimization Details")

    normalized_weights = {
        item.objective_key: (
            item.weight
            / weighted_result.configuration.total_weight
        )
        for item in (
            weighted_result
            .configuration
            .objective_weights
        )
    }

    st.caption(
        "Normalized objective weights: "
        + " · ".join(
            (
                f"{OBJECTIVE_KEY_TO_LABEL.get(key, key)} "
                f"{value * 100.0:.1f}%"
            )
            for key, value in normalized_weights.items()
        )
    )

    rows = []

    for ranked in (
        weighted_result.ranking.ranked_candidates[:10]
    ):
        scored = ranked.scored_candidate
        candidate = scored.analysis.candidate

        row = {
            "Rank": ranked.rank,
            "Weighted Score": f"{scored.total_score:.5f}",
            "Rth (°C/W)": f"{candidate.thermal_resistance:.4f}",
            "ΔP (Pa)": f"{candidate.pressure_drop:.3f}",
            "Pump Power (W)": f"{candidate.pumping_power:.5f}",
            "Mass (g)": f"{candidate.mass * 1000.0:.1f}",
            "Fin H (mm)": candidate.fin_height,
            "Fin T (mm)": candidate.fin_thickness,
            "Spacing (mm)": candidate.fin_spacing,
        }

        rows.append(row)

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )

    with st.expander(
        "Selected-candidate objective contributions"
    ):
        best_scored = (
            weighted_result
            .best_candidate
            .scored_candidate
        )

        for contribution in best_scored.contributions:
            st.write(
                "**"
                f"{contribution.objective.name}"
                "**"
            )
            st.caption(
                "Normalized value: "
                f"{contribution.normalized_value:.4f} · "
                "Normalized weight: "
                f"{contribution.normalized_weight:.4f} · "
                "Weighted contribution: "
                f"{contribution.weighted_value:.4f}"
            )


def candidate_for_performance_display(result):
    """
    Return the finalized candidate used for performance display.
 
    For ordinary and weighted optimization this is the uniquely
    selected design. For a finalized Pareto workflow this is the
    design explicitly selected by the engineer.
    """
 
    return result.selected_candidate


def display_airflow_performance(result) -> None:
    """Display airflow only for forced convection."""

    requirements = result.requirements

    if requirements.convection_mode != "forced":
        return

    candidate = candidate_for_performance_display(result)

    if candidate is None:
        return

    major_heading("Airflow Performance")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Approach Velocity",
        f"{candidate.approach_velocity:.2f} m/s",
    )
    c2.metric(
        "Channel Velocity",
        f"{candidate.channel_velocity:.2f} m/s",
    )
    c3.metric(
        "Pressure Drop",
        f"{candidate.pressure_drop:.2f} Pa",
    )
    c4.metric(
        "Pumping Power",
        f"{candidate.pumping_power:.4f} W",
    )

    if requirements.fan is None:
        airflow_description = "Fixed approach velocity"
    elif requirements.fan.fan_name is not None:
        airflow_description = (
            "Fan coupled · "
            f"{requirements.fan.fan_name}"
        )
    else:
        airflow_description = "Fan coupled · custom fan curve"

    st.caption(
        f"Airflow model: {airflow_description} · "
        f"Reynolds number: {candidate.reynolds_number:.0f}"
    )


# ==========================================================
# Engineering Intelligence / Traceability
# ==========================================================

def format_evidence(evidence) -> str:
    """Format one structured engineering evidence value."""

    value = evidence.value

    if isinstance(value, float):
        value_text = f"{value:g}"
    else:
        value_text = str(value)

    if evidence.unit:
        value_text = f"{value_text} {evidence.unit}"

    return f"{evidence.key}: {value_text}"


def display_engineering_intelligence(result) -> None:
    """Expose deterministic insights, assessments and evidence."""

    intelligence = result.intelligence_result

    major_heading("Engineering Intelligence")

    c1, c2, c3 = st.columns(3)
    c1.metric("Engineering Insights", len(intelligence.insights))
    c2.metric(
        "Engineering Assessments",
        len(intelligence.assessments),
    )
    c3.metric(
        "Selected Design Set",
        len(intelligence.context.selected_candidates),
    )

    with st.expander(
        "Deterministic insights and assessment traceability"
    ):
        sub_heading("Engineering Insights")

        for insight in intelligence.insights:
            category = (
                insight.category.value
                .replace("_", " ")
                .title()
            )
            severity = insight.severity.value.upper()

            st.markdown(
                f"**{insight.title}**"
            )
            st.caption(
                f"{category} · {severity} · "
                f"ID: {insight.insight_id}"
            )
            st.write(insight.summary)

            if insight.evidence:
                st.caption(
                    "Evidence: "
                    + " · ".join(
                        format_evidence(item)
                        for item in insight.evidence
                    )
                )

        sub_heading("Engineering Assessments")

        for assessment in intelligence.assessments:
            category = (
                assessment.category.value
                .replace("_", " ")
                .title()
            )
            severity = assessment.severity.value.upper()
            outcome = "PASS" if assessment.passed else "ACTION"

            st.markdown(
                f"**{assessment.title}**"
            )
            st.caption(
                f"{category} · {severity} · {outcome} · "
                f"Rule: {assessment.rule_id}"
            )
            st.write(assessment.summary)

            if assessment.evidence:
                st.caption(
                    "Evidence: "
                    + " · ".join(
                        format_evidence(item)
                        for item in assessment.evidence
                    )
                )

            if assessment.recommendation:
                st.caption(
                    "Deterministic action: "
                    f"{assessment.recommendation}"
                )


# ==========================================================
# Engineering Review
# ==========================================================

def display_review_item(item) -> None:
    """Display one structured engineering-review item."""

    st.markdown(f"**{item.title}**")
    st.write(item.summary)

    details = []

    if item.consequence:
        details.append(
            "Consequence: " + item.consequence
        )

    if item.verification:
        details.append(
            "Verification: " + item.verification
        )

    if details:
        st.caption(" · ".join(details))


def display_engineering_review(result) -> None:
    """Display the complete structured engineering review."""

    review = result.review_result.review

    major_heading("Engineering Review")
    st.write(review.executive_summary)

    if review.strengths:
        with st.expander(
            f"Strengths ({len(review.strengths)})"
        ):
            for item in review.strengths:
                display_review_item(item)

    if review.concerns:
        with st.expander(
            f"Concerns ({len(review.concerns)})"
        ):
            for item in review.concerns:
                display_review_item(item)

    if review.tradeoffs:
        with st.expander(
            f"Engineering Trade-Offs ({len(review.tradeoffs)})"
        ):
            for tradeoff in review.tradeoffs:
                st.markdown(f"**{tradeoff.title}**")
                st.write(
                    "**Benefit:** "
                    f"{tradeoff.benefit}"
                )
                st.write(
                    "**Penalty:** "
                    f"{tradeoff.penalty}"
                )
                if tradeoff.guidance:
                    st.caption(
                        "Guidance: "
                        f"{tradeoff.guidance}"
                    )

    sub_heading("Category Review")

    for section in review.sections:
        title = (
            section.category.value
            .replace("_", " ")
            .title()
        )
        status = (
            section.status.value
            .replace("_", " ")
            .upper()
        )

        with st.expander(f"{title} — {status}"):
            st.write(section.summary)

            for finding in section.findings:
                display_review_item(finding)

    if review.required_actions:
        sub_heading("Required Actions")

        for index, item in enumerate(
            review.required_actions,
            start=1,
        ):
            st.markdown(
                f"**{index}. {item.title}**"
            )
            st.write(item.summary)

            if item.verification:
                st.caption(
                    "Verification: "
                    f"{item.verification}"
                )


# ==========================================================
# Recommendations / Validation
# ==========================================================

def display_recommendations(result) -> None:
    """Display complete grounded recommendation content."""

    major_heading("Engineering Recommendations")

    if not result.has_recommendations:
        if result.review_result.ai_requested:
            st.info(
                "No additional grounded AI engineering "
                "recommendations were generated."
            )
        else:
            st.info(
                "AI-assisted recommendation generation was "
                "disabled for this run."
            )
        return

    for index, recommendation in enumerate(
        result.recommendation_result.recommendations,
        start=1,
    ):
        with st.expander(
            f"{index}. {recommendation.title}",
            expanded=(index == 1),
        ):
            priority = recommendation.priority.value.upper()
            category = (
                recommendation.category.value
                .replace("_", " ")
                .title()
            )
            recommendation_type = (
                recommendation.recommendation_type.value
                .replace("_", " ")
                .title()
            )

            st.caption(
                f"Priority: {priority} · "
                f"Category: {category} · "
                f"Type: {recommendation_type}"
            )

            st.write(recommendation.recommendation)

            st.markdown("**Rationale**")
            st.write(recommendation.rationale)

            if recommendation.expected_effect:
                st.markdown("**Expected Effect**")
                st.write(recommendation.expected_effect)

            if recommendation.verification:
                st.caption(
                    "Verification: "
                    f"{recommendation.verification}"
                )


def display_validation_requirements(result) -> None:
    """Display deterministic validation requirements."""

    review = result.review_result.review

    if not review.validation_requirements:
        return

    major_heading("Validation Requirements")

    for index, item in enumerate(
        review.validation_requirements,
        start=1,
    ):
        st.markdown(
            f"**{index}. {item.summary}**"
        )

        if item.verification:
            st.caption(
                "Verification: "
                f"{item.verification}"
            )


# ==========================================================
# Engineering Outputs
# ==========================================================

def render_report_html(result) -> str:
    """Render the canonical V2 HTML report."""

    logo_path = LOGO_FILE

    if logo_path.is_file():
        return EngineeringReportHTMLRenderer.render(
            result.report,
            logo_path=logo_path,
        )

    return EngineeringReportHTMLRenderer.render(
        result.report
    )


def display_engineering_outputs(result) -> None:
    """Display available engineering downloads."""

    major_heading("Engineering Outputs")

    report_html = render_report_html(result)

    step_file = result.step_file

    if step_file is not None:
        step_data = Path(step_file).read_bytes()

        c1, c2 = st.columns(2)

        c1.download_button(
            label="Download STEP Model",
            data=step_data,
            file_name="heatsink.step",
            mime="application/step",
            use_container_width=True,
        )

        c2.download_button(
            label="Download Engineering Report",
            data=report_html.encode("utf-8"),
            file_name=(
                "thermal_design_engineering_report.html"
            ),
            mime="text/html",
            use_container_width=True,
        )
    else:
        st.download_button(
            label="Download Engineering Report",
            data=report_html.encode("utf-8"),
            file_name=(
                "thermal_design_engineering_report.html"
            ),
            mime="text/html",
            use_container_width=True,
        )


    if result.review_result.ai_enriched:
        st.caption(
            "Engineering calculations, feasibility, "
            "assessments and engineering status are "
            "deterministic. Review narrative and "
            "recommendations include grounded AI synthesis."
        )
    elif result.review_result.ai_requested:
        st.caption(
            "AI review synthesis was unavailable. The "
            "deterministic engineering review was preserved."
        )
    else:
        st.caption(
            "This run used deterministic engineering review "
            "only. AI review and recommendation synthesis "
            "were disabled."
        )


# ==========================================================
# Result Orchestration
# ==========================================================

def display_complete_result(result) -> None:
    """Render all applicable result layers."""

    if result.uses_pareto_selection:
        display_pareto_design_set(result)
    else:
        display_selected_design(result)

    display_design_space(result)
    display_weighted_optimization_details(result)
    display_airflow_performance(result)
    display_engineering_intelligence(result)
    display_engineering_review(result)
    display_recommendations(result)
    display_validation_requirements(result)
    display_engineering_outputs(result)


# ==========================================================
# Application Shell
# ==========================================================

display_sidebar()
display_application_header()


# ==========================================================
# New Design Request
# ==========================================================

if not st.session_state.design_requested:
    major_heading("Engineering Design Request")
    sub_heading("Describe the thermal design problem")

    st.caption(
        "Provide the heat load, available envelope, ambient "
        "condition, cooling mode and relevant thermal or "
        "airflow limits. Missing required information can "
        "be clarified in the next step."
    )

    prompt = st.text_area(
        "Design request",
        value="",
        placeholder=(
            "Example: Design a plate-fin heat sink for a "
            "165 W heat load under forced convection. The "
            "base dimensions are 50 mm × 50 mm, ambient "
            "temperature is 30 °C, air velocity is 5 m/s, "
            "maximum total height is 25 mm, and maximum "
            "allowable base temperature is 105 °C."
        ),
        height=145,
        label_visibility="collapsed",
    )

    generate_clicked = st.button(
        "Review Design Requirements",
        type="primary",
        use_container_width=True,
    )

else:
    prompt = st.session_state.original_prompt

    control_columns = st.columns([3, 1])

    with control_columns[0]:
        major_heading("Current Design Request")
        st.write(st.session_state.original_prompt)

    with control_columns[1]:
        st.markdown(
            '<div style="height:1.05rem;"></div>',
            unsafe_allow_html=True,
        )

        if st.button(
            "Start New Design",
            use_container_width=True,
        ):
            reset_design_session()
            st.rerun()

    generate_clicked = False


# ==========================================================
# Initial Requirement Extraction
# ==========================================================

if generate_clicked:
    reset_design_session()

    if not prompt.strip():
        st.warning(
            "Please enter an engineering design requirement."
        )
        st.stop()

    extraction_progress = st.progress(0)

    try:
        with st.spinner(
            "Extracting engineering requirements..."
        ):
            raw_requirements = extract_requirements(prompt)

        extraction_progress.progress(15)

        with st.spinner(
            "Reviewing the extracted engineering requirements..."
        ):
            engineering = parse_requirements(
                raw_requirements
            )
            review = review_requirements(engineering)

        extraction_progress.progress(30)
        extraction_progress.empty()

        st.session_state.engineering_requirements = engineering
        st.session_state.requirements_review = review
        st.session_state.original_prompt = prompt
        st.session_state.design_requested = True
        st.session_state.analysis_result = None
        st.session_state.fixed_air_velocity_backup = (
            engineering.requirements.air_velocity
        )

        st.rerun()

    except Exception as exc:
        extraction_progress.empty()
        st.error(
            "Requirement extraction could not be completed."
        )
        st.exception(exc)


# ==========================================================
# Resume Stored Workflow
# ==========================================================

if st.session_state.design_requested:
    try:
        engineering = (
            st.session_state.engineering_requirements
        )

        initial_review = review_requirements(engineering)
        display_requirements_review(initial_review)

        airflow_mode = display_airflow_definition(
            engineering
        )

        review = review_requirements_for_active_airflow(
            engineering,
            airflow_mode,
        )

        st.session_state.requirements_review = review

        if review.needs_clarification:
            clarification_answers = (
                collect_clarification_answers(review)
            )

            if clarification_answers is not None:
                apply_clarification_answers(
                    engineering,
                    clarification_answers,
                )

                st.session_state.engineering_requirements = (
                    engineering
                )
                st.session_state.analysis_result = None
                st.rerun()

            st.stop()

        if review.has_validation_errors:
            st.info(
                "Correct the invalid engineering requirements "
                "before continuing."
            )
            st.stop()

        st.divider()

        display_analysis_configuration(
            review.engineering_requirements,
            airflow_mode,
        )

        if (
            st.session_state.pareto_exploration_result
            is not None
            and st.session_state.analysis_result is None
        ):
            st.divider()
            display_pareto_exploration_for_selection(
                review.engineering_requirements
            )

        if st.session_state.analysis_result is not None:
            st.divider()
            display_complete_result(
                st.session_state.analysis_result
            )

    except Exception as exc:
        st.error(
            "The engineering design process could not be "
            "completed."
        )
        st.exception(exc)
          