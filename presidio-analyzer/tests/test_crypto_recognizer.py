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
        ## Bitcoin
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
        ("8f953371d3e85eddb89b05ed6b9e680791055315c73e1025ab5dba7bb2aee189", 0, (),),
        
        ## Ethereum
        ## Match
        # Test with valid Ethereum address
        ("0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed", 1, ((0, 42),),),
        # Test with multiple valid Ethereum addresses
        ("0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed 0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb", 2, ((0, 42), (43, 85)),),
        # Test with valid Ethereum address
        ("My Ethereum wallet is 0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB", 1, ((22, 64),),),
        
        ## No match
        ("lowercase address 0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed", 0, (),),
        ("checksummed but invalid address 0xdbF03B407c01E7cD3CBea99509d93f8DDdC8C6FB", 0, (),),
        
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
