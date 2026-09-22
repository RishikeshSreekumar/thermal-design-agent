"""
test_requirements_review.py
 
Tests the engineering requirement clarification and validation workflow.
"""
 
from core.parser import parse_requirements
from core.validator import review_requirements
 
 
def print_review(title: str, data: dict) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
 
    engineering = parse_requirements(data)
    review = review_requirements(engineering)
 
    print()
    print("Parsed requirements:")
    print(review.engineering_requirements)
 
    print()
    print("Can proceed:", review.can_proceed)
    print("Needs clarification:", review.needs_clarification)
    print("Has validation errors:", review.has_validation_errors)
 
    if review.clarification_questions:
        print()
        print("Clarification questions:")
 
        for index, question in enumerate(
            review.clarification_questions,
            start=1,
        ):
            print(
                f"{index}. [{question.field_name}] "
                f"{question.question}"
            )
            print(f"   Reason: {question.reason}")
 
    if review.validation_errors:
        print()
        print("Validation errors:")
 
        for error in review.validation_errors:
            print(f"- {error}")
 
    if review.assumptions:
        print()
        print("Assumptions:")
 
        for assumption in review.assumptions:
            print(f"- {assumption}")
 
 
def main() -> None:
 
    # --------------------------------------------------
    # Case 1: Complete forced-convection request
    # --------------------------------------------------
 
    complete_forced = {
        "component_type": "heat_sink",
        "convection_mode": "forced",
        "requirements": {
            "heat_load": 165,
            "ambient_temperature": 30,
            "air_velocity": 5,
        },
        "constraints": {
            "base_length": 50,
            "base_width": 50,
            "max_height": 25,
        },
    }
 
    # --------------------------------------------------
    # Case 2: Incomplete request requiring clarification
    # --------------------------------------------------
 
    incomplete_request = {
        "component_type": "heat_sink",
        "convection_mode": None,
        "requirements": {
            "heat_load": 200,
            "ambient_temperature": None,
            "air_velocity": None,
        },
        "constraints": {
            "base_length": None,
            "base_width": None,
            "max_height": None,
        },
    }
 
    # --------------------------------------------------
    # Case 3: Complete natural-convection request
    # --------------------------------------------------
 
    complete_natural = {
        "component_type": "heat_sink",
        "convection_mode": "natural",
        "requirements": {
            "heat_load": 80,
            "ambient_temperature": 35,
            "air_velocity": None,
        },
        "constraints": {
            "base_length": 100,
            "base_width": 80,
            "max_height": 50,
        },
    }
 
    # --------------------------------------------------
    # Case 4: Invalid supplied values
    # --------------------------------------------------
 
    invalid_request = {
        "component_type": "heat_sink",
        "convection_mode": "forced",
        "requirements": {
            "heat_load": -100,
            "ambient_temperature": 150,
            "air_velocity": -2,
        },
        "constraints": {
            "base_length": -50,
            "base_width": 0,
            "max_height": -20,
        },
    }
 
    print_review(
        "CASE 1 — COMPLETE FORCED CONVECTION",
        complete_forced,
    )
 
    print_review(
        "CASE 2 — INCOMPLETE REQUEST",
        incomplete_request,
    )
 
    print_review(
        "CASE 3 — COMPLETE NATURAL CONVECTION",
        complete_natural,
    )
 
    print_review(
        "CASE 4 — INVALID VALUES",
        invalid_request,
    )
 
 
if __name__ == "__main__":
    main()