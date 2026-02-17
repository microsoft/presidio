from pathlib import Path

from presidio_analyzer.analyzer.gliner_edge.recognizers import (
    EdgeONNXGLiNERRecognizer,
    GLiNERPartialCardRecognizer,
)
from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider


def test_gliner_edge_registry_configuration_loads(monkeypatch):
    monkeypatch.setattr(EdgeONNXGLiNERRecognizer, "load", lambda self: None)
    monkeypatch.setattr(GLiNERPartialCardRecognizer, "load", lambda self: None)

    conf_file = Path("presidio_analyzer/conf/gliner_edge_recognizers.yaml")
    provider = RecognizerRegistryProvider(conf_file=conf_file)
    registry = provider.create_recognizer_registry()

    names = [recognizer.name for recognizer in registry.recognizers]

    assert "GLiNERFreeTextRecognizer" in names
    assert "GLiNERDobRecognizer" in names
    assert "ContextAwareUsSsnRecognizer" in names
    assert "GLiNERPartialCardRecognizer" in names
    assert "SpacyRecognizer" not in names


def test_gliner_edge_configuration_preserves_custom_fields():
    conf_file = Path("presidio_analyzer/conf/gliner_edge_recognizers.yaml")
    provider = RecognizerRegistryProvider(conf_file=conf_file)

    free_text = next(
        rec
        for rec in provider.configuration["recognizers"]
        if isinstance(rec, dict) and rec.get("name") == "GLiNERFreeTextRecognizer"
    )

    assert free_text["model_name"] == "knowledgator/gliner-pii-edge-v1.0"
    assert free_text["onnx_model_file"] == "onnx/model.onnx"
    assert free_text["entity_mapping"]["name"] == "PERSON"
