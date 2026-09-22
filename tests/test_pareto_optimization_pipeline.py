"""
Regression checks for the complete Pareto optimization
pipeline.
"""
 
from dataclasses import replace
 
from core.pareto_optimization_pipeline import (
    ParetoOptimizationPipelineError,
    optimize_candidates_by_pareto_front,
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
 
    result = (
        optimize_candidates_by_pareto_front(
            candidates
        )
    )
 
    assert len(result.analyses) == 4
 
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
 
    assert tuple(
        metadata.analysis.candidate
        for metadata
        in result.pareto_metadata
    ) == (
        airflow_focused_candidate,
        balanced_candidate,
        thermal_focused_candidate,
    )
 
    dominated_metadata = (
        result.metadata.get_metadata(
            result.analyses[0]
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
 
    balanced_metadata = (
        result.metadata.get_metadata(
            result.analyses[2]
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
 
    single_result = (
        optimize_candidates_by_pareto_front(
            (
                thermal_focused_candidate,
            )
        )
    )
 
    assert (
        single_result.total_candidate_count
        == 1
    )
 
    assert (
        single_result.pareto_candidate_count
        == 1
    )
 
    assert (
        single_result.dominated_candidate_count
        == 0
    )
 
    assert not (
        single_result.has_tradeoff_set
    )
 
    assert (
        single_result.pareto_candidates[0]
        .candidate
        is thermal_focused_candidate
    )
 
    try:
        optimize_candidates_by_pareto_front(
            ()
        )
 
    except ParetoOptimizationPipelineError:
        pass
 
    else:
        raise AssertionError(
            "Empty candidate collection must raise "
            "ParetoOptimizationPipelineError."
        )
 
    try:
        optimize_candidates_by_pareto_front(
            candidates,
            objectives=(),
        )
 
    except ParetoOptimizationPipelineError:
        pass
 
    else:
        raise AssertionError(
            "Empty custom objectives must raise "
            "ParetoOptimizationPipelineError."
        )
 
    try:
        optimize_candidates_by_pareto_front(
            candidates,
            objective_tolerance=-1.0,
        )
 
    except ParetoOptimizationPipelineError:
        pass
 
    else:
        raise AssertionError(
            "Negative objective tolerance must raise "
            "ParetoOptimizationPipelineError."
        )
 
    print(
        "ALL PARETO OPTIMIZATION PIPELINE "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()