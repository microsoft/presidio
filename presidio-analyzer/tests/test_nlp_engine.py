import pytest
import spacy

from presidio_analyzer.nlp_engine import SpacyNlpEngine, create_nlp_engine


def test_create_nlp_engine_two_models_succeeds(mock_he_model, mock_bn_model):
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "he", "model_name": "he_test"},
            {"lang_code": "bn", "model_name": "bn_test"},
        ],
    }

    engine = create_nlp_engine(nlp_configuration=nlp_configuration)

    assert isinstance(engine, SpacyNlpEngine)

    assert engine.nlp["he"] is not None
    assert isinstance(engine.nlp["he"], spacy.lang.he.Hebrew)

    assert engine.nlp["bn"] is not None
    assert isinstance(engine.nlp["bn"], spacy.lang.bn.Bengali)


def test_create_nlp_engine_from_wrong_conf_fails():
    with pytest.raises(OSError):
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "de", "model_name": "de_test"}],
        }
        create_nlp_engine(nlp_configuration=nlp_configuration)
