from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnalyzerResults, AnonymizerRequest


def test_given_empty_list_then_analyzer_result_creation_is_not_failing():
    analyzer_result = AnalyzerResults()
    assert len(analyzer_result.to_sorted_unique_results()) == 0


def test_given_conflicting_analyzer_results_then_none_conflicting_results_returned():
    payload = get_dup_payload()
    data = AnonymizerRequest(payload, AnonymizerEngine().builtin_anonymizers)
    analyze_results = data.get_analysis_results()
    assert len(analyze_results) == len(payload.get("analyzer_results"))
    sorted_results = analyze_results.to_sorted_unique_results()
    assert len(sorted_results) == 2
    assert list(sorted_results)[0].start < list(sorted_results)[1].start
    assert list(sorted_results)[0].end < list(sorted_results)[1].end


def test_given_conflict_analyzer_results_then_reversed_none_conflict_list_returned():
    payload = get_dup_payload()
    data = AnonymizerRequest(payload, AnonymizerEngine().builtin_anonymizers)
    analyze_results = data.get_analysis_results()
    assert len(analyze_results) == len(payload.get("analyzer_results"))
    sorted_results = analyze_results.to_sorted_unique_results(True)
    assert len(sorted_results) == 2
    assert list(sorted_results)[1].start < list(sorted_results)[0].start
    assert list(sorted_results)[1].end < list(sorted_results)[0].end


def get_dup_payload():
    return {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "analyzer_results": [
            {"start": 48, "end": 57, "score": 0.95, "entity_type": "PHONE_NUMBER"},
            {"start": 24, "end": 32, "score": 0.6, "entity_type": "FULL_NAME"},
            {"start": 24, "end": 28, "score": 0.9, "entity_type": "FIRST_NAME"},
            {"start": 29, "end": 32, "score": 0.6, "entity_type": "LAST_NAME"},
            {"start": 24, "end": 30, "score": 0.8, "entity_type": "NAME"},
        ],
    }
