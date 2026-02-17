from unittest.mock import MagicMock

from presidio_analyzer.analyzer.gliner_edge.recognizers import (
    ContextAwareUsSsnRecognizer,
    EdgeONNXGLiNERRecognizer,
    GLiNERPartialCardRecognizer,
)
from presidio_analyzer.recognizer_result import RecognizerResult


def test_context_aware_ssn_filters_low_score_without_context(monkeypatch):
    def fake_super_analyze(self, text, entities, nlp_artifacts=None):
        return [
            RecognizerResult(entity_type="US_SSN", start=9, end=20, score=0.05),
            RecognizerResult(entity_type="US_SSN", start=29, end=40, score=0.9),
        ]

    monkeypatch.setattr(
        "presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer.UsSsnRecognizer.analyze",
        fake_super_analyze,
    )

    recognizer = ContextAwareUsSsnRecognizer(
        min_score=0.5,
        low_score_require_context=True,
        context_terms=["ssn"],
        context_window_chars=5,
    )

    text = "identifier 123-45-6789 and ssn 987-65-4321"
    results = recognizer.analyze(text=text, entities=["US_SSN"])

    assert len(results) == 1
    assert results[0].score == 0.9


def test_partial_card_recognizer_detects_last_four():
    recognizer = GLiNERPartialCardRecognizer(enabled=False)
    recognizer.enabled = True
    recognizer.gliner = MagicMock()
    recognizer.gliner.predict_entities.return_value = [
        {
            "label": "partial credit card",
            "text": "card ending in 4821",
            "score": 0.81,
        }
    ]

    text = "Payment failed for your credit card ending in 4821 yesterday."
    results = recognizer.analyze(text=text, entities=["CREDIT_CARD"])

    assert len(results) == 1
    assert results[0].entity_type == "CREDIT_CARD"
    assert text[results[0].start : results[0].end] == "4821"


def test_partial_card_respects_target_entities():
    recognizer = GLiNERPartialCardRecognizer(enabled=False, target_entities=["US_SSN"])
    recognizer.enabled = True
    recognizer.gliner = MagicMock()

    text = "Credit card ending in 4821"
    results = recognizer.analyze(text=text, entities=["CREDIT_CARD"])

    assert results == []
    recognizer.gliner.predict_entities.assert_not_called()


def test_edge_gliner_uses_fixed_configured_labels(monkeypatch):
    monkeypatch.setattr(EdgeONNXGLiNERRecognizer, "load", lambda self: None)

    recognizer = EdgeONNXGLiNERRecognizer(
        name="Edge",
        supported_language="en",
        model_name="knowledgator/gliner-pii-edge-v1.0",
        onnx_model_file="onnx/model.onnx",
        entity_mapping={"name": "PERSON"},
        threshold=0.45,
    )

    recognizer.gliner = MagicMock()
    recognizer.gliner.predict_entities.return_value = [
        {
            "label": "name",
            "start": 0,
            "end": 4,
            "score": 0.9,
        }
    ]

    results = recognizer.analyze(text="John", entities=["PERSON", "EMAIL_ADDRESS"])

    assert len(results) == 1
    assert results[0].entity_type == "PERSON"

    call_kwargs = recognizer.gliner.predict_entities.call_args.kwargs
    assert call_kwargs["labels"] == ["name"]
