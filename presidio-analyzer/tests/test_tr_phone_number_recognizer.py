"""Tests for Turkish phone number (TR_PHONE_NUMBER) recognizer."""

import pytest
from presidio_analyzer.predefined_recognizers import PhoneRecognizer

from tests import assert_result_within_score_range

TURKISH_CONTEXT = [
    "telefon",
    "telefon numarası",
    "cep telefonu",
    "cep no",
    "telefon no",
    "numara",
    "mobil telefon",
    "mobil no",
    "hücresel telefon",
    "ara",
    "ulaş",
    "iletişim",
    "bağlantı",
    "irtibat",
    "numaram",
    "telefonum",
    "cep telefonum",
    "mobil telefonum",
    "telefon numarası",
    "cep numarası",
    "mobil numarası",
    "phone",
    "mobile",
    "cell",
    "cellphone",
    "call",
    "contact",
    "number",
    "phone number",
    "sms",
    "mesaj",
    "whatsapp",
    "telegram",
    "signal",
    "viber",
]


@pytest.fixture(scope="module")
def recognizer():
    """Create a TR-configured PhoneRecognizer instance for testing."""
    return PhoneRecognizer(
        supported_regions=["TR"],
        supported_entity="TR_PHONE_NUMBER",
        context=TURKISH_CONTEXT,
        supported_language="en",
    )


@pytest.fixture(scope="module")
def entities():
    """Return the TR_PHONE_NUMBER entity type for testing."""
    return ["TR_PHONE_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # International format (+90)
        ("+905321234567", 1, ((0, 13),), ((0.4, 1.0),)),
        ("+90 532 123 45 67", 1, ((0, 17),), ((0.4, 1.0),)),
        ("+90-532-123-45-67", 1, ((0, 17),), ((0.4, 1.0),)),
        ("+90 (532) 123 45 67", 1, ((0, 19),), ((0.4, 1.0),)),
        # National format (0)
        ("05321234567", 1, ((0, 11),), ((0.3, 1.0),)),
        ("0 532 123 45 67", 1, ((0, 15),), ((0.3, 1.0),)),
        ("0-532-123-45-67", 1, ((0, 15),), ((0.3, 1.0),)),
        ("0 (532) 1234567", 1, ((0, 15),), ((0.3, 1.0),)),
        # Local format (just the number)
        ("5321234567", 1, ((0, 10),), ((0.15, 1.0),)),
        ("532 123 45 67", 1, ((0, 13),), ((0.15, 1.0),)),
        ("532-123-45-67", 1, ((0, 13),), ((0.15, 1.0),)),
        # In sentence with context
        (
            "Telefon numaram +905321234567 olarak kayitli.",
            1,
            ((16, 29),),
            ((0.4, 1.0),),
        ),
        (
            "Cep no: 05321234567",
            1,
            ((8, 19),),
            ((0.3, 1.0),),
        ),
        (
            "Phone: 5321234567",
            1,
            ((7, 17),),
            ((0.15, 1.0),),
        ),
        # Multiple numbers
        (
            "Birinci: +905321234567, Ikinci: 05359876543",
            2,
            ((9, 22), (32, 43)),
            ((0.4, 1.0), (0.3, 1.0)),
        ),
        # Geographic number: starts with 4 (valid geographic)
        ("4321234567", 1, ((0, 10),), ((0.05, 1.0),)),
        # Invalid: too short
        ("532123456", 0, (), ()),
        # Invalid: too long (11 digits without prefix)
        ("53212345678", 0, (), ()),
        # Invalid: not a phone number
        ("hello world", 0, (), ()),
        ("1234567890", 0, (), ()),
        # False positive: random 10-digit number not starting with 5
        ("12345678901", 0, (), ()),
        # Geographic numbers: valid area codes (starts with 2, 3, 4)
        ("2121234567", 1, ((0, 10),), ((0.05, 1.0),)),
        ("3121234567", 1, ((0, 10),), ((0.05, 1.0),)),
        ("4621234567", 1, ((0, 10),), ((0.05, 1.0),)),
        # Geographic numbers (lower priority)
        ("02121234567", 1, ((0, 11),), ((0.1, 1.0),)),
        ("0216 123 45 67", 1, ((0, 14),), ((0.1, 1.0),)),
        ("0232 123 45 67", 1, ((0, 14),), ((0.05, 1.0),)),
        ("0312 123 45 67", 1, ((0, 14),), ((0.1, 1.0),)),
        ("0412 123 45 67", 1, ((0, 14),), ((0.1, 1.0),)),

        # False positive: embedded in longer number
        ("15053212345678", 0, (), ()),
        # Geographic number: starts with 2 (valid geographic)
        # Note: 2023123456 is not recognized by phonenumbers as valid TR number
        # ("202" is not a valid Turkish area code in phonenumbers)
        # ("2121234567", 1, ((0, 10),), ((0.05, 1.0),)),
        # False positive: TCKN-like (11 digits starting with 1)
        ("10000000146", 0, (), ()),
        # Note: phonenumbers matches dotted format as valid TR number
        ("532.123.45.67", 1, ((0, 13),), ((0.05, 1.0),)),
        # False positive: Turkish plate-like
        ("34 ABC 1234", 0, (), ()),
        # Invalid: unused first digits in Turkey (1, 6, 7, 8, 9)
        ("1123456789", 0, (), ()),
        ("6123456789", 0, (), ()),
        ("7123456789", 0, (), ()),
        ("8123456789", 0, (), ()),
        ("9123456789", 0, (), ()),
    ],
)
def test_when_phone_in_text_then_all_phones_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    """Test that Turkish phone number recognizer correctly identifies numbers."""
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len

    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


def test_supported_entity(recognizer):
    """Test that supported entity is correctly set."""
    assert recognizer.supported_entities == ["TR_PHONE_NUMBER"]


def test_supported_language(recognizer):
    """Test that supported language is correctly set."""
    assert recognizer.supported_language == "en"
