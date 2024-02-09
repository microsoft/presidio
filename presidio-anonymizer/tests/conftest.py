from typing import Dict, Type

import pytest

from presidio_anonymizer.operators import Operator, OperatorType


@pytest.fixture(scope="session")
def mock_anonymizer_cls() -> Type[Operator]:
    class MyAnonymizer(Operator):
        def operate(self, text: str, params: Dict = None) -> str:
            return text

        def validate(self, params: Dict = None) -> None:
            pass

        def operator_name(self) -> str:
            return "MockAnonymizer"

        def operator_type(self) -> OperatorType:
            return OperatorType.Anonymize

    return MyAnonymizer


@pytest.fixture(scope="session")
def mock_deanonymizer_cls() -> Type[Operator]:
    class MyDeanonymizer(Operator):
        def operate(self, text: str, params: Dict = None) -> str:
            return text

        def validate(self, params: Dict = None) -> None:
            pass

        def operator_name(self) -> str:
            return "MockDeanonymizer"

        def operator_type(self) -> OperatorType:
            return OperatorType.Deanonymize

    return MyDeanonymizer
