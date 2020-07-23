from presidio_analyzer import RecognizerResult
from tests import assert_result_within_score_range
import pytest

ENTITY_TYPE = "ANY_ENTITY"


def test_assert_result_within_score_range_uses_given_range():
    result = RecognizerResult(ENTITY_TYPE, 0, 10, 0.3)
    assert_result_within_score_range(result, ENTITY_TYPE, 0, 10, 0.2, 0.4)

    result = RecognizerResult(ENTITY_TYPE, 0, 10, 0.1)
    assert_result_within_score_range(result, ENTITY_TYPE, 0, 10, 0.05, 0.15)

    result = RecognizerResult(ENTITY_TYPE, 0, 10, 0.9)
    assert_result_within_score_range(result, ENTITY_TYPE, 0, 10, 0.89, 0.91)


def test_assert_result_within_score_range_uses_given_range_fails():

    with pytest.raises(AssertionError):
        result = RecognizerResult(ENTITY_TYPE, 0, 10, 0.3)
        assert_result_within_score_range(result, ENTITY_TYPE, 0, 10, 0.4, 0.6)

    with pytest.raises(AssertionError):
        result = RecognizerResult(ENTITY_TYPE, 0, 10, 0)
        assert_result_within_score_range(result, ENTITY_TYPE, 0, 10, 0.4, 0.6)

    with pytest.raises(AssertionError):
        result = RecognizerResult(ENTITY_TYPE, 0, 10, 1)
        assert_result_within_score_range(result, ENTITY_TYPE, 0, 10, 0, 0.5)
