import pytest

from presidio_analyzer.nlp_engine import TransformersNlpEngine


def test_default_models():
    engine = TransformersNlpEngine()
    assert len(engine.models) > 0
    assert engine.models[0]["lang_code"] == "en"
    assert isinstance(engine.models[0]["model_name"], dict)


def test_validate_model_params_happy_path():
    model = {
        "lang_code": "en",
        "model_name": {
            "spacy": "en_core_web_sm",
            "transformers": "obi/deid_roberta_i2b2",
        },
    }

    TransformersNlpEngine._validate_model_params(model)


@pytest.mark.parametrize(
    "key",
    [("lang_code"), ("model_name"), ("model_name.spacy"), ("model_name.transformers")],
)
def test_validate_model_params_missing_fields(key):
    model = {
        "lang_code": "en",
        "model_name": {
            "spacy": "en_core_web_sm",
            "transformers": "obi/deid_roberta_i2b2",
        },
    }
    keys = key.split(".")
    if len(keys) == 1:
        del model[keys[0]]
    else:
        del model[keys[0]][keys[1]]

    with pytest.raises(ValueError):
        TransformersNlpEngine._validate_model_params(model)
