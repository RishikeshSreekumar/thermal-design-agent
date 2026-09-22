"""
requirements.py
 
Engineering requirement models.
 
These dataclasses represent the structured engineering
information extracted from the user's natural-language prompt.
 
Missing values are represented using None so that the
clarification workflow can identify information that must
be requested from the user.
"""
 
import math 
from dataclasses import dataclass
from typing import Optional 
from fan.fan_curve import FanCurve
 
 
@dataclass
class Requirements:
    """
    Thermal operating requirements.
    """
 
    heat_load: Optional[float] = None
    ambient_temperature: Optional[float] = None
 
    maximum_base_temperature: Optional[
        float
    ] = None
    
    maximum_pressure_drop: Optional[
        float
    ] = None
    
    maximum_pumping_power: Optional[
        float
    ] = None
 
    air_velocity: Optional[float] = None

@dataclass(frozen=True)
class MaterialCostBudget:
    """
    Optional raw-material cost limit.
 
    The amount and currency must always be supplied
    together so that costs from different currencies
    are never compared silently.
    """
 
    maximum_amount: float
 
    currency_code: str = "INR"
 
    def __post_init__(
        self,
    ) -> None:
        """
        Validate and normalize the immutable budget.
        """
 
        if not math.isfinite(
            self.maximum_amount
        ):
            raise ValueError(
                "'maximum_amount' must be finite."
            )
 
        if self.maximum_amount <= 0.0:
            raise ValueError(
                "'maximum_amount' must be greater "
                "than zero."
            )
 
        normalized_currency_code = (
            self.currency_code.strip().upper()
        )
 
        if (
            len(normalized_currency_code) != 3
            or not normalized_currency_code.isalpha()
        ):
            raise ValueError(
                "'currency_code' must contain exactly "
                "three alphabetic characters."
            )
 
        object.__setattr__(
            self,
            "currency_code",
            normalized_currency_code,
        )

 
@dataclass
class Constraints:
    """
    Geometric envelope and commercial constraints.
    """
 
    base_length: Optional[float] = None
    base_width: Optional[float] = None
    max_height: Optional[float] = None
 
    material_cost_budget: Optional[
        MaterialCostBudget
    ] = None
 

@dataclass
class FanSpecification:
    """
    Information describing the selected fan.
    """
 
    fan_curve: Optional[FanCurve] = None
    fan_name: Optional[str] = None
    fan_count: int = 1
    speed_fraction: float = 1.0
 
 
NATURAL_CONVECTION_ORIENTATIONS = (
    "vertical",
    "horizontal_fins_up",
    "horizontal_fins_down",
)
 
 
@dataclass
class NaturalConvectionSpecification:
    """
    Configuration specific to natural-convection
    heat-sink analysis.
 
    Orientation values currently planned for the
    plate-fin solver are:
 
    - vertical
    - horizontal_fins_up
    - horizontal_fins_down
 
    Missing optional values are preserved so that the
    requirement-review or UI configuration layer can
    resolve them explicitly before engineering analysis.
    """
 
    orientation: Optional[str] = None
 
    include_radiation: bool = False
 
    surface_emissivity: Optional[float] = None
 
    surroundings_temperature: Optional[float] = None
 
@dataclass
class EngineeringRequirements:
    """
    Complete structured representation of the
    user's engineering design problem.
    """
    component_type: Optional[str] = None
    convection_mode: Optional[str] = None
    
    allowed_materials: tuple[
        str,
        ...,
    ] = ()
    
    requirements: Optional[Requirements] = None
    constraints: Optional[Constraints] = None
 
    natural_convection: Optional[
        NaturalConvectionSpecification
    ] = None
 
    fan: Optional[FanSpecification] = None