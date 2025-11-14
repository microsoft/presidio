"""Pytest configuration for e2e tests."""
import os
import urllib.error
import urllib.request

import pytest


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-ollama",
        action="store_true",
        default=False,
        help="Run Ollama integration tests (requires Ollama server running)"
    )


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers",
        "ollama: mark test as requiring Ollama server"
    )


@pytest.fixture(scope="session")
def ollama_available():
    """Check if Ollama server is available."""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    try:
        url = f"{ollama_url}/api/tags"
        request = urllib.request.Request(url, method='GET')
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return False
