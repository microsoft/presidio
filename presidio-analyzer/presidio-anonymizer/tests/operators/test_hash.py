import pytest

from presidio_anonymizer.operators import Hash
from presidio_anonymizer.entities import InvalidParamError


@pytest.mark.parametrize(
    "text, anonymized_text",
    [
        # fmt: off
        (
            "123456",
            "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",
        ),  # Hash 123456
        (
            "54321",
            "20f3765880a5c269b747e1e906054a4b4a3a991259f1e16b5dde4742cec2319a",
        ),  # Hash 54321
        (
            "😈😈😈😈",
            "0fff975d92d0f33d23030511b4dc02cf706f4da9b9ffdefebed56bb364b73219",
        ),
        # Hash 'Unicode EmojiSources' character
        # fmt: on
    ],
)
def test_when_given_valid_value_without_hash_type_then_expected_sha256_string_returned(
    text, anonymized_text
):
    params = {}
    actual_anonymized_text = Hash().operate(text=text, params=params)

    assert anonymized_text == actual_anonymized_text


@pytest.mark.parametrize(
    "text, hash_type, anonymized_text",
    [
        # fmt: off
        (
            "123456",
            "sha256",
            "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92",
        ),  # Sha256 Hash 123456
        (
            "54321",
            "sha256",
            "20f3765880a5c269b747e1e906054a4b4a3a991259f1e16b5dde4742cec2319a",
        ),  # Sha256 Hash 54321
        (
            "😈😈😈😈",
            "sha256",
            "0fff975d92d0f33d23030511b4dc02cf706f4da9b9ffdefebed56bb364b73219",
        ),  # Sha256  Hash 'Unicode EmojiSources' character
        (
            "123456",
            "sha512",
            "ba3253876aed6bc22d4a6ff53d8406c6ad864195ed144ab5c87621b6c233b54"
            "8baeae6956df346ec8c17f5ea10f35ee3cbc514797ed7ddd3145464e2a0bab413",
        ),  # Sha512 Hash 123456
        (
            "54321",
            "sha512",
            "e16d6b316f3bef1794c548b7a98b969a6aacb02f6ae5138efc1c443ae6643a6a77"
            "d92a0e33e382d6cbb7758f9ab25ab0f97504554d1904620a41fed463796fc2",
        ),  # Sha512 Hash 54321
        (
            "😈😈😈😈",
            "sha512",
            "8500ce5af27e4db23f533e54c8c1ad74de62e93ca77c05e8de90e9eb27c7abe155"
            "e01d47868eded3106ccf6ac1f5c33bbaa95d55d40e9d89091c3d4617cc6d60",
        ),  # Sha512  Hash 'Unicode EmojiSources' character
        # fmt: on
    ],
)
def test_when_given_valid_value_with_hash_type_then_expected_string_returned(
    text, hash_type, anonymized_text
):
    params = {
        "hash_type": hash_type,
    }
    actual_anonymized_text = Hash().operate(text=text, params=params)

    assert anonymized_text == actual_anonymized_text


def test_when_hash_type_not_in_range_then_ipe_raised():
    params = _get_default_hash_parameters()
    params["hash_type"] = "not_a_hash"

    with pytest.raises(
        InvalidParamError,
        match="Parameter hash_type value not_a_hash is not in range of values"
        " \\['sha256', 'sha512'\\]",
    ):
        Hash().validate(params)


def test_when_hash_type_is_missing_then_we_pass():
    params = _get_default_hash_parameters()
    params.pop("hash_type")

    Hash().validate(params)


def test_when_hash_type_is_empty_string_then_ipe_raised():
    params = _get_default_hash_parameters()
    params["hash_type"] = ""

    with pytest.raises(
        InvalidParamError,
        match="Parameter hash_type value  is not in range of values"
        " \\['sha256', 'sha512'\\]",
    ):
        Hash().validate(params)


def test_when_validate_anonymizer_then_correct_name():
    assert Hash().operator_name() == "hash"


def _get_default_hash_parameters():
    return {"hash_type": ""}
