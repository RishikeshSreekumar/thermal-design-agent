"""
context_builder.py
 
Build the shared engineering context used by the
engineering intelligence layer.
 
This module only assembles deterministic engineering
data. It does not perform engineering calculations,
candidate selection, or AI inference.
"""
 
from models.engineering_context import (
    EngineeringContext,
)
from models.optimization_result import (
    OptimizationResult,
)
from models.requirements import (
    EngineeringRequirements,
)
 
 
class EngineeringContextBuilder:
    """
    Build validated engineering contexts from completed
    deterministic optimization results.
    """
 
    @staticmethod
    def build(
        requirements: EngineeringRequirements,
        optimization_result: OptimizationResult,
        known_limitations: tuple[
            str,
            ...,
        ] = (),
    ) -> EngineeringContext:
        """
        Construct an EngineeringContext from an existing
        optimization result.
 
        The optimization run must have completed candidate
        selection before the context can be created.
        """
 
        if not isinstance(
            requirements,
            EngineeringRequirements,
        ):
            raise ValueError(
                "'requirements' must be an "
                "EngineeringRequirements object."
            )
 
        if not isinstance(
            optimization_result,
            OptimizationResult,
        ):
            raise ValueError(
                "'optimization_result' must be an "
                "OptimizationResult object."
            )
 
        selection_result = (
            optimization_result.selection_result
        )
 
        if selection_result is None:
            raise ValueError(
                "Cannot build engineering context because "
                "the optimization result has no candidate "
                "selection result."
            )
 
        if not optimization_result.has_feasible_design:
            raise ValueError(
                "Cannot build engineering context because "
                "the optimization result has no feasible "
                "design."
            )
 
        if not selection_result.selected_candidates:
            raise ValueError(
                "Cannot build engineering context because "
                "no candidates were selected."
            )
 
        return EngineeringContext(
            requirements=requirements,
            optimization_result=optimization_result,
            selection_mode=(
                selection_result.configuration.mode
            ),
            selected_candidates=(
                selection_result.selected_candidates
            ),
            selected_material=(
                optimization_result.selected_material
            ),
            selected_process=(
                optimization_result.selected_process
            ),
            feasible_candidate_count=(
                optimization_result
                .feasible_candidate_count
            ),
            rejected_candidate_count=(
                optimization_result
                .rejected_candidate_count
            ),
            known_limitations=known_limitations,
        )