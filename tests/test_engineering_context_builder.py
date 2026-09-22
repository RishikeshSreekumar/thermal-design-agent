"""
Focused checks for EngineeringContextBuilder.
"""
 
from intelligence.context_builder import (
    EngineeringContextBuilder,
)
from models.candidate_selection_result import (
    CandidateSelectionResult,
)
from models.design_candidate import (
    DesignCandidate,
)
from models.optimization_result import (
    OptimizationResult,
)
from models.optimization_selection import (
    OptimizationSelectionConfiguration,
    OptimizationSelectionMode,
)
from models.requirements import (
    EngineeringRequirements,
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
 
 
candidate = DesignCandidate(
    base_thickness=3.0,
    fin_thickness=1.0,
    fin_height=25.0,
    fin_spacing=3.0,
    fin_count=12,
    total_height=28.0,
    gross_frontal_area=0.0014,
    open_flow_area=0.0010,
    blockage_ratio=0.2857,
    approach_velocity=3.0,
    channel_velocity=4.2,
    reynolds_number=2500.0,
    nusselt_number=8.5,
    heat_transfer_coefficient=45.0,
    friction_factor=0.04,
    pressure_drop=18.0,
    pumping_power=0.0756,
    thermal_resistance=0.42,
    estimated_base_temperature=99.3,
)
 
selection_configuration = (
    OptimizationSelectionConfiguration(
        mode=(
            OptimizationSelectionMode
            .MINIMUM_THERMAL_RESISTANCE
        )
    )
)
 
selection_result = CandidateSelectionResult(
    configuration=selection_configuration,
    selected_candidates=(candidate,),
)
 
optimization_result = OptimizationResult(
    best_result=None,
    candidates=[candidate],
    feasible_candidate_count=1,
    rejected_candidate_count=3,
    selected_material="Al6063",
    selected_process="extrusion",
    selection_result=selection_result,
)
 
requirements = EngineeringRequirements(
    component_type="heat_sink",
    convection_mode="forced",
)
 
known_limitations = (
    "Radiation heat transfer is not yet included.",
    "Fan accuracy depends on the supplied fan curve.",
)
 
context = EngineeringContextBuilder.build(
    requirements=requirements,
    optimization_result=optimization_result,
    known_limitations=known_limitations,
)
 
assert context.requirements is requirements
 
assert (
    context.optimization_result
    is optimization_result
)
 
assert context.selection_mode == (
    OptimizationSelectionMode
    .MINIMUM_THERMAL_RESISTANCE
)
 
assert context.selected_candidates == (
    candidate,
)
 
assert context.selected_candidate is candidate
 
assert context.selected_material == "Al6063"
 
assert context.selected_process == "extrusion"
 
assert context.feasible_candidate_count == 1
 
assert context.rejected_candidate_count == 3
 
assert context.total_candidate_count == 4
 
assert context.feasibility_rate == 25.0
 
assert context.known_limitations == (
    known_limitations
)
 
assert (
    context.selected_candidates
    is selection_result.selected_candidates
)
 
expect_value_error(
    lambda: EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=OptimizationResult(
            best_result=None,
            candidates=[],
            feasible_candidate_count=0,
            rejected_candidate_count=4,
            selected_material="Al6063",
            selected_process="extrusion",
            selection_result=None,
        ),
    ),
    "no candidate selection result",
)
 
no_feasible_design_result = OptimizationResult(
    best_result=None,
    candidates=[],
    feasible_candidate_count=0,
    rejected_candidate_count=4,
    selected_material="Al6063",
    selected_process="extrusion",
    selection_result=selection_result,
)
 
expect_value_error(
    lambda: EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result=(
            no_feasible_design_result
        ),
    ),
    "no feasible design",
)
 
expect_value_error(
    lambda: EngineeringContextBuilder.build(
        requirements="invalid requirements",
        optimization_result=optimization_result,
    ),
    "'requirements' must be an "
    "EngineeringRequirements object",
)
 
expect_value_error(
    lambda: EngineeringContextBuilder.build(
        requirements=requirements,
        optimization_result="invalid result",
    ),
    "'optimization_result' must be an "
    "OptimizationResult object",
)
 
print(
    "ALL ENGINEERING CONTEXT BUILDER CHECKS PASSED"
)