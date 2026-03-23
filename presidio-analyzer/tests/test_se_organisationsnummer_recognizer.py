import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import SeOrganisationsnummerRecognizer


@pytest.fixture(scope="module")
def recognizer():
    """Return an instance of the SeOrganisationsnummerRecognizer."""
    return SeOrganisationsnummerRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return entities to analyze."""
    return ["SE_ORGANISATIONSNUMMER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # Valid Swedish organisationsnummer.
        (
            "212000-0142",
            1,
            ((0, 11),),
        ),
        (
            "Our company identity code is: 212000-0142. Thank you.",
            1,
            ((30, 41),),
        ),
        (
            "2120000142",
            1,
            ((0, 10),),
        ),
        (
            "556703-7485",
            1,
            ((0, 11),),
        ),
        (
            "5567037485",
            1,
            ((0, 10),),
        ),
        (
            "556703-7485 är vårt orgnummer.",
            1,
            ((0, 11),),
        ),
        (
            "556703-7485 tillhör vårt företag.",
            1,
            ((0, 11),),
        ),
        # invalid Organisationsnummer scores
        ("19000309-3393", 0, ()),
        ("19001309-2393", 0, ()),
        ("55670x-7485", 0, ()),
        ("556703-7r85", 0, ()),],
)
def test_when_all_swedish_organisationsnummer_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    """Tests our recognizer against valid & invalid Swedish organisationsnummer."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)