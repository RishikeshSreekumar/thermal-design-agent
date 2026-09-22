"""
engineering_review_status.py
 
Controlled overall and section-level statuses used by
structured engineering reviews.
 
These statuses communicate the consolidated review
outcome. They do not replace or modify deterministic
engineering assessment results.
"""
 
from enum import Enum
 
 
class EngineeringReviewStatus(
    str,
    Enum,
):
    """
    Consolidated status assigned to an engineering review
    or one category-specific review section.
 
    ACCEPTABLE:
        The available deterministic evidence does not
        identify a required corrective action.
 
    ACCEPTABLE_WITH_ACTIONS:
        The design may proceed, but identified actions or
        validations must be completed.
 
    REVIEW_REQUIRED:
        One or more engineering concerns require review
        before the design proceeds.
 
    NOT_RECOMMENDED:
        The available deterministic evidence identifies a
        serious concern that makes the current design
        unsuitable for progression.
 
    INSUFFICIENT_EVIDENCE:
        The available engineering evidence is not
        sufficient to reach a supported conclusion.
 
    NOT_APPLICABLE:
        The engineering category is not applicable to the
        current design or was not evaluated.
    """
 
    ACCEPTABLE = "acceptable"
 
    ACCEPTABLE_WITH_ACTIONS = (
        "acceptable_with_actions"
    )
 
    REVIEW_REQUIRED = "review_required"
 
    NOT_RECOMMENDED = "not_recommended"
 
    INSUFFICIENT_EVIDENCE = (
        "insufficient_evidence"
    )
 
    NOT_APPLICABLE = "not_applicable"