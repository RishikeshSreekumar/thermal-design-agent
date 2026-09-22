from core.llm import extract_requirements

requirements = extract_requirements(
    "Design a 165 W heat sink with a 50 mm x 50 mm base and 5 m/s airflow."
)

print(requirements)