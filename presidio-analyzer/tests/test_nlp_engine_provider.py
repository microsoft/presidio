from pathlib import Path
from typing import Dict

import pytest
import spacy

from presidio_analyzer.nlp_engine import (
    SpacyNlpEngine,
    StanzaNlpEngine,
    NlpEngineProvider,
)
from presidio_analyzer.nlp_engine.transformers_nlp_engine import TransformersNlpEngine


@pytest.fixture(scope="module")
def mock_he_model():
    """
    Create an empty Hebrew spaCy pipeline and save it to disk.

    So that it could be loaded using spacy.load()
    """
    he = spacy.blank("he")
    he.to_disk("he_test")


@pytest.fixture(scope="module")
def mock_bn_model():
    """
    Create an empty Bengali spaCy pipeline and save it to disk.

    So that it could be loaded using spacy.load()
    """
    bn = spacy.blank("bn")
    bn.to_disk("bn_test")


@pytest.fixture(scope="session")
def nlp_configuration_dict() -> Dict:
    nlp_configuration = {
        "lang_code": "en",
        "model_name": {
            "spacy": "en_core_web_lg",
            "transformers": "StanfordAIMI/stanford-deidentifier-base",
        },
    }

    return nlp_configuration


@pytest.fixture(scope="session")
def ner_model_configuration_dict() -> Dict:
    ner_model_configuration = {
        "nlp_engine_name": "transformers",
        "aggregation_strategy": "simple",
        "alignment_mode": "strict",
        "low_score_entity_names": ["O"],
    }
    return ner_model_configuration


def test_when_create_nlp_engine__then_return_default_configuration():
    provider = NlpEngineProvider()
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.nlp is not None


def test_when_create_nlp_engine_then_simple_config_succeeds(mocker, mock_he_model):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "he", "model_name": "he_test"}],
    }

    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.nlp["he"] is not None
    assert isinstance(engine.nlp["he"], spacy.lang.he.Hebrew)


def test_when_create_nlp_engine_then_two_models_succeeds(
    mocker, mock_he_model, mock_bn_model
):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "he", "model_name": "he_test"},
            {"lang_code": "bn", "model_name": "bn_test"},
        ],
    }

    engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    assert isinstance(engine, SpacyNlpEngine)

    assert engine.nlp["he"] is not None
    assert isinstance(engine.nlp["he"], spacy.lang.he.Hebrew)

    assert engine.nlp["bn"] is not None
    assert isinstance(engine.nlp["bn"], spacy.lang.bn.Bengali)


def test_when_create_nlp_engine_from_wrong_conf_then_fail(mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    with pytest.raises(OSError):
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "de", "model_name": "de_test"}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        provider.create_engine()


def test_when_unsupported_nlp_engine_then_fail(mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    with pytest.raises(ValueError) as e:
        unsupported_engine_name = "not exists"
        nlp_configuration = {
            "nlp_engine_name": unsupported_engine_name,
            "models": [{"lang_code": "de", "model_name": "de_test"}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        provider.create_engine()
    assert (
        f"NLP engine '{unsupported_engine_name}' is not available. "
        "Make sure you have all required packages installed"
    ) == e.value.args[0]


def test_when_read_test_nlp_conf_file_then_returns_spacy_nlp_engine(mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    test_conf_file = Path(Path(__file__).parent, "conf", "test.yaml")
    provider = NlpEngineProvider(conf_file=test_conf_file)
    nlp_engine = provider.create_engine()

    assert isinstance(nlp_engine, SpacyNlpEngine)
    assert nlp_engine.nlp is not None


@pytest.mark.skip_engine("stanza_en")
def test_when_read_test_nlp_conf_file_then_returns_stanza_nlp_engine():
    test_conf_file = Path(Path(__file__).parent, "conf", "test_stanza.yaml")
    provider = NlpEngineProvider(conf_file=test_conf_file)
    nlp_engine = provider.create_engine()

    assert isinstance(nlp_engine, StanzaNlpEngine)
    assert nlp_engine.nlp is not None


def test_when_both_conf_and_config_then_fail(mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "he", "model_name": "he_test"}],
    }
    conf_file = "conf/default.yaml"

    with pytest.raises(ValueError):
        NlpEngineProvider(conf_file=conf_file, nlp_configuration=nlp_configuration)


@pytest.mark.skip_engine("transformers_en")
def test_when_create_transformers_nlp_engine_then_succeeds(mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.TransformersNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    nlp_configuration = {
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "en",
                "model_name": {
                    "spacy": "en_core_web_lg",
                    "transformers": "StanfordAIMI/stanford-deidentifier-base",
                },
            }
        ],
    }
    engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
    assert isinstance(engine, TransformersNlpEngine)
    assert engine.nlp["en"] is not None
    assert isinstance(engine.nlp["en"], spacy.lang.en.English)


@pytest.mark.skip_engine("transformers_en")
def test_when_create_transformers_nlp_engine_from_wrong_conf_with_model_name_not_dict_then_fail(
    mocker,
):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    nlp_configuration = {
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "en",
                "model_name": object,
            }
        ],
    }
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()


def test_when_create_transformers_nlp_engine_from_wrong_conf_with_model_name_keys_not_include_spacy_then_fail(
    nlp_configuration_dict,
):
    nlp_configuration = nlp_configuration_dict.copy()
    del nlp_configuration["model_name"]["spacy"]
    nlp_configuration["model_name"]["not_spacy"] = "ERROR"
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()


def test_when_create_transformers_nlp_engine_from_wrong_conf_with_model_name_keys_not_include_transformers_then_fail(
    nlp_configuration_dict,
):
    nlp_configuration = nlp_configuration_dict.copy()
    del nlp_configuration["model_name"]["transformers"]
    nlp_configuration["model_name"]["not_transformers"] = "ERROR"
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()


def test_nlp_engine_provider_init_through_nlp_engine_configuration():
    engine = NlpEngineProvider().create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.engine_name == "spacy"
