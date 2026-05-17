import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import UsCliaRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return UsCliaRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["US_CLIA"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid CLIA, weak base score (no separators, no context)
        ("11D2030122", 1, ((0, 10),), ((0.0, 0.4),),),
        # Valid CLIA, lowercase 'd' is also accepted (case-insensitive global flag)
        ("11d2030122", 1, ((0, 10),), ((0.0, 0.4),),),
        # Valid CLIA with dashes — medium score from the separator pattern
        ("11-D-2030122", 1, ((0, 12),), ((0.3, 0.6),),),
        # Valid CLIA with spaces — medium score from the separator pattern
        ("11 D 2030122", 1, ((0, 12),), ((0.3, 0.6),),),
        # CLIA inside text with explicit "CLIA:" prefix — base regex score; the
        # AnalyzerEngine layer applies context boosting on top of this.
        (
            "CLIA: 11D2030122",
            1, ((6, 16),), ((0.0, 0.4),),
        ),
        # CLIA in a sentence with "laboratory" context — bare recognizer score
        (
            "Laboratory ID 22D9876543 was on the report",
            1, ((14, 24),), ((0.0, 0.4),),
        ),
        # Multiple CLIA numbers in text
        (
            "Labs 11D2030122 and 33D4455667 sent results",
            2, ((5, 15), (20, 30),), ((0.0, 0.4), (0.0, 0.4),),
        ),
        # Invalid: position 3 is not 'D'
        ("11X2030122", 0, (), (),),
        # Invalid: too short (9 chars)
        ("11D203012", 0, (), (),),
        # Invalid: too long (11 chars)
        ("11D20301223", 0, (), (),),
        # Invalid: starts with a letter (positions 1-2 must be digits)
        ("AAD2030122", 0, (), (),),
        # Invalid: all trailing digits identical — degenerate, invalidated
        ("11D0000000", 0, (), (),),
        ("11D1111111", 0, (), (),),
        # fmt: on
    ],
)
def test_when_clia_in_text_then_all_us_clias_are_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    results = recognizer.analyze(text, entities)
    results = sorted(results, key=lambda x: x.start)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        if st_score == "max":
            st_score = max_score
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


def test_clia_recognizer_supported_entity(recognizer):
    """Test that recognizer supports the correct entity."""
    assert recognizer.supported_entities == ["US_CLIA"]


def test_clia_recognizer_supported_language(recognizer):
    """Test that recognizer supports English by default."""
    assert recognizer.supported_language == "en"


def test_clia_recognizer_context_words(recognizer):
    """Test that recognizer has appropriate context words."""
    expected_context = [
        "clia",
        "clia number",
        "clia id",
        "lab",
        "laboratory",
        "clinical laboratory",
        "lab id",
        "lab number",
    ]
    assert recognizer.context == expected_context


def test_clia_recognizer_country_code(recognizer):
    """Test that recognizer is tagged as US-specific."""
    assert recognizer.COUNTRY_CODE == "us"
