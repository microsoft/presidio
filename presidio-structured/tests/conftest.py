""" Pytest fixtures for presidio-structured tests. """

import pandas as pd
import pytest
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import PandasAnalysisBuilder, JsonAnalysisBuilder
from presidio_structured.config import StructuredAnalysis


@pytest.fixture
def sample_df():
    data = {
        "name": ["John Doe", "Jane Doe", "John Smith"],
        "email": [
            "john@example.com",
            "jane@example.com",
            "johnsmith@example.com",
        ],
        "phone": ["1234567890", "0987654321", "1122334455"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_json():
    data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "12345",
        },
    }
    return data


@pytest.fixture
def sample_json_with_array():
    data = {
        "users": [
            {"id": 1, "name": "John Doe"},
            {"id": 2, "name": "Jane Doe"},
        ]
    }
    return data


@pytest.fixture
def json_analysis_builder():
    return JsonAnalysisBuilder()


@pytest.fixture
def tabular_analysis_builder():
    return PandasAnalysisBuilder()


@pytest.fixture
def operators():
    return {
        "PERSON": OperatorConfig("replace", {"new_value": "PERSON_REPLACEMENT"}),
        "DEFAULT": OperatorConfig("replace", {"new_value": "DEFAULT_REPLACEMENT"}),
    }


@pytest.fixture
def operators_no_default():
    return {
        "PERSON": OperatorConfig("replace", {"new_value": "PERSON_REPLACEMENT"}),
    }


@pytest.fixture
def tabular_analysis():
    return StructuredAnalysis(
        entity_mapping={
            "name": "PERSON",
            "email": "EMAIL_ADDRESS",
            "phone": "PHONE_NUMBER",
        }
    )


@pytest.fixture
def json_analysis():
    return StructuredAnalysis(
        entity_mapping={
            "name": "PERSON",
            "address.city": "LOCATION",
        }
    )
