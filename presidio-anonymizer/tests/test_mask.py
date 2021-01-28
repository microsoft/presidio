import pytest

from presidio_anonymizer.anonymizers import Mask


@pytest.mark.parametrize(
    # fmt: off
    "original_text, masking_char, chars_to_mask, from_end, anonymized_text",
    [
        ("text", "*", 4, False, "****"),  # Fully mask
        ("text", "*", 4, True, "****"),  # Fully mask from the end
        ("text", "*", 3, False, "***t"),  # Partially mask
        ("text", "*", 3, True, "t***"),  # Partially mask from the end
        ("text", "*", 5, False, "****"),  # Fully mask with overflowing chars_to_mask
        ("text", "*", 5, True, "****"),  # from the end
        ("t", "*", 1, False, "*"),  # Fully mask one character text
        ("t", "*", 1, True, "*"),  # from the end
        ("t", "*", 3, False, "*"),  # with overflowing chars_to_mask
        ("t", "*", 3, True, "*"),  # from the end
        ("text", "😈", 4, False, "😈😈😈😈"),  # Mask with 'Unicode EmojiSources' character
        ("text", "*", 0, False, "text"),  # Nullified mask
        ("text", "*", 0, True, "text"),  # from the end
        ("text", "*", -1, False, "text"),  # Negative chars_to_mask
        ("text", "*", -1, True, "text"),  # from the end
    ]
    # fmt: on
)
def test_anonymize_returns_expected_string_for_valid_inputs(
    original_text, masking_char, chars_to_mask, from_end, anonymized_text
):
    # TODO: mock MaskParameters
    params = {
        "masking_char": masking_char,
        "chars_to_mask": chars_to_mask,
        "from_end": from_end,
    }

    actual_anonymized_text = Mask().anonymize(
        original_text=original_text, params=params
    )

    assert anonymized_text == actual_anonymized_text
