"""
manufacturing.py
 
Models used to assess heat-sink manufacturing feasibility.
 
Manufacturing rules are kept separate from thermal-performance
calculations so that different processes can later use their
own capability limits.
"""
 
from dataclasses import dataclass, field
 
 
@dataclass
class ManufacturingAssessment:
    """
    Manufacturing feasibility result for one design candidate.
    """
 
    process: str
    material: str
 
    is_feasible: bool
 
    violations: list[str] = field(
        default_factory=list
    )
 
    warnings: list[str] = field(
        default_factory=list
    )
 
    checked_rules: list[str] = field(
        default_factory=list
    )
 
    @property
    def status(self) -> str:
        """
        Return a user-friendly feasibility status.
        """
 
        if not self.is_feasible:
            return "Rejected"
 
        if self.warnings:
            return "Feasible with review"
 
        return "Feasible"