"""Tests for llm_utils.config_loader module."""
import pytest
import tempfile
from pathlib import Path
from presidio_analyzer.llm_utils.config_loader import (
    load_yaml_file,
    get_model_config,
)
from presidio_analyzer.llm_utils.langextract_helper import extract_lm_config


class TestLoadYamlFile:
    """Tests for load_yaml_file function."""

    def test_when_config_file_exists_then_loads_yaml(self):
        """Test loading a valid YAML configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
lm_recognizer:
  supported_entities: ["PERSON", "EMAIL"]
  min_score: 0.7
  labels_to_ignore: ["metadata"]
""")
            config_path = f.name

        try:
            config = load_yaml_file(config_path)
            assert config is not None
            assert "lm_recognizer" in config
            assert config["lm_recognizer"]["supported_entities"] == ["PERSON", "EMAIL"]
            assert config["lm_recognizer"]["min_score"] == 0.7
        finally:
            Path(config_path).unlink()

    def test_when_config_file_missing_then_raises_file_not_found_error(self):
        """Test that missing config file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_yaml_file("/nonexistent/path/config.yaml")

    def test_when_config_has_invalid_yaml_then_raises_value_error(self):
        """Test that invalid YAML raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:\n  - [unclosed")
            config_path = f.name

        try:
            with pytest.raises(ValueError, match="Failed to parse YAML"):
                load_yaml_file(config_path)
        finally:
            Path(config_path).unlink()

    def test_when_config_is_empty_then_returns_none(self):
        """Test loading an empty YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            config_path = f.name

        try:
            config = load_yaml_file(config_path)
            # yaml.safe_load returns None for empty file
            assert config is None
        finally:
            Path(config_path).unlink()

    def test_when_config_has_multiple_sections_then_loads_all(self):
        """Test loading config with multiple sections."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
lm_recognizer:
  supported_entities: ["PERSON"]
  
langextract:
  model:
    model_id: "qwen2.5:1.5b"
    
other_section:
  some_key: "some_value"
""")
            config_path = f.name

        try:
            config = load_yaml_file(config_path)
            assert "lm_recognizer" in config
            assert "langextract" in config
            assert "other_section" in config
        finally:
            Path(config_path).unlink()


class TestExtractLmConfig:
    """Tests for extract_lm_config function."""

    def test_when_lm_recognizer_section_exists_then_extracts_with_defaults(self):
        """Test extracting lm_recognizer config applies defaults for missing fields."""
        full_config = {
            "lm_recognizer": {
                "supported_entities": ["PERSON", "EMAIL"]
            }
        }

        lm_config = extract_lm_config(full_config)

        # Should have the provided entities
        assert lm_config["supported_entities"] == ["PERSON", "EMAIL"]
        # Should apply defaults for missing fields
        assert lm_config["min_score"] == 0.5
        assert lm_config["labels_to_ignore"] == []
        assert lm_config["enable_generic_consolidation"] is True

    def test_when_all_fields_present_then_uses_provided_values(self):
        """Test that provided values override defaults."""
        full_config = {
            "lm_recognizer": {
                "supported_entities": ["PERSON"],
                "min_score": 0.8,
                "labels_to_ignore": ["system", "metadata"],
                "enable_generic_consolidation": False
            }
        }

        lm_config = extract_lm_config(full_config)

        assert lm_config["supported_entities"] == ["PERSON"]
        assert lm_config["min_score"] == 0.8
        assert lm_config["labels_to_ignore"] == ["system", "metadata"]
        assert lm_config["enable_generic_consolidation"] is False

    def test_when_lm_recognizer_missing_then_returns_none_for_entities(self):
        """Test that missing lm_recognizer section returns None for supported_entities."""
        full_config = {"other_section": {}}

        lm_config = extract_lm_config(full_config)

        # Should return None for supported_entities when lm_recognizer missing
        assert lm_config["supported_entities"] is None
        assert lm_config["min_score"] == 0.5
        assert lm_config["labels_to_ignore"] == []
        assert lm_config["enable_generic_consolidation"] is True

    def test_when_partial_config_then_merges_with_defaults(self):
        """Test partial config merges with defaults."""
        full_config = {
            "lm_recognizer": {
                "supported_entities": ["PHONE"],
                "min_score": 0.6
                # labels_to_ignore and enable_generic_consolidation missing
            }
        }

        lm_config = extract_lm_config(full_config)

        assert lm_config["supported_entities"] == ["PHONE"]
        assert lm_config["min_score"] == 0.6
        assert lm_config["labels_to_ignore"] == []  # Default
        assert lm_config["enable_generic_consolidation"] is True  # Default


class TestGetModelConfig:
    """Tests for get_model_config function."""

    def test_when_provider_key_exists_then_extracts_model_config(self):
        """Test extracting model config for a specific provider."""
        config = {
            "langextract": {
                "model": {
                    "model_id": "qwen2.5:1.5b",
                    "temperature": 0.0,
                    "model_url": "http://localhost:11434"
                }
            }
        }

        model_config = get_model_config(config, "langextract")

        assert model_config is not None
        assert "model_id" in model_config
        assert model_config["model_id"] == "qwen2.5:1.5b"
        assert model_config["temperature"] == 0.0

    def test_when_provider_key_missing_then_raises_value_error(self):
        """Test that missing provider key raises ValueError."""
        config = {
            "other_provider": {
                "model": {"model_id": "some-model"}
            }
        }

        with pytest.raises(ValueError, match="Configuration must contain 'langextract'"):
            get_model_config(config, "langextract")

    def test_when_model_section_missing_then_raises_value_error(self):
        """Test that missing model section raises ValueError."""
        config = {
            "langextract": {
                "other_section": {}
            }
        }

        with pytest.raises(ValueError, match="Configuration must contain 'langextract.model'"):
            get_model_config(config, "langextract")

    def test_when_model_id_missing_then_raises_value_error(self):
        """Test that missing model_id raises ValueError."""
        config = {
            "langextract": {
                "model": {
                    "temperature": 0.0
                }
            }
        }

        with pytest.raises(ValueError, match="Configuration must contain 'langextract.model.model_id'"):
            get_model_config(config, "langextract")

    def test_when_model_config_has_extra_params_then_includes_all(self):
        """Test that extra model parameters are included."""
        config = {
            "langextract": {
                "model": {
                    "model_id": "qwen2.5:1.5b",
                    "temperature": 0.1,
                    "model_url": "http://localhost:11434",
                    "custom_param": "custom_value"
                }
            }
        }

        model_config = get_model_config(config, "langextract")

        assert model_config["model_id"] == "qwen2.5:1.5b"
        assert model_config["temperature"] == 0.1
        assert model_config["model_url"] == "http://localhost:11434"
        assert model_config["custom_param"] == "custom_value"


class TestIntegration:
    """Integration tests for config_loader functions."""

    def test_when_loading_full_config_workflow_then_extracts_correctly(self):
        """Test complete workflow: load YAML → extract lm config → get model config."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
lm_recognizer:
  supported_entities: ["PERSON", "EMAIL", "PHONE"]
  min_score: 0.75
  labels_to_ignore: ["system"]
  enable_generic_consolidation: false
  
langextract:
  model:
    model_id: "qwen2.5:1.5b"
    temperature: 0.0
    model_url: "http://localhost:11434"
""")
            config_path = f.name

        try:
            # Step 1: Load YAML
            full_config = load_yaml_file(config_path)
            
            # Step 2: Extract lm_recognizer config
            lm_config = extract_lm_config(full_config)
            assert lm_config["supported_entities"] == ["PERSON", "EMAIL", "PHONE"]
            assert lm_config["min_score"] == 0.75
            assert lm_config["labels_to_ignore"] == ["system"]
            assert lm_config["enable_generic_consolidation"] is False
            
            # Step 3: Get model config
            model_config = get_model_config(full_config, "langextract")
            assert model_config["model_id"] == "qwen2.5:1.5b"
            assert model_config["temperature"] == 0.0
            
        finally:
            Path(config_path).unlink()
