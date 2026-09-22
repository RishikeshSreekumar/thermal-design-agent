"""
plate_fin_natural_convection.py
 
Deterministic natural-convection correlations specific
to horizontal plate-fin heat sinks.
 
Implemented correlations are based on:
 
I. Tari and M. Mehrtash,
"Natural convection heat transfer from horizontal and
slightly inclined plate-fin heat sinks",
Applied Thermal Engineering, 61 (2013), 728-736.
 
The correlations distinguish:
 
- upward-facing horizontal plate-fin heat sinks;
- downward-facing horizontal plate-fin heat sinks.
 
The vertical natural-convection path remains owned by the
existing NaturalConvectionSolver and is intentionally not
duplicated here.
"""
 
import math
 
 
UPWARD_HORIZONTAL_MAX_GROUP = 5000.0
DOWNWARD_HORIZONTAL_MAX_RAYLEIGH = 1.8e4
 
 
def upward_horizontal_modified_grashof(
    *,
    grashof_based_on_spacing: float,
    fin_spacing: float,
    fin_height: float,
    heat_sink_length: float,
) -> float:
    """
    Calculate the modified Grashof number used by the
    Tari-Mehrtash upward-facing horizontal correlation.
 
    Gr'_up,h =
        Gr_S
        * (H / L)^0.5
        * (S / H)^0.38
 
    where Gr_S is based on fin spacing S.
 
    All lengths must use the same units. SI metres are
    recommended.
    """
 
    values = {
        "grashof_based_on_spacing": (
            grashof_based_on_spacing
        ),
        "fin_spacing": fin_spacing,
        "fin_height": fin_height,
        "heat_sink_length": heat_sink_length,
    }
 
    for field_name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(
                f"'{field_name}' must be finite."
            )
 
        if value <= 0.0:
            raise ValueError(
                f"'{field_name}' must be greater "
                "than zero."
            )
 
    return (
        grashof_based_on_spacing
        * (
            fin_height
            / heat_sink_length
        ) ** 0.5
        * (
            fin_spacing
            / fin_height
        ) ** 0.38
    )
 
 
def tari_mehrtash_horizontal_upward_nusselt(
    *,
    modified_grashof_number: float,
    prandtl_number: float,
) -> float:
    """
    Calculate average Nusselt number for an upward-facing
    horizontal plate-fin heat sink.
 
    Nu_S =
        0.0915 * (Gr'_up,h * Pr)^0.436
 
    The published correlation is stated for:
 
        Gr'_up,h * Pr < 5000
 
    Nusselt number is based on fin spacing S.
    """
 
    if not math.isfinite(
        modified_grashof_number
    ):
        raise ValueError(
            "Modified Grashof number must be finite."
        )
 
    if modified_grashof_number <= 0.0:
        raise ValueError(
            "Modified Grashof number must be greater "
            "than zero."
        )
 
    if not math.isfinite(
        prandtl_number
    ):
        raise ValueError(
            "Prandtl number must be finite."
        )
 
    if prandtl_number <= 0.0:
        raise ValueError(
            "Prandtl number must be greater than zero."
        )
 
    correlation_group = (
        modified_grashof_number
        * prandtl_number
    )
 
    if (
        correlation_group
        >= UPWARD_HORIZONTAL_MAX_GROUP
    ):
        raise ValueError(
            "Tari-Mehrtash upward-horizontal "
            "correlation requires "
            "Gr'_up,h * Pr < 5000."
        )
 
    return (
        0.0915
        * correlation_group ** 0.436
    )
 
 
def tari_mehrtash_horizontal_downward_nusselt(
    *,
    rayleigh_number_based_on_spacing: float,
) -> float:
    """
    Calculate average Nusselt number for a downward-facing
    horizontal plate-fin heat sink.
 
    Nu_S =
        0.0149 * Ra_S^0.5
 
    The published correlation is stated for:
 
        Ra_S < 1.8e4
 
    Rayleigh and Nusselt numbers are based on fin spacing S.
    """
 
    if not math.isfinite(
        rayleigh_number_based_on_spacing
    ):
        raise ValueError(
            "Rayleigh number must be finite."
        )
 
    if (
        rayleigh_number_based_on_spacing
        <= 0.0
    ):
        raise ValueError(
            "Rayleigh number must be greater than zero."
        )
 
    if (
        rayleigh_number_based_on_spacing
        >= DOWNWARD_HORIZONTAL_MAX_RAYLEIGH
    ):
        raise ValueError(
            "Tari-Mehrtash downward-horizontal "
            "correlation requires Ra_S < 1.8e4."
        )
 
    return (
        0.0149
        * rayleigh_number_based_on_spacing ** 0.5
    )