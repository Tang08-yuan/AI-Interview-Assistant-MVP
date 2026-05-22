from __future__ import annotations

from langchain_openai import ChatOpenAI

from .config import get_settings


def get_llm() -> ChatOpenAI:
    settings = get_settings()

    try:
        return ChatOpenAI(
            model=settings.model,
            temperature=settings.temperature,
            api_key=settings.api_key,
            base_url=settings.base_url,
        )
    except TypeError:
        return ChatOpenAI(
            model=settings.model,
            temperature=settings.temperature,
            openai_api_key=settings.api_key,
            openai_api_base=settings.base_url,
        )
