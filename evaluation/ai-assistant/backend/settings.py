"""Centralised settings loaded from .env with PRESIDIO_EVAL_ prefix."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

_ENV_FILE = Path(__file__).resolve().parent / ".env"

# ── Available model choices shown in the UI dropdown ──
MODEL_CHOICES: list[dict[str, str]] = [
    {"id": "gpt-5.1", "label": "GPT-5.1", "provider": "Azure OpenAI"},
    {
        "id": "gpt-5.2-chat",
        "label": "GPT-5.2 Chat",
        "provider": "Azure OpenAI",
    },
    {"id": "gpt-5.4", "label": "GPT-5.4", "provider": "Azure OpenAI"},
]


class EvalSettings(BaseModel):
    """Runtime settings, sourced from env vars or interactive input."""

    azure_endpoint: str = ""
    azure_api_key: Optional[str] = None
    deployment_name: str = "gpt-5.4"
    api_version: str = "2024-02-15-preview"


def _load_dotenv() -> None:
    """Read .env into os.environ (simple key=value parser, no dependency)."""
    if not _ENV_FILE.is_file():
        return
    with open(_ENV_FILE) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Only set if not already in os.environ (explicit env wins)
            if key not in os.environ:
                os.environ[key] = value


def load_from_env() -> EvalSettings:
    """Build settings from PRESIDIO_EVAL_* environment variables."""
    _load_dotenv()
    api_key = os.environ.get("PRESIDIO_EVAL_AZURE_API_KEY") or None
    return EvalSettings(
        azure_endpoint=os.environ.get("PRESIDIO_EVAL_AZURE_ENDPOINT", ""),
        azure_api_key=api_key,
        deployment_name=os.environ.get(
            "PRESIDIO_EVAL_DEPLOYMENT_NAME", "gpt-4o"
        ),
        api_version=os.environ.get(
            "PRESIDIO_EVAL_API_VERSION", "2024-02-15-preview"
        ),
    )
