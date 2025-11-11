from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from presidio_analyzer.nlp_engine import NerModelConfiguration


@pytest.fixture(scope="module")
def ner_model_configuration_dict():
    this_path = Path(__file__).parent.absolute()
    conf_file = Path(this_path, "conf/test_transformers.yaml")
    with open(conf_file) as f:
        configuration_dict = yaml.safe_load(f)

    return configuration_dict["ner_model_configuration"]


@pytest.mark.parametrize(
    "key, original_value, expected_value",
    [
        ("labels_to_ignore", [], []),
        ("labels_to_ignore", ["A", "B"], ["A", "B"]),
        ("aggregation_strategy", "X", "X"),
        ("alignment_mode", "Y", "Y"),
        ("stride", 51, 51),
        ("model_to_presidio_entity_mapping", {"A": "B"}, {"A": "B"}),
        ("low_score_entity_names", ["A", "C"], ["A", "C"]),
        ("low_confidence_score_multiplier", 12.0, 12.0),
    ],
)
def test_from_dict_happy_path(
    ner_model_configuration_dict, key, original_value, expected_value
):
    ner_model_configuration_dict[key] = original_value

    result = NerModelConfiguration.from_dict(ner_model_configuration_dict)
    assert result.to_dict()[key] == expected_value


@pytest.mark.parametrize(
    "key, value",
    [
        ("stride", []),
        ("stride", "X"),
        ("alignment_mode", 5),
        ("low_confidence_score_multiplier", "X"),
    ],
)
def test_from_dict_wrong_types(ner_model_configuration_dict, key, value):
    new_config = ner_model_configuration_dict.copy()
    new_config[key] = value
    with pytest.raises(ValueError):
        NerModelConfiguration.from_dict(new_config)


@pytest.mark.parametrize(
    "key, value",
    [
        ("stride", None),
        ("alignment_mode", None),
    ],
)
def test_from_dict_none_resolves_to_default(ner_model_configuration_dict, key, value):
    new_config = ner_model_configuration_dict.copy()
    new_config[key] = value
    ner_model_configuration = NerModelConfiguration.from_dict(new_config)
    assert ner_model_configuration.stride is not None
    assert ner_model_configuration.alignment_mode is not None


def test_ner_model_configuration_validation_success():
    """Test NerModelConfiguration validates correctly."""
    config_data = {
        "aggregation_strategy": "max",
        "stride": 16,
        "alignment_mode": "expand",
        "default_score": 0.9,
        "low_confidence_score_multiplier": 0.3
    }

    config = NerModelConfiguration.from_dict(config_data)
    assert config.aggregation_strategy == "max"
    assert config.stride == 16
    assert config.default_score == 0.9
    assert config.low_confidence_score_multiplier == 0.3

def test_ner_model_configuration_invalid_score():
    """Test NerModelConfiguration rejects invalid score values."""
    config_data = {
        "default_score": 1.5  # Invalid: > 1.0
    }

    with pytest.raises(ValidationError) as exc_info:
        NerModelConfiguration.from_dict(config_data)

    assert "less than or equal to 1" in str(exc_info.value)

def test_backward_compatibility_ner_config_to_dict():
    """Test that NerModelConfiguration maintains backward compatibility."""
    config = NerModelConfiguration(default_score=0.8, stride=20)
    config_dict = config.to_dict()

    assert "default_score" in config_dict
    assert config_dict["default_score"] == 0.8
    assert config_dict["stride"] == 20
