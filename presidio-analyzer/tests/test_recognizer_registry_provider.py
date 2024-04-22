import pytest
import re
from pathlib import Path
from typing import List


from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider
from presidio_analyzer import RecognizerRegistry


def assert_default_configuration(
    recognizer_registry: RecognizerRegistry, mandatory_recognizers: List[str]
):
    assert recognizer_registry.supported_languages == ["en"]
    assert recognizer_registry.global_regex_flags == re.DOTALL | re.MULTILINE | re.IGNORECASE
    names = [recognizer.name for recognizer in recognizer_registry.recognizers]
    for predefined_recognizer in mandatory_recognizers:
        assert predefined_recognizer in names


def test_recognizer_registry_provider_default_configuration(mandatory_recognizers):
    provider = RecognizerRegistryProvider()
    recognizer_registry = provider.create_recognizer_registry()
    assert_default_configuration(recognizer_registry, mandatory_recognizers)


def test_recognizer_registry_provider_configuration_file():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/test_recognizer_registry.yaml")
    provider = RecognizerRegistryProvider(test_yaml)
    recognizer_registry = provider.create_recognizer_registry()
    assert recognizer_registry.supported_languages == ["en", "es"]
    assert recognizer_registry.global_regex_flags == 26
    assert len(recognizer_registry.recognizers) == 5
    assert [recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "ItFiscalCodeRecognizer"] == ["en", "es"]
    assert [recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "CreditCardRecognizer"] == ["en"]
    assert [recognizer.supported_language for recognizer in recognizer_registry.recognizers if recognizer.name == "ExampleCustomRecognizer"] == ["en", "es"]
    snpanish_recognizer = [recognizer for recognizer in recognizer_registry.recognizers if recognizer.name == "ExampleCustomRecognizer" and recognizer.supported_language == "es"][0]
    assert snpanish_recognizer.context == ["tarjeta", "credito"]


def test_recognizer_registry_provider_missing_conf_file_expect_default_configuration(mandatory_recognizers):
    test_yaml = Path("missing.yaml")
    provider = RecognizerRegistryProvider(test_yaml)
    recognizer_registry = provider.create_recognizer_registry()
    assert_default_configuration(recognizer_registry, mandatory_recognizers)


def test_recognizer_registry_provider_corrupt_conf_file_expect_default_configurationl(mandatory_recognizers):
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/recognizers_error.yaml")

    provider = RecognizerRegistryProvider(conf_file=test_yaml)
    recognizer_registry = provider.create_recognizer_registry()
    assert_default_configuration(recognizer_registry, mandatory_recognizers)


def test_recognizer_registry_provider_conf_file_valid_missing_keys_default_values():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/recognizer_configuration_missing_keys.yaml")

    provider = RecognizerRegistryProvider(conf_file=test_yaml)
    recognizer_registry = provider.create_recognizer_registry()
    assert recognizer_registry.supported_languages == ["en"]
    assert recognizer_registry.global_regex_flags == 26
    assert len(recognizer_registry.recognizers) == 0


def test_recognizer_registry_provider_with_registry_configuration():
    registry_configuration = {
        "supported_languages": ["de", "es", "en"],
        "recognizers": [
            {
                "name": "Zip code Recognizer",
                "supported_language": "en",
                "patterns": [
                    {
                        "name": "zip code (weak)",
                        "regex": "(\\b\\d{5}(?:\\-\\d{4})?\\b)",
                        "score": 0.01,
                    }
                ],
                "context": ["zip", "code"],
                "supported_entity": "ZIP",
            }
        ]
    }

    provider = RecognizerRegistryProvider(registry_configuration=registry_configuration)
    recognizer_registry = provider.create_recognizer_registry()
    assert recognizer_registry.supported_languages == ["de", "es", "en"]
    assert recognizer_registry.global_regex_flags == re.DOTALL | re.MULTILINE | re.IGNORECASE
    assert len(recognizer_registry.recognizers) == 1
    recognizer = recognizer_registry.recognizers[0]
    assert recognizer.name == "Zip code Recognizer"
    assert recognizer.supported_language == "en"
    assert recognizer.supported_entities == ["ZIP"]
    assert len(recognizer.patterns) == 1


def test_recognizer_registry_provider_when_conf_file_and_registry_configuration_fail():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/recognizer_configuration_missing_keys.yaml")
    registry_configuration = {"supported_languages": ["de", "es"]}

    with pytest.raises(ValueError):
        RecognizerRegistryProvider(
            conf_file=test_yaml, registry_configuration=registry_configuration
        )
