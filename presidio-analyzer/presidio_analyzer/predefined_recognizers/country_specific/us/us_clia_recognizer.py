"""Recognizer for US CLIA (Clinical Laboratory Improvement Amendments) numbers."""

from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class UsCliaRecognizer(PatternRecognizer):
    """Recognize US CLIA (Clinical Laboratory Improvement Amendments) numbers.

    A CLIA number uniquely identifies a clinical laboratory certified under the
    CLIA program administered by CMS (Centers for Medicare & Medicaid Services).
    CLIA numbers appear on lab orders, lab reports, and Medicare claims for
    laboratory services.

    Format: 10 characters, ``NN D NNNNNNN``
    - Positions 1-2: 2-digit state code (numeric)
    - Position 3: literal letter ``D`` (designates "lab")
    - Positions 4-10: 7-digit unique sequence

    Example: ``11D2030122``

    No publicly documented check-digit algorithm exists for CLIA numbers, so
    this recognizer is regex + context only. The base patterns therefore carry
    a low confidence and rely on surrounding context words ("CLIA", "lab",
    "laboratory", "clinical") to reach a meaningful score.

    Reference: https://www.cms.gov/medicare/quality/clinical-laboratory-improvement-amendments

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes
    or spaces.
    """

    COUNTRY_CODE = "us"

    PATTERNS = [
        Pattern(
            "CLIA number (weak)",
            r"\b\d{2}[Dd]\d{7}\b",
            0.1,
        ),
        Pattern(
            "CLIA number with separators (medium)",
            r"\b\d{2}[ -][Dd][ -]\d{7}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "clia",
        "clia number",
        "clia id",
        "lab",
        "laboratory",
        "clinical laboratory",
        "lab id",
        "lab number",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_CLIA",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )

    def invalidate_result(self, pattern_text: str) -> bool:  # noqa: D102
        sanitized_value = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )
        # Defensive: pattern already enforces length, but guard anyway.
        if len(sanitized_value) != 10:
            return True
        # Position 3 must be a 'D' (case-insensitive); already enforced by the
        # regex, but kept as an explicit assertion for the no-separator path.
        if sanitized_value[2].upper() != "D":
            return True
        # Reject degenerate sequences where all 7 trailing digits are identical
        # (e.g., 11D0000000, 11D1111111). These almost certainly represent
        # placeholders rather than real CLIA numbers.
        trailing = sanitized_value[3:]
        if len(set(trailing)) == 1:
            return True
        return False
