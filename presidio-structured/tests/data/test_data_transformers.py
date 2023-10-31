import pytest
from pandas import DataFrame
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured.data.data_transformers import DataTransformerBase, PandasDataTransformer, JsonDataTransformer
from presidio_structured.config import StructuredAnalysis

class TestDataTransformerBase:
    def test_abstract_init_raises(self, sample_df, tabular_analysis_builder, operators):
        with pytest.raises(TypeError):
            DataTransformerBase()

class TestPandasDataTransformer:
    def test_process(self, sample_df, operators, tabular_analysis):
        transformer = PandasDataTransformer()
        result = transformer.operate(sample_df, tabular_analysis, operators)
        assert isinstance(result, DataFrame)
        for key in tabular_analysis.entity_mapping:
            if key == 'name':
                assert all(result[key] == "PERSON_REPLACEMENT")
            else:
                assert all(result[key] == "DEFAULT_REPLACEMENT")

    def test_process_no_default_should_raise(self, sample_df, operators_no_default, tabular_analysis):
        transformer = PandasDataTransformer()
        with pytest.raises(ValueError):
            transformer.operate(sample_df, tabular_analysis, operators_no_default)

    def test_process_invalid_data(self, sample_json, tabular_analysis, operators):
        transformer = PandasDataTransformer()
        with pytest.raises(ValueError):
            transformer.operate(sample_json, tabular_analysis, operators)

class TestJsonDataTransformer:
    def test_process(self, sample_json, operators, json_analysis):
        transformer = JsonDataTransformer()
        result = transformer.operate(sample_json, json_analysis, operators)
        assert isinstance(result, dict)
        for key, value in json_analysis.entity_mapping.items():
            keys = key.split(".")
            nested_value = sample_json
            for inner_key in keys:
                nested_value = nested_value[inner_key]
            if value == 'PERSON':
                assert nested_value == "PERSON_REPLACEMENT"
            else:
                assert nested_value == "DEFAULT_REPLACEMENT"

    def test_process_no_default_should_raise(self, sample_json, operators_no_default, json_analysis):
        transformer = JsonDataTransformer()
        with pytest.raises(ValueError):
            transformer.operate(sample_json, json_analysis, operators_no_default)

    def test_process_invalid_data(self, sample_df, json_analysis, operators):
        transformer = JsonDataTransformer()
        with pytest.raises(ValueError):
          transformer.operate(sample_df, json_analysis, operators)