import logging

from core.llm import extract_requirements

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

prompt = """
Design a heat sink for 165 W.
Base 50 x 50 mm.
Maximum height 30 mm.
Forced convection.
Air velocity 5 m/s.
Ambient temperature 30 C.
"""

result = extract_requirements(prompt)

print("\nEngineering Requirements\n")
print(result)