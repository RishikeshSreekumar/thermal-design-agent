"""
test_llm_factory.py
 
Verifies that the configured LLM provider is selected correctly
and can extract engineering requirements.
"""
 
from llm.factory import get_llm_provider
 
 
def main() -> None:
    provider = get_llm_provider()
 
    print("Selected provider:", provider.__class__.__name__)
 
    result = provider.extract_requirements(
        "Design a 165 W heat sink for a 50 mm x 50 mm base "
        "with 5 m/s airflow and a maximum total height of 25 mm."
    )
 
    print("\nExtracted requirements:")
    print(result)
 
 
if __name__ == "__main__":
    main()