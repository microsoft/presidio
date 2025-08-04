from pathlib import Path
from typing import Dict

import pytest
import spacy
import shutil

from presidio_analyzer.nlp_engine import (
    SpacyNlpEngine,
    StanzaNlpEngine,
    NlpEngineProvider,
)
from presidio_analyzer.nlp_engine.transformers_nlp_engine import TransformersNlpEngine

def _write_yaml(tmp_path, content: str, name: str = "config.yaml") -> Path:
    path = tmp_path / name
    path.write_text(content)
    return path

@pytest.fixture(scope="module")
def mock_he_model():
    """
    Create an empty Hebrew spaCy pipeline and save it to disk.

    So that it could be loaded using spacy.load()
    """
    he = spacy.blank("he")
    he.to_disk("he_test")
    yield
    shutil.rmtree("he_test", ignore_errors=True)


@pytest.fixture(scope="module")
def mock_bn_model():
    """
    Create an empty Bengali spaCy pipeline and save it to disk.

    So that it could be loaded using spacy.load()
    """
    bn = spacy.blank("bn")
    bn.to_disk("bn_test")
    yield
    shutil.rmtree("bn_test", ignore_errors=True)


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


def test_when_labels_to_ignore_not_define_in_conf_file_default_into_empty_set(mocker):
    conf_file = (Path(__file__).parent.parent/ "presidio_analyzer"/ "conf"/ "spacy_multilingual.yaml")
    engine = NlpEngineProvider(conf_file=conf_file).create_engine()
    assert len(engine.ner_model_configuration.labels_to_ignore) == 0


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

    
def test_create_engine_missing_ner_model_configuration_english_only():
    config = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_lg"}
        ],
    }
    provider = NlpEngineProvider(nlp_configuration=config)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert 'en' in engine.nlp
    assert isinstance(engine.nlp['en'], spacy.lang.en.English)


def test_create_engine_missing_ner_model_configuration_non_english(mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    config = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "de", "model_name": "de_core_news_md"}
        ],
    }
    provider = NlpEngineProvider(nlp_configuration=config)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert 'de' in engine.nlp
    assert isinstance(engine.nlp['de'], spacy.lang.de.German)


def test_create_engine_missing_ner_model_configuration_mixed_languages(mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    config = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_lg"},
            {"lang_code": "de", "model_name": "de_core_news_md"}
        ],
    }
    provider = NlpEngineProvider(nlp_configuration=config)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert set(engine.nlp.keys()) == {'en', 'de'}


def test_create_engine_missing_ner_model_configuration_empty_models():
    config = {
        "nlp_engine_name": "spacy",
        "models": [],
        # ner_model_configuration is missing
    }
    provider = NlpEngineProvider(nlp_configuration=config)
    with pytest.raises(ValueError) as e:
        provider.create_engine()
    assert "Configuration should include nlp_engine_name and models" in str(e.value)


def test_read_nlp_conf_file_invalid(tmp_path, caplog):
    yaml_content = """
nlp_engine_name: spacy
models:
  - lang_code: en
    model_name: en_core_web_lg
"""
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text(yaml_content)

    with caplog.at_level("WARNING"):
        config = NlpEngineProvider._read_nlp_conf(str(yaml_file))
        assert "ner_model_configuration is missing" in caplog.text
        assert config["nlp_engine_name"] == "spacy"
    yaml_file.unlink()


def test_supported_languages_only_en_warns_and_creates(tmp_path, caplog, mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    yaml_content = """
nlp_engine_name: spacy
models:
  - lang_code: en
    model_name: en_core_web_lg
supported_languages:
  - en
"""
    conf_file = _write_yaml(tmp_path, yaml_content)
    provider = NlpEngineProvider(conf_file=str(conf_file))
    with caplog.at_level("WARNING"):
        engine = provider.create_engine()
        assert "ner_model_configuration is missing" in caplog.text
    assert isinstance(engine, SpacyNlpEngine)
    assert "en" in engine.nlp
    conf_file.unlink()


def test_supported_languages_non_en_raises(tmp_path, mocker):
    yaml_content = """
nlp_engine_name: spacy
models:
  - lang_code: de
    model_name: de_core_news_md
supported_languages:
  - de
"""
    conf_file = _write_yaml(tmp_path, yaml_content)
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    with pytest.raises(ValueError) as excinfo:
        NlpEngineProvider(conf_file=str(conf_file)).create_engine()
    assert "missing 'ner_model_configuration'" in str(excinfo.value)
    conf_file.unlink()



def test_recognizer_registry_only_en_warns_and_creates(tmp_path, caplog, mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    yaml_content = """
nlp_engine_name: spacy
models:
  - lang_code: en
    model_name: en_core_web_lg
recognizer_registry:
  supported_languages:
    - en
"""
    conf_file = _write_yaml(tmp_path, yaml_content, "recog.yaml")
    provider = NlpEngineProvider(conf_file=str(conf_file))
    with caplog.at_level("WARNING"):
        engine = provider.create_engine()
        assert "ner_model_configuration is missing" in caplog.text
    assert isinstance(engine, SpacyNlpEngine)
    conf_file.unlink()



def test_recognizer_registry_non_en_raises(tmp_path, mocker):
    yaml_content = """
nlp_engine_name: spacy
models:
  - lang_code: en
    model_name: en_core_web_lg
recognizer_registry:
  supported_languages:
    - fr
"""
    conf_file = _write_yaml(tmp_path, yaml_content, "recog2.yaml")
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    with pytest.raises(ValueError) as excinfo:
        NlpEngineProvider(conf_file=str(conf_file)).create_engine()
    assert "missing 'ner_model_configuration'" in str(excinfo.value)
    conf_file.unlink()



def test_mixed_supported_and_recognizer_non_en_raises(tmp_path, mocker):
    yaml_content = """
nlp_engine_name: spacy
models:
  - lang_code: en
    model_name: en_core_web_lg
supported_languages:
  - en
recognizer_registry:
  supported_languages:
    - de
"""
    conf_file = _write_yaml(tmp_path, yaml_content, "mixed.yaml")
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    with pytest.raises(ValueError) as excinfo:
        NlpEngineProvider(conf_file=str(conf_file)).create_engine()
    assert "Detected languages: ['de', 'en']" in str(excinfo.value)
    conf_file.unlink()



def test_no_supported_or_recognizer_defaults_to_english(tmp_path, caplog, mocker):
    mocker.patch(
        "presidio_analyzer.nlp_engine.SpacyNlpEngine._download_spacy_model_if_needed",
        return_value=None,
    )
    yaml_content = """
nlp_engine_name: spacy
models:
  - lang_code: en
    model_name: en_core_web_lg
"""
    conf_file = _write_yaml(tmp_path, yaml_content, "none.yaml")
    provider = NlpEngineProvider(conf_file=str(conf_file))
    with caplog.at_level("WARNING"):
        engine = provider.create_engine()
        assert "ner_model_configuration is missing" in caplog.text
    assert isinstance(engine, SpacyNlpEngine)
    assert 'en' in engine.nlp
    conf_file.unlink()
    


def test_when_valid_nlp_engines_then_return_default_configuration():
    nlp_engines = (SpacyNlpEngine, StanzaNlpEngine, TransformersNlpEngine)
    provider = NlpEngineProvider(nlp_engines=nlp_engines)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.nlp is not None


def test_when_nlp_engines_type_is_not_tuple_then_fail():
    nlp_engines = [SpacyNlpEngine, StanzaNlpEngine, TransformersNlpEngine]
    
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_engines)
     
        
def test_when_invalid_nlp_engine_types_then_fail():
    nlp_engines = (1, 2, 3)
    
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_engines)


def test_when_valid_nlp_configuration_then_return_default_configuration():
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]
    }
    provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.nlp is not None

        
def test_when_nlp_configuration_is_passed_instead_of_nlp_engines_then_fail():
    nlp_configuration = {
        "nlp_engine_name": "stanza",
        "models": [{"lang_code": "en", "model_name": "en"}]
    }
 
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration)
        

def test_when_nlp_configuration_is_not_dict_then_fail():
    nlp_configuration = "not a dict"
    
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration)
        

def test_when_nlp_configuration_is_missing_nlp_engine_name_key_then_fail():
    nlp_configuration = {
        "models": [{"lang_code": "en", "model_name": "en"}]
    }
    
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration)
        
def test_when_nlp_configuration_is_missing_models_key_then_fail():
    nlp_configuration = {
        "nlp_engine_name": "stanza"
    }
    
    with pytest.raises(ValueError):
        NlpEngineProvider(nlp_configuration=nlp_configuration)


def test_when_valid_conf_file_then_return_default_configuration():
    file_name = "default.yaml"
    conf_file = Path(Path(__file__).parent, "conf", file_name)
    provider = NlpEngineProvider(conf_file=conf_file)
    engine = provider.create_engine()
    assert isinstance(engine, SpacyNlpEngine)
    assert engine.nlp is not None

def test_when_conf_file_is_empty_string_then_fail():
    conf_file = ''
    
    with pytest.raises(ValueError):
        NlpEngineProvider(conf_file=conf_file)


def test_when_conf_file_is_not_string_or_path_then_fail():
    conf_file = 1
    
    with pytest.raises(ValueError):
        NlpEngineProvider(conf_file=conf_file)


def test_when_conf_file_is_directory_then_fail():
    conf_file = '/'
    
    with pytest.raises(ValueError):
        NlpEngineProvider(conf_file=conf_file)


def test_when_conf_file_does_not_exist_then_fail():
    conf_file = 'test.yml'
    
    with pytest.raises(ValueError):
        NlpEngineProvider(conf_file=conf_file)
