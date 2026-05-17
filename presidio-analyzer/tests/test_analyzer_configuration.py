import pytest
from presidio_analyzer.configuration import AnalyzerConfiguration


def test_from_yaml_wraps_invalid_yaml_as_value_error(tmp_path):
    """Test invalid YAML parser errors are exposed as ValueError."""
    config_file = tmp_path / "invalid.yaml"
    config_file.write_text("invalid: [unclosed", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML"):
        AnalyzerConfiguration.from_yaml(config_file)


def test_from_yaml_wraps_validation_errors_as_value_error(tmp_path):
    """Test invalid analyzer schemas are exposed as ValueError."""
    config_file = tmp_path / "invalid_analyzer.yaml"
    config_file.write_text("unknown_key: value\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid analyzer configuration"):
        AnalyzerConfiguration.from_yaml(config_file)
