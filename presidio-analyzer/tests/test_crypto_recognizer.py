import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import CryptoRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return CryptoRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["CRYPTO"]


# Generate random address https://www.bitaddress.org/
@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        ("16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ", 1, ((0, 34),),),
        ("my wallet address is: 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ", 1, ((22, 56),),),
        ("16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2", 0, ()),
        ("my wallet address is: 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2", 0, ()),
    ],
)
def test_all_cryptos(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
