import pytest

from presidio_anonymizer.entities import AnalyzerResult, InvalidParamException


@pytest.mark.parametrize(
    # fmt: off
    "start, end",
    [
        (0, 10),
        (10, 10),
        (2, 8),
        (0, 8),
        (0, 10),
    ],
    # fmt: on
)
def test_analyzer_result_successfully_contains_another(start, end):
    first = AnalyzerResult("", 0, 0, 10)
    second = AnalyzerResult("", 0, start, end)

    assert first.contains(second)


@pytest.mark.parametrize(
    # fmt: off
    "start, end",
    [
        (4, 10),
        (5, 11),
        (0, 5),
        (0, 6),
    ],
    # fmt: on
)
def test_analyzer_result_fail_contains_another(start, end):
    first = AnalyzerResult("", 0, 5, 10)
    second = AnalyzerResult("", 0, start, end)

    assert not first.contains(second)


def test_analyzer_result_successfully_equal_indices_of_another():
    first = AnalyzerResult("", 0, 0, 10)
    second = AnalyzerResult("", 0, 0, 10)

    assert first.equal_indices(second)


@pytest.mark.parametrize(
    # fmt: off
    "start, end",
    [
        (4, 10),
        (5, 11),
        (0, 5),
        (0, 6),
    ],
    # fmt: on
)
def test_analyzer_result_fail_equal_indices_of_another(start, end):
    first = AnalyzerResult("", 0, 5, 10)
    second = AnalyzerResult("", 0, start, end)

    assert not first.equal_indices(second)


def test_analyzer_result_equals_another():
    first = AnalyzerResult("bla", 0.2, 0, 10)
    second = AnalyzerResult("bla", 0.2, 0, 10)

    assert first == second


@pytest.mark.parametrize(
    # fmt: off
    "entity_type, score, start, end",
    [
        ("bla", 0.2, 4, 10),
        ("changed", 0.2, 0, 10),
        ("bla", 0.2, 0, 11),
        ("bla", 0.3, 0, 10),
    ],
    # fmt: on
)
def test_analyzer_result_not_equal_another(entity_type, score, start, end):
    first = AnalyzerResult("bla", 0.2, 0, 10)
    second = AnalyzerResult(entity_type, score, start, end)

    assert first != second


def test_analyzer_result_successfully_hashed_and_equal():
    first = AnalyzerResult("", 0, 0, 10)
    second = AnalyzerResult("", 0, 0, 10)

    assert first.__hash__() == second.__hash__()


@pytest.mark.parametrize(
    # fmt: off
    "entity_type, score, start, end",
    [
        ("bla", 0.2, 4, 10),
        ("changed", 0.2, 0, 10),
        ("bla", 0.2, 0, 11),
        ("bla", 0.3, 0, 10),
    ],
    # fmt: on
)
def test_analyzer_result_hash_not_equal_another(entity_type, score, start, end):
    first = AnalyzerResult("bla", 0.2, 0, 10)
    second = AnalyzerResult(entity_type, score, start, end)

    assert first.__hash__() != second.__hash__()


@pytest.mark.parametrize(
    # fmt: off
    "entity_type, score, start, end",
    [
        ("bla", 0.2, 0, 10),
        ("changed", 0.2, 2, 10),
        ("bla", 0.3, 0, 11),
        ("bla", 0.1, 0, 10),
    ],
    # fmt: on
)
def test_analyzer_result_has_conflict(entity_type, score, start, end):
    first = AnalyzerResult("bla", 0.2, 2, 10)
    second = AnalyzerResult(entity_type, score, start, end)

    assert first.has_conflict(second)


@pytest.mark.parametrize(
    # fmt: off
    "entity_type, score, start, end",
    [
        ("bla", 0.2, 3, 10),
        ("changed", 0.1, 2, 10),
        ("bla", 0.3, 0, 9),
    ],
    # fmt: on
)
def test_analyzer_result_has_no_conflict(entity_type, score, start, end):
    first = AnalyzerResult("bla", 0.2, 2, 10)
    second = AnalyzerResult(entity_type, score, start, end)

    assert not first.has_conflict(second)


@pytest.mark.parametrize(
    # fmt: off
    "request_json, result_text",
    [
        ({}, "Invalid input, analyzer result must contain start",),
        ({
             "end": 32,
             "score": 0.8,
             "entity_type": "NUMBER"
         }, "Invalid input, analyzer result must contain start",),
        ({
             "start": 28,
             "score": 0.8,
             "entity_type": "NUMBER"
         }, "Invalid input, analyzer result must contain end",),
        ({
             "start": 28,
             "end": 32,
             "entity_type": "NUMBER"
         }, "Invalid input, analyzer result must contain score",),
        ({
             "start": 28,
             "end": 32,
             "score": 0.8,
         }, "Invalid input, analyzer result must contain entity_type",),
    ],
    # fmt: on
)
def test_analyzer_result_fails_on_invalid_json_formats(request_json, result_text):
    try:
        AnalyzerResult.validate_and_create(request_json)
    except InvalidParamException as e:
        assert e.err == result_text
    except Exception as e:
        assert not e


def test_analyzer_result_pass_with_valid_json():
    content = {
        "start": 0,
        "end": 32,
        "score": 0.8,
        "entity_type": "NUMBER"
    }
    data = AnalyzerResult.validate_and_create(content)
    assert data.start == content.get("start")
    assert data.end == content.get("end")
    assert data.score == content.get("score")
    assert data.entity_type == content.get("entity_type")


@pytest.mark.parametrize(
    # fmt: off
    "start, end",
    [
        (4, 10),
        (4, 9),
        (0, 2),
        (5, 9),
    ],
    # fmt: on
)
def test_analyzer_result_greater_of_another(start, end):
    first = AnalyzerResult("", 0, 5, 10)
    second = AnalyzerResult("", 0, start, end)

    assert first.__gt__(second)


@pytest.mark.parametrize(
    # fmt: off
    "start, end",
    [
        (5, 10),
        (6, 12),
        (6, 7),
    ],
    # fmt: on
)
def test_analyzer_result_not_greater_of_another(start, end):
    first = AnalyzerResult("", 0, 5, 10)
    second = AnalyzerResult("", 0, start, end)

    assert not first.__gt__(second)
