"""
factory.py
 
Factory for selecting the configured LLM provider.
 
The rest of the Thermal AI Engineer application does not need
to know whether Azure OpenAI, Gemini, or the offline mock
provider is being used.
"""
 
import os
 
from dotenv import load_dotenv
 
from llm.base import LLMProvider
 
 
# -----------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------
 
load_dotenv()
 
 
# -----------------------------------------------------
# Provider Factory
# -----------------------------------------------------
 
def get_llm_provider() -> LLMProvider:
    """
    Create and return the configured LLM provider.
 
    Supported providers:
    - azure
    - gemini
    - mock
    """
 
    provider_name = os.getenv(
        "LLM_PROVIDER",
        "mock",
    ).strip().lower()
 
    # -------------------------------------------------
    # Azure OpenAI
    # -------------------------------------------------
 
    if provider_name == "azure":
 
        from llm.azure_provider import AzureOpenAIProvider
 
        return AzureOpenAIProvider()
 
    # -------------------------------------------------
    # Gemini
    # -------------------------------------------------
 
    if provider_name == "gemini":
 
        from llm.gemini_provider import GeminiProvider
 
        api_key = os.getenv("GEMINI_API_KEY")
 
        model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )
 
        return GeminiProvider(
            api_key=api_key,
            model_name=model_name,
        )
 
    # -------------------------------------------------
    # Offline Mock
    # -------------------------------------------------
 
    if provider_name == "mock":
 
        from llm.mock_provider import MockProvider
 
        return MockProvider()
 
    # -------------------------------------------------
    # Unsupported Provider
    # -------------------------------------------------
 
    raise ValueError(
        f"Unsupported LLM_PROVIDER: '{provider_name}'. "
        "Choose 'azure', 'gemini', or 'mock'."
    )