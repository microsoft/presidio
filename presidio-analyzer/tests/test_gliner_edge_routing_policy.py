from presidio_analyzer.analysis_explanation import AnalysisExplanation
from presidio_analyzer.analyzer.gliner_edge.routing_policy import filter_results_by_source
from presidio_analyzer.recognizer_result import RecognizerResult


def _result(entity, start, end, score, recognizer_name):
    return RecognizerResult(
        entity_type=entity,
        start=start,
        end=end,
        score=score,
        analysis_explanation=AnalysisExplanation(
            recognizer=recognizer_name,
            original_score=score,
            textual_explanation="test",
        ),
    )


def test_filter_results_by_source_keeps_owned_entities():
    text = "John Doe email john@example.com"
    results = [
        _result("PERSON", 0, 8, 0.8, "GLiNERFreeTextRecognizer"),
        _result("PERSON", 0, 8, 0.9, "SpacyRecognizer"),
        _result("EMAIL_ADDRESS", 15, 31, 0.7, "EmailRecognizer"),
    ]

    filtered = filter_results_by_source(
        text=text,
        results=results,
        use_source_routing=True,
        gliner_owned_entities={"PERSON"},
        regex_owned_entities={"EMAIL_ADDRESS"},
        gliner_recognizer_names=("GLiNERFreeTextRecognizer", "GLiNERDobRecognizer"),
    )

    assert len(filtered) == 2
    assert any(r.entity_type == "PERSON" and r.analysis_explanation.recognizer == "GLiNERFreeTextRecognizer" for r in filtered)
    assert any(r.entity_type == "EMAIL_ADDRESS" for r in filtered)
