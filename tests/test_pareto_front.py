"""
Regression checks for Pareto-front extraction.
"""
 
from dataclasses import replace
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.pareto_front import (
    ParetoFrontError,
    extract_pareto_front,
)
from models.design_candidate import DesignCandidate
 
 
def create_base_candidate() -> DesignCandidate:
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
        pressure_drop=100.0,
        pumping_power=0.3,
 
        thermal_resistance=0.5,
        estimated_base_temperature=112.5,
    )
 
 
def main() -> None:
    thermal_focused_candidate = (
        create_base_candidate()
    )
 
    balanced_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.7,
        pressure_drop=60.0,
        pumping_power=0.2,
    )
 
    airflow_focused_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.9,
        pressure_drop=20.0,
        pumping_power=0.1,
    )
 
    dominated_candidate = replace(
        thermal_focused_candidate,
        thermal_resistance=0.8,
        pressure_drop=80.0,
        pumping_power=0.25,
    )
 
    candidates = (
        dominated_candidate,
        airflow_focused_candidate,
        balanced_candidate,
        thermal_focused_candidate,
    )
 
    analyses = analyze_candidate_objectives(
        candidates
    )
 
    result = extract_pareto_front(
        analyses
    )
 
    assert result.total_candidate_count == 4
 
    assert result.pareto_candidate_count == 3
 
    assert result.dominated_candidate_count == 1
 
    assert result.has_tradeoff_set
 
    assert tuple(
        analysis.candidate
        for analysis
        in result.pareto_candidates
    ) == (
        airflow_focused_candidate,
        balanced_candidate,
        thermal_focused_candidate,
    )
 
    assert tuple(
        analysis.candidate
        for analysis
        in result.dominated_candidates
    ) == (
        dominated_candidate,
    )
 
    single_analysis = (
        analyze_candidate_objectives(
            (
                thermal_focused_candidate,
            )
        )
    )
 
    single_result = extract_pareto_front(
        single_analysis
    )
 
    assert (
        single_result.pareto_candidate_count
        == 1
    )
 
    assert (
        single_result.dominated_candidate_count
        == 0
    )
 
    assert not single_result.has_tradeoff_set
 
    assert (
        single_result.pareto_candidates[0]
        .candidate
        is thermal_focused_candidate
    )
 
    try:
        extract_pareto_front(())
 
    except ParetoFrontError:
        pass
 
    else:
        raise AssertionError(
            "Empty analyses must raise "
            "ParetoFrontError."
        )
 
    try:
        extract_pareto_front(
            analyses,
            objective_tolerance=-1.0,
        )
 
    except ParetoFrontError:
        pass
 
    else:
        raise AssertionError(
            "Negative objective tolerance must raise "
            "ParetoFrontError."
        )
 
    print(
        "ALL PARETO FRONT CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()
 