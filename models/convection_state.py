"""
convection_state.py
 
Common deterministic convection-state model.
 
Represents the resolved convective heat-transfer state
independently of whether convection is forced or natural.
 
Future convection models and heat-sink topologies should
converge on this interface before downstream thermal
performance is evaluated.
"""
 
from dataclasses import dataclass
 
 
@dataclass(frozen=True)
class ConvectionState:
    """
    Resolved convection state for one engineering
    configuration.
    """
 
    mode: str
 
    nusselt_number: float
    heat_transfer_coefficient: float
 
    characteristic_length: float
 
    correlation_name: str
 
    reynolds_number: float | None = None
    rayleigh_number: float | None = None
    grashof_number: float | None = None
    prandtl_number: float | None = None
 
    def __post_init__(self) -> None:
 
        if self.mode not in {
            "forced",
            "natural",
        }:
            raise ValueError(
                "'mode' must be either 'forced' or "
                "'natural'."
            )
 
        if self.nusselt_number <= 0:
            raise ValueError(
                "'nusselt_number' must be greater "
                "than zero."
            )
 
        if self.heat_transfer_coefficient <= 0:
            raise ValueError(
                "'heat_transfer_coefficient' must be "
                "greater than zero."
            )
 
        if self.characteristic_length <= 0:
            raise ValueError(
                "'characteristic_length' must be greater "
                "than zero."
            )
 
        if not isinstance(
            self.correlation_name,
            str,
        ):
            raise ValueError(
                "'correlation_name' must be a string."
            )
 
        if not self.correlation_name.strip():
            raise ValueError(
                "'correlation_name' must not be empty."
            )
 
        if (
            self.reynolds_number is not None
            and self.reynolds_number < 0
        ):
            raise ValueError(
                "'reynolds_number' cannot be negative."
            )
 
        if (
            self.rayleigh_number is not None
            and self.rayleigh_number < 0
        ):
            raise ValueError(
                "'rayleigh_number' cannot be negative."
            )
 
        if (
            self.grashof_number is not None
            and self.grashof_number < 0
        ):
            raise ValueError(
                "'grashof_number' cannot be negative."
            )
 
        if (
            self.prandtl_number is not None
            and self.prandtl_number <= 0
        ):
            raise ValueError(
                "'prandtl_number' must be greater than "
                "zero when supplied."
            )