from typing import Dict, Type

import pytest

from presidio_anonymizer.entities import RecognizerResult
from presidio_anonymizer.operators import Operator, OperatorType


@pytest.fixture(scope="session")
def three_person_analyzer_results():
    text = "Peter gave Julie a book about Heidi."
    analyzer_results = [
        RecognizerResult("PERSON", 0, 5, 1.0),
        RecognizerResult("PERSON", 11, 16, 1.0),
        RecognizerResult("PERSON", 30, 35, 1.0),
    ]
    return text, analyzer_results


@pytest.fixture(scope="session")
def mock_anonymizer_cls() -> Type[Operator]:
    class MockAnonymizer(Operator):
        def operate(self, text: str, params: Dict = None) -> str:
            return text

        def validate(self, params: Dict = None) -> None:
            pass

        def operator_name(self) -> str:
            return self.__class__.__name__

        def operator_type(self) -> OperatorType:
            return OperatorType.Anonymize

    return MockAnonymizer


@pytest.fixture(scope="session")
def mock_deanonymizer_cls() -> Type[Operator]:
    class MockDeanonymizer(Operator):
        def operate(self, text: str, params: Dict = None) -> str:
            return text

        def validate(self, params: Dict = None) -> None:
            pass

        def operator_name(self) -> str:
            return self.__class__.__name__

        def operator_type(self) -> OperatorType:
            return OperatorType.Deanonymize

    return MockDeanonymizer
