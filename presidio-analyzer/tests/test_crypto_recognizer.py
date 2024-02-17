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
        # fmt: off
        ## Match
        # Test with valid P2PKH address that starts with 1 and 33 base58 characters
        ("16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ", 1, ((0, 34),),),        
        # Test with valid P2SH address that starts with 3 and 33 base58 characters
        ("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", 1, ((0, 34),),),
        # Test with valid Bech32 address that starts with bc1 and 39 base58 characters
        ("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq", 1, ((0, 42),),),
        # Test with valid Bech32m address that starts with bc1 and 59 base58 characters
        ("bc1p5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge8ztwac72sfr9rusxg3297", 1, ((0, 62),),),
        # Test with multiple valid addresses
        ("16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", 2, ((0, 34), (35, 69)),),
        # Test with valid address in a sentence
        ("my wallet address is: 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ", 1, ((22, 56),),),

        ## No match
        # Test with invalid address
        ("16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2", 0, ()),
        # Test with invalid address in a sentence
        ("my wallet address is: 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2", 0, ()),
        # Test with empty string
        ("", 0, (),),
        # fmt: on
    ],
)
def test_when_all_cryptos_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)
