import pytest

from presidio_anonymizer.operators import EntityCounterAnonymizer, EntityCounterDeanonymizer


@pytest.mark.parametrize(
    # fmt: off
    "params, result",
    [
        ({'entity_mapping': {}, 'entity_type': 'LOCATION'}, "<LOCATION_0>"),
        ({'entity_mapping': {'LOCATION': {'Tashkent': '<LOCATION_0>'}}, 'entity_type': 'LOCATION'}, "<LOCATION_1>"),
        ({'entity_mapping': {'PERSON': {'Ravi': '<PERSON_0>'}}, 'entity_type': 'LOCATION'}, "<LOCATION_0>"),
    ],
    # fmt: on
)
def test_when_correct_counter_for_each_entity_type_is_returned(
    params, result
):
    entity_mapping = dict()
    text = EntityCounterAnonymizer().operate("London", params)
    assert text == result


def test_when_validate_anonymizer_then_correct_name():
    assert EntityCounterAnonymizer().operator_name() == "entity_counter"

def test_when_validate_deanonymizer_then_correct_name():
    assert EntityCounterDeanonymizer().operator_name() == "entity_counter_deanonymizer"

@pytest.mark.parametrize(
    # fmt: off
    "params, result",
    [
        ({'entity_mapping': {'LOCATION': {'Tashkent': '<LOCATION_0>'}}, 'entity_type': 'LOCATION'}, "Tashkent"),
        ({'entity_mapping': {'PERSON': {'Ravi': '<PERSON_0>'},
                             'LOCATION': {'London': '<LOCATION_0>',
                                          'Tashkent': '<LOCATION_1>'}}, 'entity_type': 'LOCATION'}, "London"),
    ],
    # fmt: on
)
def test_when_correct_counter_for_each_entity_type_is_returned(
    params, result
):
    entity_mapping = dict()
    text = EntityCounterDeanonymizer().operate("<LOCATION_0>", params)
    assert text == result
