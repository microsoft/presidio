from unittest.mock import Mock

import pytest
from presidio_anonymizer.entities import OperatorConfig

from presidio_structured import TabularEngine


def test_tabular_engine_anonymize_calls_data_transformer_operate():
    # Arrange
    data_transformer = Mock()
    tabular_engine = TabularEngine(data_transformer)
    data = Mock()
    structured_analysis = Mock()
    operators = {"DEFAULT": OperatorConfig("replace")}

    # Act
    tabular_engine.anonymize(data, structured_analysis, operators)

    # Assert
    data_transformer.operate.assert_called_once_with(
        data, structured_analysis, operators
    )


def test_tabular_engine_anonymize_adds_default_operator_if_none_provided():
    # Arrange
    data_transformer = Mock()
    tabular_engine = TabularEngine(data_transformer)
    data = Mock()
    structured_analysis = Mock()

    # Act
    tabular_engine.anonymize(data, structured_analysis)

    # Assert
    data_transformer.operate.assert_called_once()
    args, _ = data_transformer.operate.call_args
    assert "DEFAULT" in args[2]


def test_tabular_engine_anonymize_does_not_override_existing_default_operator():
    # Arrange
    data_transformer = Mock()
    tabular_engine = TabularEngine(data_transformer)
    data = Mock()
    structured_analysis = Mock()
    operators = {"DEFAULT": OperatorConfig("custom")}

    # Act
    tabular_engine.anonymize(data, structured_analysis, operators)

    # Assert
    data_transformer.operate.assert_called_once_with(
        data, structured_analysis, operators
    )
