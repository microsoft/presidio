""" Test the analysis builder """

import pandas as pd
import pytest

from presidio_analyzer import AnalyzerEngine

from presidio_structured import JsonAnalysisBuilder, PandasAnalysisBuilder

# NOTE: we won't go into depth unit-testing all analyzers, as that is covered in the presidio-analyzer tests


def test_generate_analysis_tabular(tabular_analysis_builder, sample_df):
    structured_analysis = tabular_analysis_builder.generate_analysis(sample_df)

    assert structured_analysis.entity_mapping["name"] == "PERSON"
    assert structured_analysis.entity_mapping["email"] == "EMAIL_ADDRESS"
    assert structured_analysis.entity_mapping["phone"] == "PHONE_NUMBER"


def test_generate_analysis_tabular_with_sampling(tabular_analysis_builder, sample_df):
    structured_analysis = tabular_analysis_builder.generate_analysis(sample_df, n=2)

    assert len(structured_analysis.entity_mapping) == 3
    assert structured_analysis.entity_mapping["name"] == "PERSON"
    assert structured_analysis.entity_mapping["email"] == "EMAIL_ADDRESS"
    assert structured_analysis.entity_mapping["phone"] == "PHONE_NUMBER"


def test_generate_analysis_tabular_with_invalid_sampling(
    tabular_analysis_builder, sample_df
):
    with pytest.raises(ValueError):
        tabular_analysis_builder.generate_analysis(sample_df, n=-1)


def test_find_most_common_entity(tabular_analysis_builder, sample_df):
    key_recognizer_result_map = tabular_analysis_builder._generate_key_rec_results_map(
        sample_df, "en"
    )

    assert len(key_recognizer_result_map) == 3
    assert key_recognizer_result_map["name"].entity_type == "PERSON"
    assert key_recognizer_result_map["email"].entity_type == "EMAIL_ADDRESS"
    assert key_recognizer_result_map["phone"].entity_type == "PHONE_NUMBER"


def test_find_most_common_entity_with_empty_df(tabular_analysis_builder):
    df = pd.DataFrame()
    key_recognizer_result_map = tabular_analysis_builder._generate_key_rec_results_map(
        df, "en"
    )

    assert len(key_recognizer_result_map) == 0


def test_analysis_tabular_when_default_threshold_is_half_then_phone_does_not_pass(
    sample_df,
):
    analyzer_engine = AnalyzerEngine(default_score_threshold=0.5)
    tabular_analysis_builder = PandasAnalysisBuilder(analyzer_engine)
    structured_analysis = tabular_analysis_builder.generate_analysis(sample_df)

    assert len(structured_analysis.entity_mapping) == 2


def test_analysis_tabular_when_default_threshold_is_zero_then_all_results_pass(
    sample_df,
):
    analyzer_engine = AnalyzerEngine(default_score_threshold=0)
    tabular_analysis_builder = PandasAnalysisBuilder(analyzer_engine)
    structured_analysis = tabular_analysis_builder.generate_analysis(sample_df)

    assert len(structured_analysis.entity_mapping) == 3


def test_generate_analysis_json(json_analysis_builder, sample_json):
    structured_analysis = json_analysis_builder.generate_analysis(sample_json)

    assert structured_analysis.entity_mapping["name"] == "PERSON"
    assert structured_analysis.entity_mapping["address.city"] == "LOCATION"


def test_generate_analysis_json_with_list_should_raise(
    json_analysis_builder, sample_json_with_array
):
    # this feature is not supported by the BatchAnalyzerEngine used in the JsonAnalysisBuilder
    with pytest.raises(ValueError):
        json_analysis_builder.generate_analysis(sample_json_with_array)


def test_generate_analysis_json_with_empty_data(json_analysis_builder):
    data = {}
    structured_analysis = json_analysis_builder.generate_analysis(data)

    assert len(structured_analysis.entity_mapping) == 0


def test_analysis_json_when_default_threshold_is_high_then_only_email_passes(
    sample_json,
):
    analyzer_engine = AnalyzerEngine(default_score_threshold=0.9)
    json_analysis_builder = JsonAnalysisBuilder(analyzer_engine)
    structured_analysis = json_analysis_builder.generate_analysis(sample_json)

    assert len(structured_analysis.entity_mapping) == 1
