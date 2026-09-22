"""
Regression checks for Pareto-dominance comparison.
"""
 
from dataclasses import replace
 
from core.candidate_objective_pipeline import (
    analyze_candidate_objectives,
)
from core.pareto_dominance import (
    ParetoDominanceError,
    candidate_dominates,
    compare_pareto_dominance,
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
        pressure_drop=40.0,
        pumping_power=0.1,
 
        thermal_resistance=0.5,
        estimated_base_temperature=112.5,
    )
 
 
def main() -> None:
    dominant_candidate = (
        create_base_candidate()
    )
 
    dominated_candidate = replace(
        dominant_candidate,
        thermal_resistance=0.8,
        pressure_drop=100.0,
        pumping_power=0.4,
    )
 
    thermal_tradeoff_candidate = replace(
        dominant_candidate,
        thermal_resistance=0.4,
        pressure_drop=120.0,
        pumping_power=0.5,
    )
 
    equal_candidate = replace(
        dominant_candidate
    )
 
    analyses = analyze_candidate_objectives(
        (
            dominant_candidate,
            dominated_candidate,
            thermal_tradeoff_candidate,
            equal_candidate,
        )
    )
 
    dominant_analysis = analyses[0]
    dominated_analysis = analyses[1]
    tradeoff_analysis = analyses[2]
    equal_analysis = analyses[3]
 
    dominance_comparison = (
        compare_pareto_dominance(
            dominant_analysis,
            dominated_analysis,
        )
    )
 
    assert (
        dominance_comparison
        .candidate_dominates
    )
 
    assert not (
        dominance_comparison
        .compared_candidate_dominates
    )
 
    assert not dominance_comparison.is_tradeoff
 
    reverse_comparison = (
        compare_pareto_dominance(
            dominated_analysis,
            dominant_analysis,
        )
    )
 
    assert not (
        reverse_comparison
        .candidate_dominates
    )
 
    assert (
        reverse_comparison
        .compared_candidate_dominates
    )
 
    assert candidate_dominates(
        dominant_analysis,
        dominated_analysis,
    )
 
    assert not candidate_dominates(
        dominated_analysis,
        dominant_analysis,
    )
 
    tradeoff_comparison = (
        compare_pareto_dominance(
            dominant_analysis,
            tradeoff_analysis,
        )
    )
 
    assert not (
        tradeoff_comparison
        .candidate_dominates
    )
 
    assert not (
        tradeoff_comparison
        .compared_candidate_dominates
    )
 
    assert tradeoff_comparison.is_tradeoff
 
    equal_comparison = (
        compare_pareto_dominance(
            dominant_analysis,
            equal_analysis,
        )
    )
 
    assert not (
        equal_comparison
        .candidate_dominates
    )
 
    assert not (
        equal_comparison
        .compared_candidate_dominates
    )
 
    assert equal_comparison.is_tradeoff
 
    try:
        compare_pareto_dominance(
            dominant_analysis,
            dominated_analysis,
            objective_tolerance=-1.0,
        )
 
    except ParetoDominanceError:
        pass
 
    else:
        raise AssertionError(
            "Negative objective tolerance must raise "
            "ParetoDominanceError."
        )
 
    print(
        "ALL PARETO DOMINANCE CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()