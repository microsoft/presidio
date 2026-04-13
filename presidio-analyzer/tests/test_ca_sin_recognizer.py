import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import CaSinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return CaSinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["CA_SIN"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # --- Valid SINs ---
        # Space delimited
        ("130 692 544", 1, ((0, 11),), ((0.5, 0.81),),),
        ("435 418 165", 1, ((0, 11),), ((0.5, 0.81),),),
        ("948 584 792", 1, ((0, 11),), ((0.5, 0.81),),),
        # Hyphen delimited
        ("347-677-452", 1, ((0, 11),), ((0.5, 0.81),),),
        ("731-530-150", 1, ((0, 11),), ((0.5, 0.81),),),
        # No delimiter
        ("130692544", 1, ((0, 9),), ((0.0, 0.3),),),
        ("550090112", 1, ((0, 9),), ((0.0, 0.3),),),

        # --- Valid SIN with context ---
        ("my SIN is 130-692-544", 1, ((10, 21),), ((0.5, 0.81),),),
        ("mon NAS: 258 933 688", 1, ((9, 20),), ((0.5, 0.81),),),

        # --- Invalid: checksum failure ---
        ("130 692 545", 0, (), (),),
        ("130692545", 0, (), (),),
        ("435-418-166", 0, (), (),),

        # --- Invalid: reserved first digit ---
        ("046 454 286", 0, (), (),),
        ("812 345 678", 0, (), (),),

        # --- Invalid: all same digit ---
        ("111 111 111", 0, (), (),),
        ("999 999 999", 0, (), (),),

        # --- Invalid: mismatched delimiters ---
        ("046-454 286", 0, (), (),),
        ("046 454-286", 0, (), (),),

        # --- Invalid: wrong length ---
        ("13069254", 0, (), (),),
        ("1306925440", 0, (), (),),
        # fmt: on
    ],
)
def test_when_sin_in_text_then_all_ca_sins_are_found(
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
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
