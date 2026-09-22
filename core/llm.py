"""
llm.py
 
LLM interface for the Thermal AI Engineer.
 
This module provides a stable interface between the application
and the configured LLM provider.
 
The actual provider is selected through the LLM factory.
"""
 
import logging
 
from llm.factory import get_llm_provider
 
 
logger = logging.getLogger(__name__)
 
 
# -----------------------------------------------------
# Create Configured Provider
# -----------------------------------------------------
 
provider = get_llm_provider()
 
 
# -----------------------------------------------------
# Provider Information
# -----------------------------------------------------
 
def get_provider_name() -> str:
    """
    Return the name of the currently active LLM provider.
    """
 
    return provider.__class__.__name__
 
 
# -----------------------------------------------------
# Requirement Extraction
# -----------------------------------------------------
 
def extract_requirements(user_prompt: str) -> dict:
    """
    Extract structured engineering requirements from
    a natural-language user request.
 
    The configured LLM provider is selected automatically
    through the provider factory.
    """
 
    logger.info(
        "Extracting requirements using provider: %s",
        get_provider_name(),
    )
 
    return provider.extract_requirements(user_prompt)
 