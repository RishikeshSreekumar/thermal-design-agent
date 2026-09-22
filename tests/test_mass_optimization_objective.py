"""
Regression checks for mass as an explicit optimization
objective.
 
The regression verifies that:
 
- Mass is available through the objective registry.
- Mass is extracted from DesignCandidate.
- Lower mass receives the better normalized value.
- Weighted selection can use mass.
- Pareto selection can use mass.
- Candidate selection requires valid physical properties
  whenever mass is selected.
- Existing default objective behavior remains unchanged.
"""
 
import math
from dataclasses import replace
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.candidate_selector import (
    CandidateSelectionError,
    select_candidates,
)
from core.candidate_state_validator import (
    CandidateStateValidationError,
)
from core.objective_registry import (
    DEFAULT_OPTIMIZATION_OBJECTIVES,
    MASS_OBJECTIVE,
    THERMAL_RESISTANCE_OBJECTIVE,
    get_optimization_objective,
)
from models.design_candidate import DesignCandidate
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.scoring_configuration import (
    ObjectiveWeight,
    ScoringConfiguration,
)
 
 
def create_base_candidate(
) -> DesignCandidate:
    """
    Create one complete evaluated candidate with resolved
    physical state.
    """
 
    return DesignCandidate(
        base_thickness=3.0,
        fin_thickness=0.8,
        fin_height=8.0,
        fin_spacing=1.6,
        fin_count=21,
        total_height=11.0,
 
        gross_frontal_area=0.0004,
        open_flow_area=0.000256,
        blockage_ratio=0.36,
        approach_velocity=5.0,
        channel_velocity=7.8125,
 
        reynolds_number=1295.405982905983,
        nusselt_number=7.54,
        heat_transfer_coefficient=74.36325,
 
        friction_factor=0.049405,
        pressure_drop=80.0,
        pumping_power=0.20,
 
        thermal_resistance=0.50,
        estimated_base_temperature=112.5,
 
        hydraulic_diameter=(
            0.0026666666666666666
        ),
 
        solid_volume=1.50e-5,
        mass=0.0405,
    )
 
 
def create_mass_weighted_configuration(
) -> OptimizationSelectionConfiguration:
    """
    Create a weighted configuration using thermal
    resistance and mass.
    """
 
    return OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .WEIGHTED_SCORE
        ),
        scoring_configuration=(
            ScoringConfiguration(
                objective_weights=(
                    ObjectiveWeight(
                        objective_key=(
                            "thermal_resistance"
                        ),
                        weight=0.3,
                    ),
                    ObjectiveWeight(
                        objective_key="mass",
                        weight=0.7,
                    ),
                )
            )
        ),
        objectives=(
            THERMAL_RESISTANCE_OBJECTIVE,
            MASS_OBJECTIVE,
        ),
    )
 
 
def create_mass_pareto_configuration(
) -> OptimizationSelectionConfiguration:
    """
    Create an explicit thermal-resistance and mass Pareto
    configuration.
    """
 
    return OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .PARETO_FRONT
        ),
        objectives=(
            THERMAL_RESISTANCE_OBJECTIVE,
            MASS_OBJECTIVE,
        ),
    )
 
 
def main() -> None:
    # --------------------------------------------------
    # Registry definition
    # --------------------------------------------------
 
    mass_objective = (
        get_optimization_objective(
            "mass"
        )
    )
 
    assert mass_objective is MASS_OBJECTIVE
 
    assert (
        mass_objective.candidate_attribute
        == "mass"
    )
 
    assert mass_objective.unit == "kg"
 
    assert (
        MASS_OBJECTIVE
        not in DEFAULT_OPTIMIZATION_OBJECTIVES
    )
 
    # --------------------------------------------------
    # Candidate trade-off set
    # --------------------------------------------------
 
    thermal_focused_candidate = (
        create_base_candidate()
    )
 
    balanced_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.60,
        mass=0.0300,
        solid_volume=(
            0.0300 / 2700.0
        ),
    )
 
    mass_focused_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.80,
        mass=0.0200,
        solid_volume=(
            0.0200 / 2700.0
        ),
    )
 
    dominated_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.70,
        mass=0.0350,
        solid_volume=(
            0.0350 / 2700.0
        ),
    )
 
    candidates = (
        dominated_candidate,
        mass_focused_candidate,
        balanced_candidate,
        thermal_focused_candidate,
    )
 
    mass_objectives = (
        THERMAL_RESISTANCE_OBJECTIVE,
        MASS_OBJECTIVE,
    )
 
    # --------------------------------------------------
    # Raw extraction and normalization
    # --------------------------------------------------
 
    analyses = analyze_candidate_objectives(
        candidates,
        objectives=mass_objectives,
    )
 
    assert math.isclose(
        analyses[0]
        .raw_report
        .get_value("mass"),
        0.0350,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[1]
        .normalized_report
        .get_normalized_value("mass"),
        0.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[3]
        .normalized_report
        .get_normalized_value("mass"),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[3]
        .normalized_report
        .get_normalized_value(
            "thermal_resistance"
        ),
        0.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
 
    # --------------------------------------------------
    # Weighted selection using mass
    # --------------------------------------------------
 
    weighted_result = select_candidates(
        candidates,
        create_mass_weighted_configuration(),
    )
 
    assert weighted_result.uses_weighted_selection
 
    assert (
        weighted_result.selected_candidate
        is mass_focused_candidate
    )
 
    mass_contribution = (
        weighted_result
        .weighted_result
        .best_candidate
        .scored_candidate
        .get_contribution("mass")
    )
 
    assert (
        mass_contribution.objective
        is MASS_OBJECTIVE
    )
 
    # --------------------------------------------------
    # Pareto selection using mass
    # --------------------------------------------------
 
    pareto_result = select_candidates(
        candidates,
        create_mass_pareto_configuration(),
    )
 
    assert pareto_result.uses_pareto_selection
 
    assert (
        dominated_candidate
        not in pareto_result.selected_candidates
    )
 
    assert (
        len(
            pareto_result.selected_candidates
        )
        == 3
    )
 
    assert (
        thermal_focused_candidate
        in pareto_result.selected_candidates
    )
 
    assert (
        balanced_candidate
        in pareto_result.selected_candidates
    )
 
    assert (
        mass_focused_candidate
        in pareto_result.selected_candidates
    )
 
    # --------------------------------------------------
    # Mass objective requires physical state
    # --------------------------------------------------
 
    unresolved_candidate = replace(
        thermal_focused_candidate,
        solid_volume=0.0,
        mass=0.0,
    )
 
    try:
        select_candidates(
            (
                unresolved_candidate,
                balanced_candidate,
            ),
            create_mass_weighted_configuration(),
        )
 
    except CandidateSelectionError as exc:
        assert isinstance(
            exc.__cause__,
            CandidateStateValidationError,
        )
 
        assert (
            "'solid_volume' must be greater than zero"
            in str(exc.__cause__)
        )
 
    else:
        raise AssertionError(
            "Mass-weighted selection accepted unresolved "
            "physical candidate state."
        )
 
    try:
        select_candidates(
            (
                thermal_focused_candidate,
                replace(
                    balanced_candidate,
                    mass=float("nan"),
                ),
            ),
            create_mass_pareto_configuration(),
        )
 
    except CandidateSelectionError as exc:
        assert isinstance(
            exc.__cause__,
            CandidateStateValidationError,
        )
 
        assert (
            "'mass' must be finite"
            in str(exc.__cause__)
        )
 
    else:
        raise AssertionError(
            "Mass Pareto selection accepted non-finite "
            "candidate mass."
        )
 
    # --------------------------------------------------
    # Default objectives do not require physical state
    # --------------------------------------------------
 
    unresolved_default_candidates = (
        replace(
            thermal_focused_candidate,
            solid_volume=0.0,
            mass=0.0,
        ),
        replace(
            balanced_candidate,
            solid_volume=0.0,
            mass=0.0,
        ),
    )
 
    default_pareto_configuration = (
        OptimizationSelectionConfiguration(
            mode=(
                OptimizationSelectionMode
                .PARETO_FRONT
            )
        )
    )
 
    default_pareto_result = select_candidates(
        unresolved_default_candidates,
        default_pareto_configuration,
    )
 
    assert default_pareto_result.uses_pareto_selection
 
    print(
        "ALL MASS OPTIMIZATION OBJECTIVE "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()