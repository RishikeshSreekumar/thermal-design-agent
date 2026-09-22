"""
Regression checks for candidate-level Pareto metadata.
"""
 
from dataclasses import replace
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.pareto_metadata import (
    ParetoMetadataError,
    analyze_pareto_metadata,
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
 
    result = analyze_pareto_metadata(
        analyses
    )
 
    assert result.total_candidate_count == 4
 
    assert result.pareto_candidate_count == 3
 
    assert result.dominated_candidate_count == 1
 
    assert tuple(
        metadata.analysis.candidate
        for metadata in result.candidates
    ) == candidates
 
    dominated_metadata = (
        result.get_metadata(
            analyses[0]
        )
    )
 
    assert not (
        dominated_metadata
        .is_pareto_candidate
    )
 
    assert (
        dominated_metadata
        .dominates_count
        == 0
    )
 
    assert (
        dominated_metadata
        .dominated_by_count
        == 1
    )
 
    airflow_metadata = (
        result.get_metadata(
            analyses[1]
        )
    )
 
    assert (
        airflow_metadata
        .is_pareto_candidate
    )
 
    assert (
        airflow_metadata
        .dominates_count
        == 0
    )
 
    assert (
        airflow_metadata
        .dominated_by_count
        == 0
    )
 
    balanced_metadata = (
        result.get_metadata(
            analyses[2]
        )
    )
 
    assert (
        balanced_metadata
        .is_pareto_candidate
    )
 
    assert (
        balanced_metadata
        .dominates_count
        == 1
    )
 
    assert (
        balanced_metadata
        .dominated_by_count
        == 0
    )
 
    thermal_metadata = (
        result.get_metadata(
            analyses[3]
        )
    )
 
    assert (
        thermal_metadata
        .is_pareto_candidate
    )
 
    assert (
        thermal_metadata
        .dominates_count
        == 0
    )
 
    assert (
        thermal_metadata
        .dominated_by_count
        == 0
    )
 
    assert tuple(
        metadata.analysis.candidate
        for metadata
        in result.pareto_candidates
    ) == (
        airflow_focused_candidate,
        balanced_candidate,
        thermal_focused_candidate,
    )
 
    assert tuple(
        metadata.analysis.candidate
        for metadata
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
 
    single_result = (
        analyze_pareto_metadata(
            single_analysis
        )
    )
 
    single_metadata = (
        single_result.candidates[0]
    )
 
    assert (
        single_metadata
        .is_pareto_candidate
    )
 
    assert (
        single_metadata
        .dominates_count
        == 0
    )
 
    assert (
        single_metadata
        .dominated_by_count
        == 0
    )
 
    try:
        analyze_pareto_metadata(())
 
    except ParetoMetadataError:
        pass
 
    else:
        raise AssertionError(
            "Empty analyses must raise "
            "ParetoMetadataError."
        )
 
    try:
        analyze_pareto_metadata(
            analyses,
            objective_tolerance=-1.0,
        )
 
    except ParetoMetadataError:
        pass
 
    else:
        raise AssertionError(
            "Negative objective tolerance must raise "
            "ParetoMetadataError."
        )
 
    try:
        result.get_metadata(
            single_analysis[0]
        )
 
    except KeyError:
        pass
 
    else:
        raise AssertionError(
            "Unknown candidate analysis must raise "
            "KeyError."
        )
 
    print(
        "ALL PARETO METADATA CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()