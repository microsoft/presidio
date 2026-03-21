"""
Tests for DeBsnrRecognizer (Betriebsstättennummer / BSNR).

Format: 9 digits — 2-digit KV regional code + 7 sequential digits assigned
by the KV.  No public checksum; detection relies on context words to reach
useful confidence.

Legal basis: § 75 Abs. 7 SGB V; KBV-Richtlinie zur Vergabe der Arzt-,
Betriebsstätten-, Praxisnetz- sowie Netzverbundnummern.

Fictitious example BSNRs:
  021234568  – KV Hamburg (prefix 02)
  061789045  – KV Nordrhein (prefix 06)
  141234567  – KV Berlin (prefix 14)
"""
import pytest

from presidio_analyzer.predefined_recognizers import DeBsnrRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeBsnrRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_BSNR"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # 9-digit numbers are matched (no validate_result – pattern-only)
        ("021234568", 1),
        ("061789045", 1),
        ("141234567", 1),
        # In running text
        ("Betriebsstättennummer: 021234568", 1),
        ("BSNR 141234567 der Praxis.", 1),
        # Too short (8 digits) – word boundary prevents match
        ("02123456",  0),
        # Too long (10 digits) – word boundary prevents match
        ("0212345689", 0),
        # Non-numeric
        ("02123456A", 0),
        # fmt: on
    ],
)
def test_when_all_de_bsnr_numbers_then_succeed(
    text, expected_len, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
