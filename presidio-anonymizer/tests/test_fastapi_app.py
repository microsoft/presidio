"""Tests for the FastAPI anonymizer server."""

from importlib import util
from pathlib import Path

import pytest

pytest.importorskip("httpx")
fastapi_testclient = pytest.importorskip("fastapi.testclient")
TestClient = fastapi_testclient.TestClient


def _load_fastapi_app():
    module_path = Path(__file__).parents[1] / "fastapi_app.py"
    spec = util.spec_from_file_location("presidio_anonymizer_fastapi_app", module_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.create_app()


def test_health_endpoint_returns_service_status():
    """Health endpoint mirrors the existing service status response."""
    client = TestClient(_load_fastapi_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.text == "Presidio Anonymizer service is up"


def test_anonymize_endpoint_returns_engine_response():
    """Anonymize endpoint returns the anonymizer engine JSON response."""
    client = TestClient(_load_fastapi_app())

    response = client.post(
        "/anonymize",
        json={
            "text": "My name is Jane",
            "analyzer_results": [
                {
                    "start": 11,
                    "end": 15,
                    "score": 0.8,
                    "entity_type": "PERSON",
                }
            ],
            "anonymizers": {
                "DEFAULT": {"type": "replace", "new_value": "<ANONYMIZED>"}
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["text"] == "My name is <ANONYMIZED>"


def test_empty_json_body_returns_flask_compatible_error_shape():
    """Empty JSON requests keep the existing error response shape."""
    client = TestClient(_load_fastapi_app())

    response = client.post("/anonymize", json={})

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid request json"}


@pytest.mark.parametrize("request_kwargs", [{}, {"content": "not json"}])
def test_invalid_json_body_returns_flask_compatible_error_shape(request_kwargs):
    """Missing and invalid JSON requests keep the existing error response shape."""
    client = TestClient(_load_fastapi_app())

    response = client.post("/anonymize", **request_kwargs)

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid request json"}


def test_anonymizers_endpoint_returns_supported_operators():
    """Anonymizers endpoint exposes built-in anonymizer operators."""
    client = TestClient(_load_fastapi_app())

    response = client.get("/anonymizers")

    assert response.status_code == 200
    assert "replace" in response.json()


def test_deanonymize_endpoint_returns_engine_response():
    """Deanonymize endpoint returns the deanonymizer engine JSON response."""
    client = TestClient(_load_fastapi_app())

    response = client.post(
        "/deanonymize",
        json={
            "text": "My name is Jane",
            "anonymizer_results": [
                {
                    "start": 11,
                    "end": 15,
                    "entity_type": "PERSON",
                    "text": "Jane",
                    "operator": "keep",
                }
            ],
            "deanonymizers": {"DEFAULT": {"type": "deanonymize_keep"}},
        },
    )

    assert response.status_code == 200
    assert response.json()["text"] == "My name is Jane"


def test_deanonymizers_endpoint_returns_supported_operators():
    """Deanonymizers endpoint exposes built-in deanonymizer operators."""
    client = TestClient(_load_fastapi_app())

    response = client.get("/deanonymizers")

    assert response.status_code == 200
    assert "deanonymize_keep" in response.json()
