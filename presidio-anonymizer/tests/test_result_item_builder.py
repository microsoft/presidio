import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine.result import ResultItemBuilder, \
    AnonymizedEntity, DecryptedEntity
from presidio_anonymizer.operators import OperatorType


def test_given_anonymize_operator_type_then_we_get_anonymize_result_item():
    result = ResultItemBuilder(OperatorType.Anonymize).set_operator_name(
        "encrypt").set_entity_type("PERSON").set_operated_on_text("new text").set_end(
        100).build()
    assert isinstance(result, AnonymizedEntity)
    assert result.entity_type == "PERSON"
    assert result.anonymizer == "encrypt"
    assert result.anonymized_text == "new text"
    assert result.end == 100
    assert result.start == 0


def test_given_decrypt_operator_type_then_we_get_decrypt_result_item():
    result = ResultItemBuilder(OperatorType.Deanonymize).set_operator_name(
        "encrypt").set_entity_type("PERSON").set_operated_on_text(
        "new text").set_end(
        100).build()
    assert isinstance(result, DecryptedEntity)
    assert result.entity_type == "PERSON"
    assert result.decrypted_text == "new text"
    assert result.end == 100
    assert result.start == 0


def test_given_invalid_operator_type_then_we_get_decrypt_result_item():
    with pytest.raises(InvalidParamException, match="Invalid operator type 3"):
        ResultItemBuilder(3).build()
