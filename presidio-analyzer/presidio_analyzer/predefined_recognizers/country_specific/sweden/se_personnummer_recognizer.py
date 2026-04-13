# -*- coding: utf-8 -*-
"""Swedish Personnummer recognizer.

This recognizer mirrors the guard‑rail implementation used in LiteLLM:
* Supports both 6‑digit (YYMMDD) and 8‑digit (YYYYMMDD) date parts.
* Handles optional separator "-" or "+" and samordningsnummer (day >= 61).
* Validates the date component.
* Performs Luhn checksum verification.
"""

from __future__ import annotations

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class SePersonnummerRecognizer(PatternRecognizer):
    """Recognizes and validates Swedish Personal Identity Numbers.

    The recogniser follows the full guard‑rail logic:
    * Regex covers ``YYMMDD[-+]XXXX`` and ``YYYYMMDD[-+]XXXX``.
    * Date validation accommodates samordningsnummer (day ≥ 61).
    * Luhn checksum is applied to the last 10 digits.
    """

    # ---------------------------------------------------------------------
    #  Regular expressions – allow 6‑ or 8‑digit date parts.
    # ---------------------------------------------------------------------
    PATTERNS = [
        Pattern(
            "Swedish Personnummer (Medium)",
            r"\b(\d{6,8})([-+]?)\d{4}\b",
            0.5,
        ),
        Pattern(
            "Swedish Personnummer (Very Weak)",
            r"(\d{6,8})([-+]?)\d{4}",
            0.1,
        ),
    ]
    CONTEXT = [
        "personnummer",
        "svenskt personnummer",
        "svensk id",
        "ssn",
        "personal identity number",
        "samordningsnummer",
    ]

    # ---------------------------------------------------------------------
    #  Initialisation – keep type‑hint safety for ``name``.
    # ---------------------------------------------------------------------
    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "sv",
        supported_entity: str = "SE_PERSONNUMMER",
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

    # ---------------------------------------------------------------------
    #  Helper utilities (static – no instance state required)
    # ---------------------------------------------------------------------
    @staticmethod
    def _numeric_part(pnr: str) -> str:
        """Return the last 10 numeric characters of a person‑nummer string."""
        return "".join(filter(str.isdigit, pnr))[-10:]

    @staticmethod
    def _is_luhn_valid(pnr: str) -> bool:
        """Luhn checksum validation for the 10‑digit number.

        The algorithm doubles every second digit from the right (excluding the
        checksum digit), subtracts 9 if the result exceeds 9, and finally checks
        that the total modulo 10 equals 0.
        """
        digits = [int(d) for d in pnr]
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
    def _has_valid_date(pnr: str) -> bool:
        """Validate month and day, handling samordningsnummer.

        ``pnr`` must be the 10‑digit numeric representation.
        """
        try:
            month = int(pnr[2:4])
            day = int(pnr[4:6])
            # Samordningsnummer uses day + 60
            if day >= 61:
                day -= 60
            return 1 <= month <= 12 and 1 <= day <= 31
        except (ValueError, IndexError):
            return False

    # ---------------------------------------------------------------------
    #  Core validation invoked by Presidio.
    # ---------------------------------------------------------------------
    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """Validate a candidate Personnummer.

        The validation pipeline:
        1 Normalise to the last 10 digits.
        2 Verify the date component (including samordningsnummer handling).
        3 Apply the Luhn checksum.
        """
        num = self._numeric_part(pattern_text)
        if len(num) != 10:
            return False

        if not self._has_valid_date(num):
            return False

        return self._is_luhn_valid(num)
