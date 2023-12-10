import os
import pytest

from presidio_analyzer.predefined_recognizers import AzureAILanguageRecognizer
import dotenv

dotenv.load_dotenv()


def requires_env_vars():
    azure_ai_key = os.environ.get("AZURE_AI_KEY", "")
    azure_ai_endpoint = os.environ.get("AZURE_AI_ENDPOINT", "")

    return pytest.mark.skipif(
        azure_ai_key == "" or azure_ai_endpoint == "",
        reason=f"Environment variables are not set"
    )


@requires_env_vars()
def test_get_supported_entities():
    azure_ai_recognizer = AzureAILanguageRecognizer()
    supported_entities = azure_ai_recognizer.get_supported_entities()
    assert len(supported_entities) > 10


@requires_env_vars()
def test_analyze_simple():
    azure_ai_recognizer = AzureAILanguageRecognizer(supported_language="en")
    text = "My name is John Smith and my email is john.smith@email.com"
    results = azure_ai_recognizer.analyze(text=text)
    assert len(results) == 2


@requires_env_vars()
def test_analyze_subset_of_entities_on_request():
    azure_ai_recognizer = AzureAILanguageRecognizer(supported_language="en")
    text = "My name is John Smith and my email is john.smith@email.com"
    results = azure_ai_recognizer.analyze(text=text, entities=["EMAIL"])
    assert len(results) == 1
    assert results[0].entity_type == "EMAIL"


@requires_env_vars()
def test_analyze_subset_of_entities_on_init():
    azure_ai_recognizer = AzureAILanguageRecognizer(
        supported_language="en", supported_entities=["EMAIL"]
    )
    text = "My name is John Smith and my email is john.smith@email.com"
    results = azure_ai_recognizer.analyze(text=text)
    assert len(results) == 1
    assert results[0].entity_type == "EMAIL"
