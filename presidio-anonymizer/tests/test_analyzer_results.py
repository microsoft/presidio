import json
import os

from presidio_anonymizer.entities import AnalyzerResults, AnonymizerRequest


def test_given_empty_list_then_analyzer_result_creation_is_not_failing():
    analyzer_result = AnalyzerResults()
    assert len(analyzer_result.to_sorted_unique_results()) == 0


def test_given_conflicting_analyzer_results_then_none_conflicting_results_returned():
    payload = get_dup_payload()
    data = AnonymizerRequest(payload)
    analyze_results = data.get_analysis_results()
    assert len(analyze_results) == len(payload.get("analyzer_results"))
    sorted_results = analyze_results.to_sorted_unique_results()
    assert len(sorted_results) == 2
    assert list(sorted_results)[0].start < list(sorted_results)[1].start
    assert list(sorted_results)[0].end < list(sorted_results)[1].end


def test_given_conflict_analyzer_results_then_reversed_none_conflict_list_returned():
    payload = get_dup_payload()
    data = AnonymizerRequest(payload)
    analyze_results = data.get_analysis_results()
    assert len(analyze_results) == len(payload.get("analyzer_results"))
    sorted_results = analyze_results.to_sorted_unique_results(True)
    assert len(sorted_results) == 2
    assert list(sorted_results)[1].start < list(sorted_results)[0].start
    assert list(sorted_results)[1].end < list(sorted_results)[0].end


content = {}


def get_dup_payload():
    global content
    if not content:
        json_path = file_path("dup_payload.json")
        with open(json_path) as json_file:
            content = json.load(json_file)
    return content


def file_path(file_name: str):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"resources/{file_name}"))
