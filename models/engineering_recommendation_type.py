"""
engineering_recommendation_type.py
 
Controlled recommendation classifications.
 
These values classify recommendations for presentation and
workflow purposes only. They are not new engineering
evaluator categories.
"""
 
from enum import Enum
 
 
class EngineeringRecommendationType(
    str,
    Enum,
):
    """
    Functional type of one engineering recommendation.
    """
 
    CORRECTIVE_ACTION = "corrective_action"
 
    VALIDATION = "validation"
 
    DESIGN_IMPROVEMENT = "design_improvement"
 
    TRADEOFF_REVIEW = "tradeoff_review"