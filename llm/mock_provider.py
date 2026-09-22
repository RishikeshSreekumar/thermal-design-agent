"""
mock_provider.py
 
Offline mock implementation of the LLM provider interface.
 
Useful for:
- Local development
- Unit testing
- Working without network access
- Avoiding unnecessary API calls
 
The mock provider returns the same requirements schema used
by the Azure OpenAI and Gemini providers.
"""
 
import re
 
from llm.base import LLMProvider
 
 
class MockProvider(LLMProvider):
    """
    Offline requirement extractor for development and testing.
    """
 
    def extract_requirements(
        self,
        user_prompt: str,
    ) -> dict:
        """
        Extract common thermal-design requirements using
        deterministic pattern matching.
 
        Missing information is returned as None.
        """
 
        prompt = user_prompt.lower()
 
        # --------------------------------------------------
        # Heat Load
        # --------------------------------------------------
 
        heat_load = self._extract_first_number(
            prompt,
            patterns=[
                r"(\d+(?:\.\d+)?)\s*w",
                r"heat load\s*(?:of|=|:)?\s*(\d+(?:\.\d+)?)",
            ],
        )
 
        # --------------------------------------------------
        # Ambient Temperature
        # --------------------------------------------------
 
        ambient_temperature = self._extract_first_number(
            prompt,
            patterns=[
                (
                    r"ambient(?: temperature)?\s*"
                    r"(?:of|=|:)?\s*(\d+(?:\.\d+)?)"
                ),
                r"(\d+(?:\.\d+)?)\s*°?\s*c",
            ],
        )

        # --------------------------------------------------
        # Maximum Base Temperature
        # --------------------------------------------------
        maximum_base_temperature = (
            self._extract_first_number(
                prompt,
                patterns=[
                    (
                        r"maximum base temperature\s*"
                        r"(?:of|=|:|below|under|<=|≤)?\s*"
                        r"(\d+(?:\.\d+)?)"
                    ),
                    (
                        r"base temperature\s*"
                        r"(?:limit(?:ed)? to|must not exceed|"
                        r"below|under|<=|≤)\s*"
                        r"(\d+(?:\.\d+)?)"
                    ),
                ],
            )
        )
        # --------------------------------------------------
        # Maximum Pressure Drop
        # --------------------------------------------------
        maximum_pressure_drop = (
            self._extract_first_number(
                prompt,
                patterns=[
                    (
                        r"maximum pressure drop\s*"
                        r"(?:of|=|:|below|under|<=|≤)?\s*"
                        r"(\d+(?:\.\d+)?)"
                    ),
                    (
                        r"pressure drop\s*"
                        r"(?:limit(?:ed)? to|must not exceed|"
                        r"below|under|<=|≤)\s*"
                        r"(\d+(?:\.\d+)?)"
                    ),
                ],
            )
        )
        # --------------------------------------------------
        # Maximum Pumping Power
        # --------------------------------------------------
        maximum_pumping_power = (
            self._extract_first_number(
                prompt,
                patterns=[
                    (
                        r"maximum pumping power\s*"
                        r"(?:of|=|:|below|under|<=|≤)?\s*"
                        r"(\d+(?:\.\d+)?)"
                    ),
                    (
                        r"pumping power\s*"
                        r"(?:limit(?:ed)? to|must not exceed|"
                        r"below|under|<=|≤)\s*"
                        r"(\d+(?:\.\d+)?)"
                    ),
                ],
            )
        )
 
        # --------------------------------------------------
        # Air Velocity
        # --------------------------------------------------
 
        air_velocity = self._extract_first_number(
            prompt,
            patterns=[
                (
                    r"air velocity\s*(?:of|=|:)?\s*"
                    r"(\d+(?:\.\d+)?)"
                ),
                (
                    r"airflow\s*(?:of|=|:|around)?\s*"
                    r"(\d+(?:\.\d+)?)\s*m/s"
                ),
                r"(\d+(?:\.\d+)?)\s*m/s",
            ],
        )
 
        # --------------------------------------------------
        # Base Dimensions
        # --------------------------------------------------
 
        base_length = None
        base_width = None
 
        base_match = re.search(
            r"(\d+(?:\.\d+)?)\s*(?:mm)?\s*[x×]\s*"
            r"(\d+(?:\.\d+)?)\s*mm",
            prompt,
        )
 
        if base_match:
            base_length = float(
                base_match.group(1)
            )
 
            base_width = float(
                base_match.group(2)
            )
 
        # --------------------------------------------------
        # Maximum Total Height
        # --------------------------------------------------
 
        max_height = self._extract_first_number(
            prompt,
            patterns=[
                (
                    r"maximum total height\s*"
                    r"(?:of|=|:)?\s*(\d+(?:\.\d+)?)"
                ),
                (
                    r"maximum height\s*"
                    r"(?:of|=|:)?\s*(\d+(?:\.\d+)?)"
                ),
                (
                    r"max height\s*"
                    r"(?:of|=|:)?\s*(\d+(?:\.\d+)?)"
                ),
            ],
        )
 
        # --------------------------------------------------
        # Convection Mode
        # --------------------------------------------------
 
        convection_mode = self._detect_convection_mode(
            prompt=prompt,
            air_velocity=air_velocity,
        )

        # --------------------------------------------------
        # Natural-Convection Configuration
        # --------------------------------------------------
 
        natural_orientation = None
        include_radiation = False
        surface_emissivity = None
        surroundings_temperature = None
 
        if convection_mode == "natural":
 
            natural_orientation = (
                self._detect_natural_convection_orientation(
                    prompt
                )
            )
 
            surface_emissivity = (
                self._extract_first_number(
                    prompt,
                    patterns=[
                        (
                            r"(?:surface\s+)?emissivity\s*"
                            r"(?:of|=|:|is)?\s*"
                            r"(\d+(?:\.\d+)?)"
                        ),
                    ],
                )
            )
 
            surroundings_temperature = (
                self._extract_first_number(
                    prompt,
                    patterns=[
                        (
                            r"(?:radiative\s+)?"
                            r"surroundings temperature\s*"
                            r"(?:of|=|:|is)?\s*"
                            r"(\d+(?:\.\d+)?)"
                        ),
                    ],
                )
            )
 
            radiation_disabled = any(
                term in prompt
                for term in (
                    "without radiation",
                    "exclude radiation",
                    "excluding radiation",
                    "ignore radiation",
                    "radiation excluded",
                )
            )
 
            radiation_requested = any(
                term in prompt
                for term in (
                    "include radiation",
                    "including radiation",
                    "with radiation",
                    "radiation included",
                    "thermal radiation",
                )
            )
 
            if radiation_disabled:
                include_radiation = False
 
            elif (
                radiation_requested
                or surface_emissivity is not None
            ):
                include_radiation = True

        # --------------------------------------------------
        # Allowed Materials
        # --------------------------------------------------
        allowed_materials: list[str] = []
        material_match = re.search(
            (
                r"allowed materials?\s*"
                r"(?:are|=|:)?\s*"
                r"([a-z0-9][a-z0-9 .,\-]*?)"
                r"(?:[.;]|$)"
            ),
            prompt,
        )
        if material_match:
            allowed_materials = [
                material.strip()
                for material in re.split(
                    r"\s*(?:,|\bor\b|\band\b)\s*",
                    material_match.group(1),
                )
                if material.strip()
            ]
 
        # --------------------------------------------------
        # Structured Output
        # --------------------------------------------------
 
        return {
            "component_type": "heat_sink",
            "convection_mode": convection_mode,
            "allowed_materials": allowed_materials,
            "requirements": {
                "heat_load": heat_load,
                "ambient_temperature": (
                    ambient_temperature
                ),
                "maximum_base_temperature": (
                    maximum_base_temperature
                ),
                "maximum_pressure_drop": (
                    maximum_pressure_drop
                ),
                "maximum_pumping_power": (
                    maximum_pumping_power
                ),
                "air_velocity": air_velocity,
            },
            "constraints": {
                "base_length": base_length,
                "base_width": base_width,
                "max_height": max_height,
            },
            "natural_convection": {
                "orientation": natural_orientation,
                "include_radiation": include_radiation,
                "surface_emissivity": surface_emissivity,
                "surroundings_temperature": (
                    surroundings_temperature
                ),
            },
        }
    
    def synthesize_engineering_review(
        self,
        payload: dict,
    ) -> dict:
        """
        Return deterministic offline review synthesis for
        testing the grounded AI-review workflow.
 
        The mock performs no engineering evaluation.
        """
 
        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "'payload' must be a dictionary."
            )
 
        review_data = payload.get(
            "deterministic_review"
        )
 
        if not isinstance(
            review_data,
            dict,
        ):
            raise ValueError(
                "Review payload is missing "
                "'deterministic_review'."
            )
 
        deterministic_summary = (
            review_data.get(
                "executive_summary"
            )
        )
 
        if not isinstance(
            deterministic_summary,
            str,
        ):
            raise ValueError(
                "Deterministic review summary is missing."
            )
 
        sections = review_data.get(
            "sections",
            [],
        )
 
        section_summaries = []
 
        for section in sections:
            section_summaries.append(
                {
                    "category": (
                        section["category"]
                    ),
                    "summary": (
                        "AI synthesis: "
                        f"{section['summary']}"
                    ),
                }
            )
 
        return {
            "executive_summary": (
                "AI synthesis: "
                f"{deterministic_summary}"
            ),
            "section_summaries": (
                section_summaries
            ),
            "tradeoffs": [],
        }
 
    @staticmethod
    def _extract_first_number(
        text: str,
        patterns: list[str],
    ) -> float | None:
        """
        Return the first number matching any supplied
        regular expression.
 
        Return None when no match is found.
        """
 
        for pattern in patterns:
 
            match = re.search(
                pattern,
                text,
            )
 
            if match:
                return float(
                    match.group(1)
                )
 
        return None

    @staticmethod
    def _detect_natural_convection_orientation(
        prompt: str,
    ) -> str | None:
        """
        Extract explicitly stated natural-convection
        orientation without inventing missing fin-facing
        direction.
        """
 
        upward_terms = (
            "horizontal fins up",
            "horizontal fins upward",
            "fins facing upward",
            "fins face upward",
            "upward-facing fins",
            "upward facing fins",
        )
 
        downward_terms = (
            "horizontal fins down",
            "horizontal fins downward",
            "fins facing downward",
            "fins face downward",
            "downward-facing fins",
            "downward facing fins",
        )
 
        vertical_terms = (
            "vertical orientation",
            "vertically oriented",
            "vertical heat sink",
            "vertical heatsink",
            "vertical fins",
        )
 
        if any(
            term in prompt
            for term in upward_terms
        ):
            return "horizontal_fins_up"
 
        if any(
            term in prompt
            for term in downward_terms
        ):
            return "horizontal_fins_down"
 
        if any(
            term in prompt
            for term in vertical_terms
        ):
            return "vertical"
 
        if "horizontal" in prompt:
            return "horizontal"
 
        return None
 
    @staticmethod
    def _detect_convection_mode(
        prompt: str,
        air_velocity: float | None,
    ) -> str | None:
        """
        Determine whether the prompt explicitly indicates
        natural or forced convection.
 
        Return None when the cooling mode is ambiguous.
        """
 
        natural_terms = [
            "natural convection",
            "natural-convection",
            "passive cooling",
            "passive-cooling",
            "passively cooled",
            "passively-cooled",
            "free convection",
            "free-convection",
        ]
 
        forced_terms = [
            "forced convection",
            "forced-convection",
            "fan cooled",
            "fan-cooled",
            "blower",
        ]
 
        if any(
            term in prompt
            for term in natural_terms
        ):
            return "natural"
 
        if any(
            term in prompt
            for term in forced_terms
        ):
            return "forced"
 
        if (
            air_velocity is not None
            and air_velocity > 0
        ):
            return "forced"
 
        return None

    def synthesize_engineering_recommendations(
        self,
        payload: dict,
    ) -> dict:
        """
        Return deterministic mock recommendation synthesis.
        """
 
        return {
            "recommendations": []
        }