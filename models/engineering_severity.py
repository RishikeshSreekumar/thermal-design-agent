"""
engineering_severity.py
 
Severity levels used by structured engineering insights.
"""
 
from enum import Enum
 
 
class EngineeringSeverity(
    str,
    Enum,
):
    """
    Describes the importance and urgency of an engineering
    observation.
 
    SUCCESS:
        A confirmed positive design characteristic.
 
    INFO:
        Neutral engineering information or context.
 
    WARNING:
        A concern requiring engineering attention.
 
    CRITICAL:
        A serious concern that may invalidate the design
        or require immediate corrective action.
    """
 
    SUCCESS = "success"
 
    INFO = "info"
 
    WARNING = "warning"
 
    CRITICAL = "critical"