"""Central configuration, loaded from environment / .env."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    chroma_dir: str = "chroma_db"
    collection_name: str = "farmer_advisor"
    raw_data_dir: str = "data/raw"
    processed_data_dir: str = "data/processed"

    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 6
    max_distance: float = 0.65

    def path(self, relative: str) -> Path:
        return BASE_DIR / relative


@lru_cache
def get_settings() -> Settings:
    return Settings()
