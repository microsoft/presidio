import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import DeBsnrRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeBsnrRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_BSNR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid BSNR formats (9 digits)
        # Note: BSNR without context has very low score (0.05)
        ("123456789", 1, ((0, 9),), ((0.01, 1.0),)),
        ("987654321", 1, ((0, 9),), ((0.01, 1.0),)),

        # With context - context words are in the CONTEXT list but score enhancement varies
        ("BSNR: 987654321", 1, ((6, 15),), ((0.01, 1.0),)),
        ("Betriebsstättennummer 123456700", 1, ((22, 31),), ((0.01, 1.0),)),

        # Invalid - too short
        ("12345678", 0, (), ()),

        # Invalid - too long
        ("1234567890", 0, (), ()),

        # Invalid - contains letters
        ("12345678A", 0, (), ()),
        # fmt: on
    ],
)
def test_when_bsnr_in_text_then_all_found(
    text, expected_len, expected_positions, expected_score_ranges, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


def test_recognizer_initialization():
    recognizer = DeBsnrRecognizer()
    assert recognizer.supported_entities == ["DE_BSNR"]
    assert recognizer.supported_language == "de"
    assert len(recognizer.patterns) >= 1
    assert len(recognizer.context) > 0
