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


def test_pattern_validation_success():
    """Test that Pattern class validates correctly with valid data."""
    pattern_data = {
        "name": "US ZIP Code",
        "regex": r"\b\d{5}(?:-\d{4})?\b",
        "score": 0.85
    }

    pattern = Pattern.from_dict(pattern_data)
    assert pattern.name == "US ZIP Code"
    assert pattern.score == 0.85
    assert pattern.regex == r"\b\d{5}(?:-\d{4})?\b"

def test_pattern_validation_invalid_regex():
    """Test that Pattern class rejects invalid regex patterns."""
    pattern_data = {
        "name": "Invalid Pattern",
        "regex": "[unclosed_bracket",  # Invalid regex
        "score": 0.5
    }

    with pytest.raises(ValueError) as exc_info:
        Pattern.from_dict(pattern_data)


def test_pattern_validation_invalid_score_range():
    """Test that Pattern class rejects scores outside [0,1] range."""
    pattern_data = {
        "name": "Invalid Score",
        "regex": r"\btest\b",
        "score": 1.5  # Invalid: > 1.0
    }

    with pytest.raises(ValueError) as exc_info:
        Pattern.from_dict(pattern_data)


def test_backward_compatibility_pattern_to_dict():
    """Test that Pattern maintains backward compatibility with to_dict method."""
    pattern = Pattern(name="test", regex=r"\btest\b", score=0.5)
    pattern_dict = pattern.to_dict()

    expected = {"name": "test", "regex": r"\btest\b", "score": 0.5}
    assert pattern_dict == expected
