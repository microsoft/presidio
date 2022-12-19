import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import AuTfnRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return AuTfnRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["AU_TFN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # Valid formatting and valid TFNs 
        ("876 543 210", 1, ((0, 11),), ((1.0, 1.0),), ),
        ("876543210", 1, ((0, 9),), ((1.0, 1.0),), ),
        # Valid formatting but invalid TFNs 
        ("824 753 557", 0, (), (),),
        ("824753557", 0, (), (),),
        # Invalid formatting and TFNs.  
        ("5282475355632", 0, (), (),),
        ("52824753556AF", 0, (), (),),
        ("51 824 753 5564", 0, (), (),),
        ("123 456\n789", 0, (), (),),
    ],
)
def test_when_all_tfns_then_succeed(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
