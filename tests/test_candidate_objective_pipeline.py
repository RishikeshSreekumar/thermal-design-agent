"""
Regression checks for the candidate objective-analysis
pipeline.
"""
 
import math
from dataclasses import replace
 
from core.candidate_objective_pipeline import (
    CandidateObjectivePipelineError,
    analyze_candidate_objectives,
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
        pumping_power=0.1,
 
        thermal_resistance=0.5,
        estimated_base_temperature=112.5,
    )
 
 
def main() -> None:
    first_candidate = create_base_candidate()
 
    second_candidate = replace(
        first_candidate,
        thermal_resistance=0.7,
        pressure_drop=60.0,
        pumping_power=0.2,
    )
 
    third_candidate = replace(
        first_candidate,
        thermal_resistance=0.9,
        pressure_drop=20.0,
        pumping_power=0.3,
    )
 
    candidates = (
        first_candidate,
        second_candidate,
        third_candidate,
    )
 
    analyses = analyze_candidate_objectives(
        candidates
    )
 
    assert len(analyses) == 3
 
    for index, analysis in enumerate(analyses):
        assert (
            analysis.candidate
            is candidates[index]
        )
 
        assert len(
            analysis.raw_report.results
        ) == 3
 
        assert len(
            analysis.normalized_report.results
        ) == 3
 
    assert math.isclose(
        analyses[0]
        .normalized_report
        .get_normalized_value(
            "thermal_resistance"
        ),
        0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[1]
        .normalized_report
        .get_normalized_value(
            "thermal_resistance"
        ),
        0.5,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[2]
        .normalized_report
        .get_normalized_value(
            "thermal_resistance"
        ),
        1.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[0]
        .normalized_report
        .get_normalized_value(
            "pressure_drop"
        ),
        1.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[1]
        .normalized_report
        .get_normalized_value(
            "pressure_drop"
        ),
        0.5,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[2]
        .normalized_report
        .get_normalized_value(
            "pressure_drop"
        ),
        0.0,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[1]
        .normalized_report
        .get_normalized_value(
            "pumping_power"
        ),
        0.5,
        abs_tol=1e-12,
    )
 
    assert math.isclose(
        analyses[1]
        .raw_report
        .get_value(
            "thermal_resistance"
        ),
        0.7,
        abs_tol=1e-12,
    )
 
    try:
        analyze_candidate_objectives(())
 
    except CandidateObjectivePipelineError:
        pass
 
    else:
        raise AssertionError(
            "Empty candidate collection must raise "
            "CandidateObjectivePipelineError."
        )
 
    try:
        analyze_candidate_objectives(
            candidates,
            objectives=(),
        )
 
    except CandidateObjectivePipelineError:
        pass
 
    else:
        raise AssertionError(
            "Empty objective collection must raise "
            "CandidateObjectivePipelineError."
        )
 
    print(
        "ALL CANDIDATE OBJECTIVE PIPELINE "
        "CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()