"""
Regression checks for orientation-specific horizontal
plate-fin natural-convection correlations.
"""
 
import math
 
from physics.plate_fin_natural_convection import (
    DOWNWARD_HORIZONTAL_MAX_RAYLEIGH,
    UPWARD_HORIZONTAL_MAX_GROUP,
    tari_mehrtash_horizontal_downward_nusselt,
    tari_mehrtash_horizontal_upward_nusselt,
    upward_horizontal_modified_grashof,
)
 
 
def assert_value_error(
    callback,
) -> None:
    try:
        callback()
 
    except ValueError:
        return
 
    raise AssertionError(
        "Expected ValueError."
    )
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Modified Grashof relationship
    # --------------------------------------------------
 
    grashof_spacing = 1000.0
    fin_spacing = 0.012
    fin_height = 0.015
    heat_sink_length = 0.250
 
    modified_grashof = (
        upward_horizontal_modified_grashof(
            grashof_based_on_spacing=(
                grashof_spacing
            ),
            fin_spacing=fin_spacing,
            fin_height=fin_height,
            heat_sink_length=heat_sink_length,
        )
    )
 
    expected_modified_grashof = (
        grashof_spacing
        * (
            fin_height
            / heat_sink_length
        ) ** 0.5
        * (
            fin_spacing
            / fin_height
        ) ** 0.38
    )
 
    assert math.isclose(
        modified_grashof,
        expected_modified_grashof,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Upward horizontal correlation
    # --------------------------------------------------
 
    modified_grashof = 1000.0
    prandtl_number = 0.71
 
    upward_nusselt = (
        tari_mehrtash_horizontal_upward_nusselt(
            modified_grashof_number=(
                modified_grashof
            ),
            prandtl_number=prandtl_number,
        )
    )
 
    expected_upward_nusselt = (
        0.0915
        * (
            modified_grashof
            * prandtl_number
        ) ** 0.436
    )
 
    assert math.isclose(
        upward_nusselt,
        expected_upward_nusselt,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Downward horizontal correlation
    # --------------------------------------------------
 
    rayleigh_spacing = 10000.0
 
    downward_nusselt = (
        tari_mehrtash_horizontal_downward_nusselt(
            rayleigh_number_based_on_spacing=(
                rayleigh_spacing
            ),
        )
    )
 
    expected_downward_nusselt = (
        0.0149
        * rayleigh_spacing ** 0.5
    )
 
    assert math.isclose(
        downward_nusselt,
        expected_downward_nusselt,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Correlation validity limits
    # --------------------------------------------------
 
    assert_value_error(
        lambda: (
            tari_mehrtash_horizontal_upward_nusselt(
                modified_grashof_number=(
                    UPWARD_HORIZONTAL_MAX_GROUP
                    / 0.71
                ),
                prandtl_number=0.71,
            )
        )
    )
 
    assert_value_error(
        lambda: (
            tari_mehrtash_horizontal_downward_nusselt(
                rayleigh_number_based_on_spacing=(
                    DOWNWARD_HORIZONTAL_MAX_RAYLEIGH
                ),
            )
        )
    )
 
    # --------------------------------------------------
    # Invalid geometry
    # --------------------------------------------------
 
    assert_value_error(
        lambda: upward_horizontal_modified_grashof(
            grashof_based_on_spacing=1000.0,
            fin_spacing=0.0,
            fin_height=0.015,
            heat_sink_length=0.250,
        )
    )
 
    print(
        "ALL PLATE-FIN NATURAL-CONVECTION "
        "CORRELATION CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()