from pathlib import Path

import pytest
import spacy

from presidio_analyzer.nlp_engine import (
    SpacyNlpEngine,
    StanzaNlpEngine,
    NlpEngineProvider,
)
from presidio_analyzer.nlp_engine.transformers_nlp_engine import TransformersNlpEngine


def test_when_create_nlp_engine__then_return_default_configuration():
    provider = NlpEngineProvider()
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.nlp is not None


def test_when_create_nlp_engine_then_simple_config_succeeds(mock_he_model):
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "he", "model_name": "he_test"}],
    }

    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.nlp["he"] is not None
    assert isinstance(engine.nlp["he"], spacy.lang.he.Hebrew)


def test_when_create_nlp_engine_then_two_models_succeeds(mock_he_model, mock_bn_model):
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


def test_when_create_nlp_engine_from_wrong_conf_then_fail():
    with pytest.raises(OSError):
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "de", "model_name": "de_test"}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        provider.create_engine()


def test_when_unsupported_nlp_engine_then_fail():
    with pytest.raises(ValueError) as e:
        unsupported_engine_name = "not exists"
        nlp_configuration = {
            "nlp_engine_name": unsupported_engine_name,
            "models": [{"lang_code": "de", "model_name": "de_test"}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        provider.create_engine()
    assert (f"NLP engine '{unsupported_engine_name}' is not available. "
    "Make sure you have all required packages installed") == e.value.args[0]


def test_when_read_test_nlp_conf_file_then_returns_spacy_nlp_engine():
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


def test_when_both_conf_and_config_then_fail():
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "he", "model_name": "he_test"}],
    }
    conf_file = "conf/default.yaml"

    with pytest.raises(ValueError):
        NlpEngineProvider(conf_file=conf_file, nlp_configuration=nlp_configuration)


@pytest.mark.skip_engine("transformers_en")
def test_when_create_transformers_nlp_engine_then_succeeds():
    nlp_configuration={
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "en",
                "model_name": {
                    "spacy": "en_core_web_sm",
                    "transformers": "dslim/bert-base-NER",
                },
            }
        ],
    }
    engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
    assert isinstance(engine, TransformersNlpEngine)
    assert engine.nlp["en"] is not None
    assert isinstance(engine.nlp["en"], spacy.lang.en.English)


def test_when_create_transformers_nlp_engine_from_wrong_conf_with_model_name_not_dict_then_fail():
    nlp_configuration={
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


def test_when_create_transformers_nlp_engine_from_wrong_conf_with_model_name_keys_not_include_spacy_then_fail():
    nlp_configuration={
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "en",
                "model_name": {  # keys should contain transformers and spacy
                    "not_spacy": "en_core_web_sm",
                    "transformers": "dslim/bert-base-NER",
                },
            }
        ],
    }
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()


def test_when_create_transformers_nlp_engine_from_wrong_conf_with_model_name_keys_not_include_transformers_then_fail():
    nlp_configuration={
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "en",
                "model_name": {  # keys should contain transformers and spacy
                    "spacy": "en_core_web_sm",
                    "not_transformers": "dslim/bert-base-NER",
                },
            }
        ],
    }
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()