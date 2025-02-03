import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import FiPersonalIdentityCodeRecognizer


@pytest.fixture(scope="module")
def recognizer():
    """Return an instance of the FiPersonalIdentityCodeRecognizer."""
    return FiPersonalIdentityCodeRecognizer()


@pytest.fixture(scope="module")
def entities():
    """Return entities to analyze."""
    return ["FI_PERSONAL_IDENTITY_CODE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # Valid Finnish personal identity codes.
        (
            "010594Y9032",
            1,
            ((0, 11),),
        ),
        (
            "My personal identity code is: 010594Y9032. Thank you.",
            1,
            ((30, 41),),
        ),
        (
            "010594Y9021",
            1,
            ((0, 11),),
        ),
        (
            "020594X903P",
            1,
            ((0, 11),),
        ),
        (
            "020594X903P is my hetu.",
            1,
            ((0, 11),),
        ),
        (
            "020594X902N",
            1,
            ((0, 11),),
        ),
        (
            "Here's my henkilötunnus 020594X902N.",
            1,
            ((24, 35),),
        ),
        (
            "030594W903B",
            1,
            ((0, 11),),
        ),
        (
            "My finnish id code is030594W903B.",
            1,
            ((21, 32),),
        ),
        (
            "030694W9024",
            1,
            ((0, 11),),
        ),
        (
            "040594V9030",
            1,
            ((0, 11),),
        ),
        (
            "040594V902Y",
            1,
            ((0, 11),),
        ),
        (
            "050594U903M",
            1,
            ((0, 11),),
        ),
        (
            "050594U902L",
            1,
            ((0, 11),),
        ),
        (
            "010516B903X",
            1,
            ((0, 11),),
        ),
        (
            "010516B902W",
            1,
            ((0, 11),),
        ),
        (
            "020516C903K",
            1,
            ((0, 11),),
        ),
        (
            "020516C902J",
            1,
            ((0, 11),),
        ),
        (
            "030516D9037",
            1,
            ((0, 11),),
        ),
        (
            "030516D9026",
            1,
            ((0, 11),),
        ),
        (
            "010501E9032",
            1,
            ((0, 11),),
        ),
        (
            "020502E902X",
            1,
            ((0, 11),),
        ),
        (
            "020503F9037",
            1,
            ((0, 11),),
        ),
        (
            "020504A902E",
            1,
            ((0, 11),),
        ),
        (
            "020504B904H",
            1,
            ((0, 11),),
        ),
        # invalid Personal Identity Codes scores
        ("111111-111A", 0, ()),
        ("111111+110G", 0, ()),
        ("311190-1111", 0, ()),
        ("310289-211C", 0, ()),
        ("012245A110G", 0, ()),
        ("010324A110G", 0, ()),
    ],
)
def test_when_all_finnish_personal_identity_code_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    """Tests our recognizer against valid & invalid Finnish personal identity codes."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
