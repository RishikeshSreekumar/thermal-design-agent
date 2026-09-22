"""
Focused checks for structured engineering insight models.
"""
 
from models.engineering_category import (
    EngineeringCategory,
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
 
 
def expect_value_error(
    action,
    expected_message: str,
) -> None:
    """
    Confirm that an action raises the expected validation
    error.
    """
 
    try:
        action()
 
    except ValueError as error:
        assert expected_message in str(error)
 
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
 
 
pressure_drop_evidence = EngineeringEvidence(
    key="pressure_drop",
    value=82.0,
    unit="Pa",
    description=(
        "Calculated pressure loss across the heat sink."
    ),
)
 
fan_pressure_evidence = EngineeringEvidence(
    key="available_fan_static_pressure",
    value=90.0,
    unit="Pa",
    description=(
        "Available static pressure at the operating point."
    ),
)
 
warning_insight = EngineeringInsight(
    insight_id="airflow.pressure_drop_margin",
    severity=EngineeringSeverity.WARNING,
    category=EngineeringCategory.AIRFLOW,
    title="Limited fan-pressure margin",
    summary=(
        "The calculated heat-sink pressure drop uses most "
        "of the available fan static pressure."
    ),
    evidence=(
        pressure_drop_evidence,
        fan_pressure_evidence,
    ),
    source="fan_coupled_thermal_analysis",
)
 
assert warning_insight.insight_id == (
    "airflow.pressure_drop_margin"
)
 
assert (
    warning_insight.severity
    == EngineeringSeverity.WARNING
)
 
assert (
    warning_insight.category
    == EngineeringCategory.AIRFLOW
)
 
assert warning_insight.has_evidence
 
assert warning_insight.requires_attention
 
assert not warning_insight.is_positive
 
assert not warning_insight.is_critical
 
assert warning_insight.evidence == (
    pressure_drop_evidence,
    fan_pressure_evidence,
)
 
critical_insight = EngineeringInsight(
    insight_id="thermal.base_temperature_limit",
    severity=EngineeringSeverity.CRITICAL,
    category=EngineeringCategory.THERMAL,
    title="Base-temperature limit exceeded",
    summary=(
        "The estimated base temperature exceeds the "
        "allowable requirement."
    ),
    evidence=(
        EngineeringEvidence(
            key="estimated_base_temperature",
            value=108.0,
            unit="degC",
        ),
        EngineeringEvidence(
            key="maximum_base_temperature",
            value=100.0,
            unit="degC",
        ),
    ),
    source="thermal_requirement_check",
)
 
assert critical_insight.requires_attention
 
assert critical_insight.is_critical
 
assert not critical_insight.is_positive
 
positive_insight = EngineeringInsight(
    insight_id="manufacturing.process_feasible",
    severity=EngineeringSeverity.SUCCESS,
    category=(
        EngineeringCategory.MANUFACTURING
    ),
    title="Geometry is process-feasible",
    summary=(
        "The selected geometry satisfies the checked "
        "extrusion manufacturing rules."
    ),
    evidence=(
        EngineeringEvidence(
            key="manufacturing_feasible",
            value=True,
        ),
    ),
    source="manufacturing_assessment",
)
 
assert positive_insight.is_positive
 
assert not positive_insight.requires_attention
 
assert not positive_insight.is_critical
 
expect_value_error(
    lambda: EngineeringEvidence(
        key="",
        value=82.0,
    ),
    "evidence key cannot be empty",
)
 
expect_value_error(
    lambda: EngineeringEvidence(
        key="pressure_drop",
        value="",
    ),
    "string value cannot be empty",
)
 
expect_value_error(
    lambda: EngineeringInsight(
        insight_id="",
        severity=EngineeringSeverity.INFO,
        category=EngineeringCategory.GENERAL,
        title="Valid title",
        summary="Valid summary.",
    ),
    "insight ID cannot be empty",
)
 
expect_value_error(
    lambda: EngineeringInsight(
        insight_id="general.invalid_evidence",
        severity=EngineeringSeverity.INFO,
        category=EngineeringCategory.GENERAL,
        title="Invalid evidence",
        summary="Test invalid evidence validation.",
        evidence=(
            "not structured evidence",
        ),
    ),
    "Every evidence item must be an "
    "EngineeringEvidence object",
)
 
expect_value_error(
    lambda: EngineeringInsight(
        insight_id="general.invalid_severity",
        severity="warning",
        category=EngineeringCategory.GENERAL,
        title="Invalid severity",
        summary="Test severity validation.",
    ),
    "'severity' must be an "
    "EngineeringSeverity value",
)
 
expect_value_error(
    lambda: EngineeringInsight(
        insight_id="general.invalid_category",
        severity=EngineeringSeverity.INFO,
        category="thermal",
        title="Invalid category",
        summary="Test category validation.",
    ),
    "'category' must be an "
    "EngineeringCategory value",
)
 
print(
    "ALL ENGINEERING INSIGHT MODEL CHECKS PASSED"
)