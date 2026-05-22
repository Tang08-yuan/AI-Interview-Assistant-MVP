from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.3


def get_settings() -> Settings:
    api_key = os.getenv("ARK_API_KEY", "").strip()
    base_url = os.getenv("ARK_BASE_URL", "").strip()
    model = os.getenv("ARK_MODEL", "").strip()
    temperature_raw = os.getenv("ARK_TEMPERATURE", "0.3").strip()

    if not api_key or not base_url or not model:
        raise ValueError(
            "Missing ARK settings. Please set ARK_API_KEY, ARK_BASE_URL, ARK_MODEL in .env."
        )

    try:
        temperature = float(temperature_raw)
    except ValueError:
        temperature = 0.3

    return Settings(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
    )
