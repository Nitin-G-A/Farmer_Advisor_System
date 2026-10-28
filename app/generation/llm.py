"""Gemini LLM wrapper."""
from functools import lru_cache

from google import genai

from app.config import get_settings


@lru_cache
def _client() -> genai.Client:
    key = get_settings().gemini_api_key
    if not key or key.startswith("your_"):
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to .env")
    return genai.Client(api_key=key)


def generate(prompt: str) -> str:
    resp = _client().models.generate_content(
        model=get_settings().gemini_model, contents=prompt
    )
    return (resp.text or "").strip()
