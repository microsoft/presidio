import pytest

from presidio_analyzer import RecognizerResult


@pytest.mark.parametrize(
    # fmt: off
    "start, end",
    [
        (0, 10),
        (2, 8),
        (0, 8),
        (0, 10),
    ],
    # fmt: on
)
def test_given_recognizer_results_then_one_contains_another(start, end):
    first = create_recognizer_result("", 0, 0, 10)
    second = create_recognizer_result("", 0, start, end)

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
def test_given_recognizer_result_then_they_do_not_contain_one_another(start, end):
    first = create_recognizer_result("", 0, 5, 10)
    second = create_recognizer_result("", 0, start, end)

    assert not first.contains(second)


def test_given_recognizer_results_with_same_indices_then_indices_are_equal():
    first = create_recognizer_result("", 0, 0, 10)
    second = create_recognizer_result("", 0, 0, 10)

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
def test_given_recognizer_results_with_different_indices_then_indices_are_not_equal(
    start, end
):
    first = create_recognizer_result("", 0, 5, 10)
    second = create_recognizer_result("", 0, start, end)

    assert not first.equal_indices(second)


def test_given_identical_recognizer_results_then_they_are_equal():
    first = create_recognizer_result("bla", 0.2, 0, 10)
    second = create_recognizer_result("bla", 0.2, 0, 10)

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
def test_given_different_recognizer_result_then_they_are_not_equal(
    entity_type, score, start, end
):
    first = create_recognizer_result("bla", 0.2, 0, 10)
    second = create_recognizer_result(entity_type, score, start, end)

    assert first != second


def test_given_recognizer_result_then_their_hash_is_equal():
    first = create_recognizer_result("", 0, 0, 10)
    second = create_recognizer_result("", 0, 0, 10)

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
def test_given_different_recognizer_results_then_hash_is_not_equal(
    entity_type, score, start, end
):
    first = create_recognizer_result("bla", 0.2, 0, 10)
    second = create_recognizer_result(entity_type, score, start, end)

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
def test_given_recognizer_results_with_conflicting_indices_then_there_is_a_conflict(
    entity_type, score, start, end
):
    first = create_recognizer_result("bla", 0.2, 2, 10)
    second = create_recognizer_result(entity_type, score, start, end)

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
def test_given_recognizer_results_with_no_conflicting_indices_then_there_is_no_conflict(
    entity_type, score, start, end
):
    first = create_recognizer_result("bla", 0.2, 2, 10)
    second = create_recognizer_result(entity_type, score, start, end)

    assert not first.has_conflict(second)


def test_given_valid_json_for_creating_recognizer_result_then_creation_is_successful():
    data = create_recognizer_result("NUMBER", 0.8, 0, 32)
    assert data.start == 0
    assert data.end == 32
    assert data.score == 0.8
    assert data.entity_type == "NUMBER"


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
def test_given_recognizer_results_then_one_is_greater_then_another(start, end):
    first = create_recognizer_result("", 0, 5, 10)
    second = create_recognizer_result("", 0, start, end)

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
def test_given_recognizer_result_then_one_is_not_greater_then_another(start, end):
    first = create_recognizer_result("", 0, 5, 10)
    second = create_recognizer_result("", 0, start, end)

    assert not first.__gt__(second)


def create_recognizer_result(entity_type: str, score: float, start: int, end: int):
    data = {"entity_type": entity_type, "score": score, "start": start, "end": end}
    return RecognizerResult.from_json(data)
