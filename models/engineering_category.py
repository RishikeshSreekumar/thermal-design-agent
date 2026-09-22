"""
engineering_category.py
 
Engineering disciplines used to classify structured
engineering insights.
"""
 
from enum import Enum
 
 
class EngineeringCategory(
    str,
    Enum,
):
    """
    Identifies the engineering area associated with an
    insight.
    """
 
    THERMAL = "thermal"
 
    AIRFLOW = "airflow"
 
    GEOMETRY = "geometry"
 
    MANUFACTURING = "manufacturing"
 
    MATERIAL = "material"
 
    COST = "cost"
 
    OPTIMIZATION = "optimization"
 
    REQUIREMENTS = "requirements"
 
    MODEL_LIMITATION = "model_limitation"
 
    GENERAL = "general"