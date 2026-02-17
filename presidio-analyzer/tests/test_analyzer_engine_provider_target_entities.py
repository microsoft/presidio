from presidio_analyzer.analyzer_engine_provider import AnalyzerEngineProvider
from presidio_analyzer.local_recognizer import LocalRecognizer
from presidio_analyzer.recognizer_registry import RecognizerRegistry


class DummyRecognizer(LocalRecognizer):
    def __init__(self, supported_entities, name):
        super().__init__(
            supported_entities=supported_entities,
            name=name,
            supported_language="en",
        )

    def load(self):
        return None

    def analyze(self, text, entities, nlp_artifacts=None):
        return []


def test_apply_target_entities_prunes_registry_and_mapping():
    provider = AnalyzerEngineProvider.__new__(AnalyzerEngineProvider)
    provider.configuration = {"target_entities": ["PERSON", "EMAIL_ADDRESS"]}

    gliner_like = DummyRecognizer(["PERSON", "LOCATION"], "GLiNERLike")
    gliner_like.model_to_presidio_entity_mapping = {
        "name": "PERSON",
        "address": "LOCATION",
    }
    gliner_like.gliner_labels = ["name", "address"]

    email_recognizer = DummyRecognizer(["EMAIL_ADDRESS"], "EmailLike")
    phone_recognizer = DummyRecognizer(["PHONE_NUMBER"], "PhoneLike")

    registry = RecognizerRegistry(
        recognizers=[gliner_like, email_recognizer, phone_recognizer],
        supported_languages=["en"],
    )

    provider._apply_target_entities(registry=registry)

    names = {r.name for r in registry.recognizers}
    assert "PhoneLike" not in names
    assert "GLiNERLike" in names
    assert "EmailLike" in names

    assert gliner_like.supported_entities == ["PERSON"]
    assert gliner_like.model_to_presidio_entity_mapping == {"name": "PERSON"}
    assert gliner_like.gliner_labels == ["name"]
