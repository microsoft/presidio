import json
import os

from presidio_anonymizer.entities import AnalyzerResults, AnonymizerRequest


def test_analyzer_results_not_failing_on_empty_list():
    analyzer_result = AnalyzerResults()
    assert len(analyzer_result.to_sorted_unique_results()) == 0


def test_analyzer_results_sorted_set():
    json_path = json_path = file_path("dup_payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest(content)
        analyze_results = data.get_analysis_results()
        assert len(analyze_results) == len(content.get("analyzer_results"))
        sorted_results = analyze_results.to_sorted_unique_results()
        assert len(sorted_results) == 2
        assert list(sorted_results)[0].start < list(sorted_results)[1].start
        assert list(sorted_results)[0].end < list(sorted_results)[1].end


def test_analyzer_results_reversed_sorted_set():
    json_path = file_path("dup_payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest(content)
        analyze_results = data.get_analysis_results()
        assert len(analyze_results) == len(content.get("analyzer_results"))
        sorted_results = analyze_results.to_sorted_unique_results(True)
        assert len(sorted_results) == 2
        assert list(sorted_results)[1].start < list(sorted_results)[0].start
        assert list(sorted_results)[1].end < list(sorted_results)[0].end


def file_path(file_name: str):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', f"resources/{file_name}"))
