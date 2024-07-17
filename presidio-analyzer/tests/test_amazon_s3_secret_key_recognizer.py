import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers import AmazonS3KeyRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return AmazonS3KeyRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["AMAZON_S3_KEY"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        ("abcdefghijklmnopqrst0123456789/+ABCDEFGH", 1, ((0, 40),), ((0.0, 0.5),),),
        ("73eTQ4IuhniBk=I38hjoD7J6G/4GBsAqw36DTqOA", 1, ((0, 40),), ((0.0, 0.5),),),
        ("my amazon s3 key is abcdefghijklmnopqrst0123456789/+ABCDEFGH", 1, ((20, 60),), ((0.0, 0.5),),),
        ("my amazon s3 key is 73eTQ4IuhniBk=I38hjoD7J6G/4GBsAqw36DTqOA", 1, ((20, 60),), ((0.0, 0.5),),),
        # fmt: on
    ],
)
def test_when_all_amazons3key_then_suceed(
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
