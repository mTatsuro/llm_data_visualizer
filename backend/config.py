import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Default model can be overridden via env var
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Dataset configuration: can be overridden via DATASET_PATH env var
DEFAULT_DATASET = Path(__file__).parent / "top_100_saas_companies_2025.csv"
DATASET_PATH = Path(os.getenv("DATASET_PATH", str(DEFAULT_DATASET))).resolve()
