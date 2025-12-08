"""Tests for AnalyzerMode enum and mode utility functions."""

import tempfile
from pathlib import Path

import pytest
from presidio_analyzer import AnalyzerEngine, AnalyzerMode
from presidio_analyzer.analyzer_mode import (
    get_custom_config_path,
    get_slm_config,
    get_mode_config_dir,
    get_nlp_engine_config,
)
from presidio_analyzer.nlp_engine import SpacyNlpEngine


class TestAnalyzerModeEnum:
    """Tests for AnalyzerMode enum."""

    def test_mode_enum_values(self):
        """Test that all expected modes exist."""
        assert AnalyzerMode.FAST.value == "fast"
        assert AnalyzerMode.BALANCED.value == "balanced"
        assert AnalyzerMode.ACCURATE.value == "accurate"
        assert AnalyzerMode.CUSTOM.value == "custom"


class TestModeUtilityFunctions:
    """Tests for mode utility functions."""

    def test_get_mode_config_dir_fast(self):
        """Test that FAST mode returns correct config directory."""
        config_dir = get_mode_config_dir(AnalyzerMode.FAST)
        assert config_dir.exists()
        assert config_dir.name == "fast"

    def test_get_mode_config_dir_balanced(self):
        """Test that BALANCED mode returns correct config directory."""
        config_dir = get_mode_config_dir(AnalyzerMode.BALANCED)
        assert config_dir.exists()
        assert config_dir.name == "balanced"

    def test_get_mode_config_dir_accurate(self):
        """Test that ACCURATE mode returns correct config directory."""
        config_dir = get_mode_config_dir(AnalyzerMode.ACCURATE)
        assert config_dir.exists()
        assert config_dir.name == "accurate"

    def test_get_mode_config_dir_custom_raises_error(self):
        """Test that CUSTOM mode raises ValueError."""
        with pytest.raises(ValueError, match="CUSTOM mode requires"):
            get_mode_config_dir(AnalyzerMode.CUSTOM)

    def test_get_nlp_engine_config_fast(self):
        """Test getting NLP engine config for FAST mode."""
        config_path = get_nlp_engine_config(AnalyzerMode.FAST)
        assert config_path.exists()
        assert config_path.name == "spacy.yaml"

    def test_get_slm_config_fast_returns_none(self):
        """Test that FAST mode has no SLM config."""
        slm_config = get_slm_config(AnalyzerMode.FAST)
        assert slm_config is None

    def test_get_slm_config_accurate_returns_path(self):
        """Test that ACCURATE mode has SLM config."""
        slm_config = get_slm_config(AnalyzerMode.ACCURATE)
        assert slm_config is not None
        assert slm_config.exists()
        assert slm_config.name == "slm.yaml"

    def test_get_custom_config_path_valid(self):
        """Test get_custom_config_path with valid path."""
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            f.write(b"nlp_engine_name: spacy\n")
            temp_path = f.name

        result = get_custom_config_path(temp_path)
        assert result == Path(temp_path)

        Path(temp_path).unlink()

    def test_get_custom_config_path_invalid(self):
        """Test get_custom_config_path with invalid path raises error."""
        with pytest.raises(FileNotFoundError):
            get_custom_config_path("/nonexistent/path.yaml")


class TestAnalyzerEngineWithMode:
    """Tests for AnalyzerEngine with mode parameter."""

    def test_when_mode_fast_then_analyzer_engine_created(self):
        """Test that AnalyzerEngine can be created with FAST mode."""
        analyzer = AnalyzerEngine(mode=AnalyzerMode.FAST)
        assert analyzer is not None
        assert analyzer.nlp_engine is not None
        assert isinstance(analyzer.nlp_engine, SpacyNlpEngine)

    def test_when_mode_fast_then_can_analyze_text(self):
        """Test that FAST mode analyzer can detect PII."""
        analyzer = AnalyzerEngine(mode=AnalyzerMode.FAST)
        results = analyzer.analyze(
            text="My name is John Smith and my email is john@example.com",
            language="en",
        )
        entity_types = [r.entity_type for r in results]
        assert "EMAIL_ADDRESS" in entity_types

    def test_when_mode_with_nlp_engine_then_raises_error(self):
        """Test that mode cannot be used with nlp_engine parameter."""
        from presidio_analyzer.nlp_engine import NlpArtifacts

        from tests.mocks import NlpEngineMock

        mock_nlp_artifacts = NlpArtifacts([], [], [], [], None, "en")
        mock_engine = NlpEngineMock(
            stopwords=[], punct_words=[], nlp_artifacts=mock_nlp_artifacts
        )

        with pytest.raises(ValueError, match="Cannot specify 'mode' together with"):
            AnalyzerEngine(mode=AnalyzerMode.FAST, nlp_engine=mock_engine)

    def test_when_mode_with_registry_then_raises_error(self):
        """Test that mode cannot be used with registry parameter."""
        from presidio_analyzer import RecognizerRegistry

        registry = RecognizerRegistry()

        with pytest.raises(ValueError, match="Cannot specify 'mode' together with"):
            AnalyzerEngine(mode=AnalyzerMode.FAST, registry=registry)

    def test_when_config_path_without_custom_mode_then_raises_error(self):
        """Test that config_path requires CUSTOM mode."""
        with pytest.raises(
            ValueError, match="'config_path' can only be used with AnalyzerMode.CUSTOM"
        ):
            AnalyzerEngine(mode=AnalyzerMode.FAST, config_path="/some/path.yaml")

    def test_when_custom_mode_with_valid_config_then_analyzer_created(self):
        """Test that CUSTOM mode with valid config file works."""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", delete=False, mode="w"
        ) as f:
            f.write(
                """
nlp_engine_name: spacy
models:
  -
    lang_code: en
    model_name: en_core_web_sm
"""
            )
            temp_path = f.name

        try:
            analyzer = AnalyzerEngine(
                mode=AnalyzerMode.CUSTOM, config_path=temp_path
            )
            assert analyzer is not None
            assert analyzer.nlp_engine is not None
        finally:
            Path(temp_path).unlink()

    def test_when_no_mode_then_default_behavior(self):
        """Test that no mode parameter preserves default behavior."""
        analyzer = AnalyzerEngine()
        assert analyzer is not None
        assert analyzer.nlp_engine is not None
