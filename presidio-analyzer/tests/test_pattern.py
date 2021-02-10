import pytest

from presidio_analyzer import Pattern


@pytest.fixture(scope="module")
def my_pattern():
    return Pattern(name="my pattern", score=0.9, regex="[re]")


@pytest.fixture(scope="module")
def my_pattern_dict():
    return {"name": "my pattern", "regex": "[re]", "score": 0.9}


def test_when_use_to_dict_return_dict(my_pattern, my_pattern_dict):
    expected = my_pattern_dict
    actual = my_pattern.to_dict()

    assert expected == actual


def test_when_use_from_dict_return_pattern(my_pattern, my_pattern_dict):
    expected = my_pattern
    actual = Pattern.from_dict(my_pattern_dict)

    assert expected.name == actual.name
    assert expected.score == actual.score
    assert expected.regex == actual.regex
