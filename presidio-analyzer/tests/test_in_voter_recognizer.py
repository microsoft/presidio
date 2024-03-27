import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import InVoterRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return InVoterRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["IN_VOTER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_position, expected_score",
    [
        # fmt: off
        # valid
        ("KSD1287349", 1, (0, 10), 0.7),
        ("YVU2289013", 1, (0, 10), 0.7),
        ("NUP5632811", 1, (0, 10), 0.7),
        ("my voter: mnb2345117", 1, (10, 20), (0.7)),
        ("You can vote with your CPJ4467918 number", 1, (23, 33), 0.7),
        # invalid
        ("zxdf8923q1", 0, (), (),),
        ("A8923571WZ", 0, (), (),),
        # fmt: on
    ],
)
def test_when_voter_in_text_then_all_voter_found(
    text,
    expected_len,
    expected_position,
    expected_score,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)
    print(results)

    assert len(results) == expected_len
    if results:
        assert_result(
            results[0],
            entities[0],
            expected_position[0],
            expected_position[1],
            expected_score,
        )
