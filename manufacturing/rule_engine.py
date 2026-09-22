"""
rule_engine.py
 
Manufacturing rule engine for evaluating heat-sink geometry
against a material-process capability.
 
The engine returns a ManufacturingAssessment containing:
 
- feasibility status
- violated rules
- warnings
- checked rules
"""
 
from models.design_candidate import DesignCandidate
from models.manufacturing import ManufacturingAssessment
from models.process_capability import ProcessCapability
 
 
def assess_manufacturability(
    candidate: DesignCandidate,
    capability: ProcessCapability,
    maximum_total_height: float,
) -> ManufacturingAssessment:
    """
    Evaluate one design candidate against one
    material-process capability.
 
    Parameters
    ----------
    candidate:
        Candidate geometry and thermal result.
 
    capability:
        Material-process manufacturing limits.
 
    maximum_total_height:
        Maximum permitted heat-sink height, including
        base and fins.
 
    Returns
    -------
    ManufacturingAssessment
        Manufacturing feasibility result.
    """
 
    violations: list[str] = []
    warnings: list[str] = []
    checked_rules: list[str] = []
 
    # --------------------------------------------------
    # Rule 1 — Minimum fin thickness
    # --------------------------------------------------
 
    checked_rules.append(
        "Minimum fin thickness"
    )
 
    if (
        candidate.fin_thickness
        < capability.minimum_fin_thickness
    ):
        violations.append(
            (
                f"Fin thickness is "
                f"{candidate.fin_thickness:.2f} mm, below the "
                f"minimum configured capability of "
                f"{capability.minimum_fin_thickness:.2f} mm."
            )
        )
 
    # --------------------------------------------------
    # Rule 2 — Minimum clear fin spacing
    # --------------------------------------------------
 
    checked_rules.append(
        "Minimum fin spacing"
    )
 
    if (
        candidate.fin_spacing
        < capability.minimum_fin_spacing
    ):
        violations.append(
            (
                f"Fin spacing is "
                f"{candidate.fin_spacing:.2f} mm, below the "
                f"minimum configured capability of "
                f"{capability.minimum_fin_spacing:.2f} mm."
            )
        )
 
    # --------------------------------------------------
    # Rule 3 — Fin height/thickness ratio
    # --------------------------------------------------
 
    checked_rules.append(
        "Maximum fin height-to-thickness ratio"
    )
 
    if candidate.fin_thickness <= 0:
        violations.append(
            "Fin thickness must be greater than 0 mm."
        )
    else:
        height_to_thickness = (
            candidate.fin_height
            / candidate.fin_thickness
        )
 
        if (
            height_to_thickness
            > capability
            .maximum_fin_height_to_thickness_ratio
        ):
            violations.append(
                (
                    "Fin height-to-thickness ratio is "
                    f"{height_to_thickness:.2f}, above the "
                    "configured maximum of "
                    f"{capability.maximum_fin_height_to_thickness_ratio:.2f}."
                )
            )
 
        elif (
            height_to_thickness
            > 0.9
            * capability
            .maximum_fin_height_to_thickness_ratio
        ):
            warnings.append(
                (
                    "Fin height-to-thickness ratio is close "
                    "to the configured process limit."
                )
            )
 
    # --------------------------------------------------
    # Rule 4 — Fin height/spacing ratio
    # --------------------------------------------------
 
    checked_rules.append(
        "Maximum fin height-to-spacing ratio"
    )
 
    if candidate.fin_spacing <= 0:
        violations.append(
            "Fin spacing must be greater than 0 mm."
        )
    else:
        height_to_spacing = (
            candidate.fin_height
            / candidate.fin_spacing
        )
 
        if (
            height_to_spacing
            > capability
            .maximum_fin_height_to_spacing_ratio
        ):
            violations.append(
                (
                    "Fin height-to-spacing ratio is "
                    f"{height_to_spacing:.2f}, above the "
                    "configured maximum of "
                    f"{capability.maximum_fin_height_to_spacing_ratio:.2f}."
                )
            )
 
        elif (
            height_to_spacing
            > 0.9
            * capability
            .maximum_fin_height_to_spacing_ratio
        ):
            warnings.append(
                (
                    "Fin height-to-spacing ratio is close "
                    "to the configured process limit."
                )
            )
 
    # --------------------------------------------------
    # Rule 5 — Base thickness range
    # --------------------------------------------------
 
    checked_rules.append(
        "Base thickness range"
    )
 
    if (
        candidate.base_thickness
        < capability.minimum_base_thickness
    ):
        violations.append(
            (
                f"Base thickness is "
                f"{candidate.base_thickness:.2f} mm, below the "
                f"configured minimum of "
                f"{capability.minimum_base_thickness:.2f} mm."
            )
        )
 
    if (
        candidate.base_thickness
        > capability.maximum_base_thickness
    ):
        violations.append(
            (
                f"Base thickness is "
                f"{candidate.base_thickness:.2f} mm, above the "
                f"configured maximum of "
                f"{capability.maximum_base_thickness:.2f} mm."
            )
        )
 
    # --------------------------------------------------
    # Rule 6 — Total-height constraint
    # --------------------------------------------------
 
    checked_rules.append(
        "Maximum total height"
    )
 
    calculated_total_height = (
        candidate.base_thickness
        + candidate.fin_height
    )
 
    if abs(
        candidate.total_height
        - calculated_total_height
    ) > 1e-9:
        violations.append(
            (
                "Stored candidate total height does not match "
                "base thickness plus fin height."
            )
        )
 
    if candidate.total_height > maximum_total_height:
        violations.append(
            (
                f"Total heat-sink height is "
                f"{candidate.total_height:.2f} mm, above the "
                f"maximum permitted height of "
                f"{maximum_total_height:.2f} mm."
            )
        )
 
    # --------------------------------------------------
    # Rule 7 — Basic geometry validity
    # --------------------------------------------------
 
    checked_rules.append(
        "Basic geometry validity"
    )
 
    if candidate.fin_height <= 0:
        violations.append(
            "Fin height must be greater than 0 mm."
        )
 
    if candidate.fin_count < 2:
        violations.append(
            "At least two fins are required."
        )
 
    # --------------------------------------------------
    # Supplier-review warning
    # --------------------------------------------------
 
    if capability.supplier_review_required:
        warnings.append(
            (
                "The capability uses generic engineering "
                "limits. Supplier review is required before "
                "release for manufacture."
            )
        )
 
    return ManufacturingAssessment(
        process=capability.process_name,
        material=capability.material.display_name,
        is_feasible=not violations,
        violations=violations,
        warnings=warnings,
        checked_rules=checked_rules,
    )