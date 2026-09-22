"""
Regression checks for natural-convection orientation and
radiation requirement extraction.
"""
 
from core.parser import parse_requirements
from core.validator import review_requirements
from llm.mock_provider import MockProvider
 
 
def extract(prompt: str):
    return parse_requirements(
        MockProvider().extract_requirements(prompt)
    )
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Explicit vertical
    # --------------------------------------------------
 
    vertical = extract(
        "Design a passive natural-convection heat sink "
        "with vertical orientation."
    )
 
    assert vertical.convection_mode == "natural"
 
    assert (
        vertical.natural_convection.orientation
        == "vertical"
    )
 
    assert (
        vertical.natural_convection.include_radiation
        is False
    )
 
    # --------------------------------------------------
    # Horizontal fins upward + radiation
    # --------------------------------------------------
 
    upward = extract(
        "Design a passive natural-convection heat sink "
        "mounted horizontally with fins facing upward. "
        "Include thermal radiation with surface "
        "emissivity 0.85."
    )
 
    assert (
        upward.natural_convection.orientation
        == "horizontal_fins_up"
    )
 
    assert (
        upward.natural_convection.include_radiation
        is True
    )
 
    assert (
        upward.natural_convection.surface_emissivity
        == 0.85
    )
 
    # --------------------------------------------------
    # Horizontal fins downward
    # --------------------------------------------------
 
    downward = extract(
        "Design a natural convection heat sink, "
        "horizontal with fins facing downward, "
        "without radiation."
    )
 
    assert (
        downward.natural_convection.orientation
        == "horizontal_fins_down"
    )
 
    assert (
        downward.natural_convection.include_radiation
        is False
    )
 
    # --------------------------------------------------
    # Horizontal without facing direction must clarify
    # --------------------------------------------------
 
    ambiguous = extract(
        "Design a horizontal passive natural-convection "
        "heat sink."
    )
 
    ambiguous_review = review_requirements(
        ambiguous
    )
 
    assert any(
        question.field_name
        == "natural_convection_orientation"
        for question
        in ambiguous_review.clarification_questions
    )
 
    # --------------------------------------------------
    # Radiation without emissivity must clarify
    # --------------------------------------------------
 
    missing_emissivity = extract(
        "Design a vertical passive natural-convection "
        "heat sink including thermal radiation."
    )
 
    missing_emissivity_review = (
        review_requirements(
            missing_emissivity
        )
    )
 
    assert any(
        question.field_name
        == "surface_emissivity"
        for question
        in (
            missing_emissivity_review
            .clarification_questions
        )
    )
 
    print(
        "ALL NATURAL-CONVECTION REQUIREMENT "
        "EXTRACTION CHECKS PASSED"
    )
 
 
if __name__ == "__main__":
    main()