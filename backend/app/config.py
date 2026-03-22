import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ROOT_ENV_PATH)


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    firecrawl_api_key: str = os.getenv("FIRECRAWL_API_KEY", "")
    firecrawl_base_url: str = os.getenv("FIRECRAWL_BASE_URL", "https://api.firecrawl.dev")
    firecrawl_timeout_seconds: float = float(os.getenv("FIRECRAWL_TIMEOUT_SECONDS", "45"))


settings = Settings()
