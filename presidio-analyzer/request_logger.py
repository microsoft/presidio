"""Structured request/response logger for Presidio Flask services."""

import json
import logging
import os
import time
from typing import Optional

from flask import Flask, g, request

logger = logging.getLogger("presidio.request")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

# Set LOG_REQUEST_TEXT=true to include the raw input text in log records.
# Disabled by default: logging un-redacted text defeats the purpose of PII
# de-identification and creates a new data-liability record.
_LOG_TEXT = os.environ.get("LOG_REQUEST_TEXT", "false").lower() == "true"


def _client_ip() -> str:
    """Return the originating client IP, honouring X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def register_request_logger(app: Flask, service_name: str) -> None:
    """Attach before/after request hooks that emit structured JSON log lines.

    :param app: Flask application instance.
    :param service_name: Label embedded in every log record (e.g. 'analyzer').
    """

    @app.before_request
    def _before() -> None:
        g._req_start = time.monotonic()
        g._req_body = None
        try:
            g._req_body = request.get_json(silent=True) or {}
        except Exception:
            g._req_body = {}

    @app.after_request
    def _after(response):
        elapsed_ms = round((time.monotonic() - g._req_start) * 1000, 2)
        body: dict = g._req_body or {}

        record: dict = {
            "service": service_name,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "client_ip": _client_ip(),
            "response_time_ms": elapsed_ms,
            "correlation_id": body.get("correlation_id"),
            "language": body.get("language"),
            "entities_requested": body.get("entities"),
            "score_threshold": body.get("score_threshold"),
        }

        if _LOG_TEXT:
            record["text"] = body.get("text")

        _log_response_entities(record, response)

        logger.info(json.dumps(record, ensure_ascii=False, default=str))
        return response


def _log_response_entities(record: dict, response) -> None:
    """Add a lightweight entity summary from the response body without re-serializing."""
    if response.content_type != "application/json":
        return
    try:
        data = response.get_json(silent=True, force=True)
        if isinstance(data, list):
            # Flat list from /analyze — could be list[dict] or list[list[dict]]
            if data and isinstance(data[0], dict):
                record["detected_entity_count"] = len(data)
                record["detected_entity_types"] = list(
                    {item.get("entity_type") for item in data if "entity_type" in item}
                )
            elif data and isinstance(data[0], list):
                # Batch mode
                record["detected_entity_count"] = sum(len(r) for r in data)
    except Exception:
        pass
