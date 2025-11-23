"""Pytest configuration for e2e tests."""
import pytest


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers",
        "ollama: mark test as requiring Ollama server"
    )
