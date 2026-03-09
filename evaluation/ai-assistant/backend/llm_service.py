"""LLM Judge service using Azure OpenAI via LangExtract."""

from __future__ import annotations

import logging
from typing import Optional

from models import Entity

logger = logging.getLogger(__name__)

# Lazy-loaded recognizer singleton
_recognizer = None


class LLMServiceError(Exception):
    """Raised when LLM service encounters an error."""


def configure(
    azure_endpoint: str,
    api_key: Optional[str] = None,
    deployment_name: str = "gpt-4o",
    api_version: str = "2024-02-15-preview",
) -> dict:
    """Initialise the Azure OpenAI LangExtract recognizer.

    :param azure_endpoint: Azure OpenAI endpoint URL.
    :param api_key: API key (or None for managed identity).
    :param deployment_name: Azure deployment / model name.
    :param api_version: Azure OpenAI API version.
    :returns: Status dict.
    """
    global _recognizer

    try:
        from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import (  # noqa: E501
            AzureOpenAILangExtractRecognizer,
        )
    except ImportError as exc:
        raise LLMServiceError(
            "langextract or presidio-analyzer is not installed. "
            "Run: pip install langextract presidio-analyzer"
        ) from exc

    try:
        _recognizer = AzureOpenAILangExtractRecognizer(
            model_id=deployment_name,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version,
        )
    except Exception as exc:
        _recognizer = None
        raise LLMServiceError(f"Failed to initialise recognizer: {exc}") from exc

    logger.info(
        "LLM Judge configured: endpoint=%s deployment=%s",
        azure_endpoint,
        deployment_name,
    )
    return {"status": "configured", "deployment": deployment_name}


def is_configured() -> bool:
    """Return True if the recognizer has been initialised."""
    return _recognizer is not None


def disconnect() -> None:
    """Reset the recognizer so a new model can be configured."""
    global _recognizer
    _recognizer = None
    logger.info("LLM Judge disconnected")


def analyze_text(text: str) -> list[Entity]:
    """Run the LLM recognizer on a single text and return Entity objects."""
    if _recognizer is None:
        raise LLMServiceError(
            "LLM service not configured. Call /api/llm/configure first."
        )

    results = _recognizer.analyze(text=text, entities=None)

    entities: list[Entity] = []
    for r in results:
        entities.append(
            Entity(
                text=text[r.start:r.end],
                entity_type=r.entity_type,
                start=r.start,
                end=r.end,
                score=round(r.score, 4),
            )
        )
    return entities
