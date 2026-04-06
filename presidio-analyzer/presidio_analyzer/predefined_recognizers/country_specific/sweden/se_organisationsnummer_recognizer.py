# -*- coding: utf-8 -*-
"""Swedish Organisationsnummer recognizer."""

from __future__ import annotations

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class SeOrganisationsnummerRecognizer(PatternRecognizer):
    """Recognizes and validates Swedish Organisationsnummer.

    Rules:
    * 10 digits: NNNNNNXXXX (optional hyphen)
    * Third digit >= 2
    * Luhn checksum validation
    """

    PATTERNS = [
        Pattern(
            "Swedish Organisationsnummer (Medium)",
            r"\b\d{6}[-]?\d{4}\b",
            0.6,
        ),
        Pattern(
            "Swedish Organisationsnummer (Weak)",
            r"\d{6}[-]?\d{4}",
            0.2,
        ),
    ]

    CONTEXT = [
        "organisationsnummer",
        "orgnr",
        "org nr",
        "företagsnummer",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "sv",
        supported_entity: str = "SE_ORGANISATIONSNUMMER",
        name: Optional[str] = None,
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT

        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    @staticmethod
    def _numeric_part(orgnr: str) -> str:
        """Extract only digits."""
        return "".join(filter(str.isdigit, orgnr))

    @staticmethod
    def _is_luhn_valid(number: str) -> bool:
        """Validate using Luhn algorithm."""
        digits = [int(d) for d in number]
        checksum = digits[-1]

        luhn_sum = 0
        for i, d in enumerate(reversed(digits[:-1])):
            if i % 2 == 0:
                d *= 2
                if d > 9:
                    d -= 9
            luhn_sum += d

        return (luhn_sum + checksum) % 10 == 0

    @staticmethod
    def _has_valid_third_digit(number: str) -> bool:
        """Third digit must be >= 2."""
        try:
            return int(number[2]) >= 2
        except (ValueError, IndexError):
            return False

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------
    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """Validate Organisationsnummer."""

        num = self._numeric_part(pattern_text)

        if len(num) != 10:
            return False

        # Rule: third digit >= 2
        if not self._has_valid_third_digit(num):
            return False

        # Luhn check
        return self._is_luhn_valid(num)
