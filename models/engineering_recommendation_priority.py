"""
engineering_recommendation_priority.py
 
Controlled priority levels used by the deterministic
Recommendation Engine.
 
Priority describes recommended action order. It does not
replace EngineeringSeverity and does not introduce an
engineering acceptance threshold.
"""
 
from enum import Enum
 
 
class EngineeringRecommendationPriority(
    str,
    Enum,
):
    """
    Priority assigned to one engineering recommendation.
 
    CRITICAL:
        Must be addressed before design progression.
 
    HIGH:
        Important action requiring prompt engineering
        attention.
 
    MEDIUM:
        Recommended action that should be addressed during
        normal design refinement or validation.
 
    LOW:
        Useful improvement or follow-up having lower
        immediate engineering urgency.
    """
 
    CRITICAL = "critical"
 
    HIGH = "high"
 
    MEDIUM = "medium"
 
    LOW = "low"