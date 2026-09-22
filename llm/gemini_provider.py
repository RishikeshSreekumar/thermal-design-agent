"""
gemini_provider.py
 
Gemini implementation of the common LLM provider interface.
 
The provider extracts structured thermal-design requirements.
Missing information is returned as null so that the clarification
workflow behaves consistently across personal and office laptops.
"""
 
import json
import logging
import time
 
from llm.base import LLMProvider
from llm.engineering_review_prompt import (
    build_engineering_review_prompt,
)
from llm.engineering_recommendation_prompt import (
    build_engineering_recommendation_prompt,
)
 
logger = logging.getLogger(__name__)
 
 
class GeminiProvider(LLMProvider):
    """
    Requirement-extraction provider using Google Gemini.
    """
 
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-2.5-flash",
    ) -> None:
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Add it to the local .env file."
            )
 
        try:
            from google import genai
 
        except ImportError as exc:
            raise ImportError(
                "The google-genai package is not installed. "
                "Run: python -m pip install google-genai"
            ) from exc
 
        self.client = genai.Client(
            api_key=api_key
        )
 
        self.model_name = model_name
 
    def extract_requirements(
        self,
        user_prompt: str,
    ) -> dict:
        """
        Convert a natural-language engineering request
        into a structured requirements dictionary.
        """
 
        prompt = f"""
You are an expert thermal engineer.
 
Your task is to extract engineering requirements from the
user's natural-language request.
 
Return ONLY valid JSON.
 
Use exactly this schema:
{{
  "component_type": "heat_sink",
  "convection_mode": null,
  "allowed_materials": [],
  "requirements": {{
    "heat_load": null,
    "ambient_temperature": null,
    "maximum_base_temperature": null,
    "maximum_pressure_drop": null,
    "maximum_pumping_power": null,
    "air_velocity": null
  }},
  "constraints": {{
    "base_length": null,
    "base_width": null,
    "max_height": null
  }},
  "natural_convection": {{
    "orientation": null,
    "include_radiation": false,
    "surface_emissivity": null,
    "surroundings_temperature": null
  }}
}}
Field definitions:
- component_type:
  The engineering component being designed.
  For the current application, use "heat_sink" when applicable.
- convection_mode:
  Use "natural" for natural or passive convection.
  Use "forced" when a fan, blower, imposed airflow,
  or air velocity is specified.
  Use null when the cooling mode cannot be determined.
- allowed_materials:
  List only materials that the user explicitly permits.
  Return an empty list when no material restriction is specified.
- heat_load:
  Heat to be dissipated, in watts.
- ambient_temperature:
  Ambient air temperature, in degrees Celsius.
- maximum_base_temperature:
  Maximum allowable heat-sink base temperature,
  in degrees Celsius.
  Use null when not specified.
- maximum_pressure_drop:
  Maximum allowable airflow pressure drop through the
  heat sink, in pascals.
  Use null when not specified.
- maximum_pumping_power:
  Maximum allowable airflow pumping power, in watts.
  Use null when not specified.
- air_velocity:
  Inlet or approach air velocity, in metres per second.
  Use null for natural convection or when not provided.
- base_length:
  Available heat-sink base length, in millimetres.
- base_width:
  Available heat-sink base width, in millimetres.
- max_height:
  Maximum permitted TOTAL heat-sink height,
  including the base and fins, in millimetres.
- natural_convection.orientation:
  Natural-convection heat-sink orientation.
  Use "vertical" when explicitly stated vertical.
  Use "horizontal_fins_up" when the heat sink is horizontal
  with fins facing upward.
  Use "horizontal_fins_down" when the heat sink is horizontal
  with fins facing downward.
  Use "horizontal" only when the user explicitly specifies
  horizontal orientation but does not state whether the fins
  face upward or downward.
  Use null when orientation is not specified.
 
- natural_convection.include_radiation:
  Set true only when the user explicitly requests thermal
  radiation or explicitly supplies a surface emissivity.
  Set false when radiation is not requested or is explicitly
  excluded.
 
- natural_convection.surface_emissivity:
  Surface emissivity used for thermal-radiation analysis.
  Use null when not explicitly supplied.
 
- natural_convection.surroundings_temperature:
  Radiative surroundings temperature in degrees Celsius.
  Use null when not explicitly supplied.
  Do not assume a value.
Rules:
1. Return only JSON.
2. Do not include markdown.
3. Do not include explanations.
4. Do not invent missing values.
5. Return null for optional numerical information that is not provided.
6. Return an empty list for allowed_materials when no material restriction is provided.
7. Do not infer maximum height from base dimensions.
8. Do not infer temperature, pressure-drop, pumping-power, or material limits.
9. If a positive air velocity, fan, or blower is specified,
   convection_mode should normally be "forced".
10. If the request explicitly states passive cooling,
    free convection, or natural convection,
    convection_mode should be "natural".
11. If the cooling mode is ambiguous, return null.
12. Preserve the units defined in the schema.
13. Use snake_case values for component_type.
14. Preserve every explicitly supplied engineering constraint
    represented by this schema.
15. Do not infer natural-convection orientation when it is
    not explicitly specified.
16. Do not invent surface emissivity.
17. If emissivity is explicitly supplied for a natural-
    convection design, set include_radiation to true.
18. If the user states only "horizontal" without saying
    fins upward or fins downward, return orientation
    "horizontal" so the application can clarify it.
19. Natural-convection configuration must not create an
    air-velocity requirement.
 
 
User request:
 
{user_prompt}
"""
 
        retries = 3
 
        for attempt in range(retries):
 
            try:
 
                logger.info(
                    "Calling Gemini (attempt %d/%d)...",
                    attempt + 1,
                    retries,
                )
 
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
 
                if not response.text:
                    raise ValueError(
                        "Gemini returned an empty response."
                    )
 
                text = response.text.strip()
 
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()
 
                result = json.loads(text)
 
                logger.info(
                    "Engineering requirements extracted successfully."
                )
 
                return result
 
            except Exception as exc:
 
                logger.warning(
                    "Gemini request failed: %s",
                    exc,
                )
 
                if attempt < retries - 1:
 
                    wait_seconds = 2 ** attempt
 
                    logger.info(
                        "Retrying in %d seconds...",
                        wait_seconds,
                    )
 
                    time.sleep(wait_seconds)
 
                else:
 
                    logger.error(
                        "Gemini failed after %d attempts.",
                        retries,
                    )
 
                    raise
    def synthesize_engineering_review(
        self,
        payload: dict,
    ) -> dict:
        """
        Generate grounded engineering-review synthesis
        using Google Gemini.
 
        The supplied payload contains authoritative
        deterministic engineering evidence. This provider
        performs communication and synthesis only.
        """
 
        prompt = build_engineering_review_prompt(
            payload
        )
 
        retries = 3
 
        for attempt in range(
            retries
        ):
            try:
                logger.info(
                    (
                        "Calling Gemini for "
                        "engineering-review synthesis "
                        "(attempt %d/%d)..."
                    ),
                    attempt + 1,
                    retries,
                )
 
                response = (
                    self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                    )
                )
 
                if not response.text:
                    raise ValueError(
                        "Gemini returned an empty "
                        "engineering-review response."
                    )
 
                text = (
                    response.text
                    .strip()
                )
 
                text = text.replace(
                    "```json",
                    "",
                )
 
                text = text.replace(
                    "```",
                    "",
                )
 
                text = text.strip()
 
                result = json.loads(
                    text
                )
 
                if not isinstance(
                    result,
                    dict,
                ):
                    raise ValueError(
                        "Gemini engineering-review "
                        "response must be a JSON object."
                    )
 
                logger.info(
                    "Gemini engineering-review "
                    "synthesis completed successfully."
                )
 
                return result
 
            except Exception as exc:
                logger.warning(
                    "Gemini engineering-review request "
                    "failed: %s",
                    exc,
                )
 
                if attempt < retries - 1:
                    wait_seconds = (
                        2 ** attempt
                    )
 
                    logger.info(
                        "Retrying in %d seconds...",
                        wait_seconds,
                    )
 
                    time.sleep(
                        wait_seconds
                    )
 
                else:
                    logger.error(
                        "Gemini engineering-review "
                        "synthesis failed after %d "
                        "attempts.",
                        retries,
                    )
 
                    raise

    def synthesize_engineering_recommendations(
        self,
        payload: dict,
    ) -> dict:
        """
        Generate grounded engineering recommendations
        using Google Gemini.
 
        The supplied payload contains authoritative
        deterministic engineering evidence. The provider
        performs recommendation reasoning only within the
        supplied grounding contract.
        """
 
        prompt = (
            build_engineering_recommendation_prompt(
                payload
            )
        )
 
        retries = 3
 
        for attempt in range(
            retries
        ):
            try:
                logger.info(
                    (
                        "Calling Gemini for "
                        "engineering-recommendation synthesis "
                        "(attempt %d/%d)..."
                    ),
                    attempt + 1,
                    retries,
                )
 
                response = (
                    self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                    )
                )
 
                if not response.text:
                    raise ValueError(
                        "Gemini returned an empty "
                        "engineering-recommendation response."
                    )
 
                text = (
                    response.text
                    .strip()
                )
 
                text = text.replace(
                    "```json",
                    "",
                )
 
                text = text.replace(
                    "```",
                    "",
                )
 
                text = text.strip()
 
                result = json.loads(
                    text
                )
 
                if not isinstance(
                    result,
                    dict,
                ):
                    raise ValueError(
                        "Gemini engineering-recommendation "
                        "response must be a JSON object."
                    )
 
                logger.info(
                    "Gemini engineering-recommendation "
                    "synthesis completed successfully."
                )
 
                return result
 
            except Exception as exc:
                logger.warning(
                    "Gemini engineering-recommendation "
                    "request failed: %s",
                    exc,
                )
 
                if attempt < retries - 1:
                    wait_seconds = (
                        2 ** attempt
                    )
 
                    logger.info(
                        "Retrying in %d seconds...",
                        wait_seconds,
                    )
 
                    time.sleep(
                        wait_seconds
                    )
 
                else:
                    logger.error(
                        "Gemini engineering-recommendation "
                        "synthesis failed after %d "
                        "attempts.",
                        retries,
                    )
 
                    raise