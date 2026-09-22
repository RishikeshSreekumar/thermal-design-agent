"""
config.py

Central configuration for the Thermal AI Engineer project.

Responsibilities:
- Load environment variables
- Define project paths
- Store application-wide constants
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# -----------------------------------------------------
# Runtime Mode
# -----------------------------------------------------

# True when running from the PyInstaller-built executable.
IS_FROZEN = getattr(sys, "frozen", False)

# -----------------------------------------------------
# Project Directories
# -----------------------------------------------------

if IS_FROZEN:
    # Read-only bundled files (app.py, assets, .streamlit)
    PROJECT_ROOT = Path(sys._MEIPASS)

    # Folder containing ThermalDesignAgent.exe
    APP_DIR = Path(sys.executable).parent

    # Writable per-user folder for generated outputs
    USER_DATA_DIR = (
        Path(os.environ.get("LOCALAPPDATA", Path.home()))
        / "ThermalDesignAgent"
    )
else:
    PROJECT_ROOT = Path(__file__).parent
    APP_DIR = PROJECT_ROOT
    USER_DATA_DIR = PROJECT_ROOT

ASSETS_DIR = PROJECT_ROOT / "assets"
LOGO_FILE = ASSETS_DIR / "havells_logo.png"

GENERATED_DIR = USER_DATA_DIR / "generated"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DOCS_DIR = PROJECT_ROOT / "docs"

GENERATED_DIR.mkdir(parents=True, exist_ok=True)

if not IS_FROZEN:
    PROMPTS_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)

# -----------------------------------------------------
# Load environment variables
# -----------------------------------------------------

# Executable: .env next to the .exe, then in the user folder.
# Source checkout: .env in the project root.
# Existing environment variables are never overridden.

load_dotenv(APP_DIR / ".env")
load_dotenv(USER_DATA_DIR / ".env")

# -----------------------------------------------------
# Azure OpenAI Configuration
# -----------------------------------------------------

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2025-03-01-preview",
)

AZURE_OPENAI_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT"
)

# -----------------------------------------------------
# Output Files
# -----------------------------------------------------

CAD_CODE_FILE = GENERATED_DIR / "cad_code.py"

STEP_FILE = GENERATED_DIR / "heatsink.step"

GEOMETRY_JSON = GENERATED_DIR / "geometry.json"

THERMAL_RESULTS_JSON = GENERATED_DIR / "thermal_results.json"

# -----------------------------------------------------
# Application Info
# -----------------------------------------------------

APP_NAME = "Thermal Design Agent"
 
VERSION = "2.0.0"