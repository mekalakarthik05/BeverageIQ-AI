import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = BASE_DIR / "data" / "database.db"

# Model Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_API_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Dataset Generation Settings
NUM_PRODUCTS = 20
NUM_STORES = 30
WEEKS_OF_SALES = 52

# Styling
APP_TITLE = "BeverageIQ - FMCG Analytics"
APP_ICON = "📈"
