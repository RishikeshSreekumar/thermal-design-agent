"""
test_provider_review.py
 
Verifies that the configured provider output can pass through:
 
Provider
    ↓
Parser
    ↓
Requirements Review
"""
 
from llm.factory import get_llm_provider
from core.parser import parse_requirements
from core.validator import review_requirements
 
 
def print_review(prompt: str) -> None:
    provider = get_llm_provider()
 
    print()
    print("=" * 70)
    print("PROMPT")
    print("=" * 70)
    print(prompt)
 
    print()
    print("Provider:")
    print(provider.__class__.__name__)
 
    raw_requirements = provider.extract_requirements(prompt)
 
    print()
    print("Raw provider output:")
    print(raw_requirements)
 
    engineering = parse_requirements(raw_requirements)
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
 
    if review.assumptions:
        print()
        print("Assumptions:")
 
        for assumption in review.assumptions:
            print(f"- {assumption}")
 
    if review.validation_errors:
        print()
        print("Validation errors:")
 
        for error in review.validation_errors:
            print(f"- {error}")
 
 
def main() -> None:
    complete_forced_prompt = (
        "Design a 165 W heat sink for forced convection. "
        "The base is 50 mm x 50 mm, the air velocity is "
        "5 m/s, and the maximum total height is 25 mm."
    )
 
    incomplete_prompt = (
        "Design a compact heat sink for 200 W."
    )
 
    natural_prompt = (
        "Design a passive natural-convection heat sink "
        "for 80 W. The base is 100 mm x 80 mm, ambient "
        "temperature is 35 C, and maximum total height "
        "is 50 mm."
    )
 
    print_review(complete_forced_prompt)
    print_review(incomplete_prompt)
    print_review(natural_prompt)
 
 
if __name__ == "__main__":
    main()