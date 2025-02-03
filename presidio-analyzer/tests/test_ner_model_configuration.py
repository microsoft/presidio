from pathlib import Path

import pytest
import yaml

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
        ("stride", None),
        ("alignment_mode", 5),
        ("alignment_mode", None),
        ("low_confidence_score_multiplier", "X"),
    ],
)
def test_from_dict_wrong_types(ner_model_configuration_dict, key, value):
    new_config = ner_model_configuration_dict.copy()
    new_config[key] = value
    with pytest.raises(ValueError):
        NerModelConfiguration.from_dict(new_config)

