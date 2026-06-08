"""
Philippines License Plate Recognizer for Microsoft Presidio
============================================================
Detects Philippine vehicle license plate numbers in unstructured text.

Plate formats covered
---------------------
1. Private / standard  : ABC 1234   (3 letters + space + 4 digits)  – LTO format since 2013
2. Old / legacy        : AB 1234    (2 letters + space + 4 digits)   – pre-2013 private plates
3. Motorcycle          : 1234 ABC   (4 digits  + space + 3 letters)  – current motorcycle format
4. Conduction sticker  : C 12 D 123 (alphanumeric, no strict letter/digit split) – handled by
                         a looser pattern at lower confidence
5. Separator variants  : dash ( - ) or no separator accepted in addition to a space

Confidence scores
-----------------
- 0.85  Strong match  : modern 3-letter / 4-digit format WITH context word nearby
- 0.75  Strong match  : modern 3-letter / 4-digit format, no context
- 0.60  Moderate      : legacy 2-letter / motorcycle / conduction formats with context
- 0.40  Weak          : legacy / conduction formats without context
"""

import re
import logging
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class PhLicensePlateRecognizer(PatternRecognizer):
    """
    Recognizer for Philippine vehicle license plate numbers.

    Inherits from PatternRecognizer, which provides the standard
    Presidio regex-matching pipeline including context-aware score
    enhancement via LemmaContextAwareEnhancer.
    """

    # ------------------------------------------------------------------ #
    # Regex patterns                                                       #
    # ------------------------------------------------------------------ #

    # Modern private plate  e.g. "ABC 1234", "ABC-1234", "ABC1234"
    PATTERN_MODERN = Pattern(
        name="ph_plate_modern",
        regex=r"\b([A-Z]{3})[\s\-]?(\d{4})\b",
        score=0.75,
    )

    # Motorcycle plate  e.g. "1234 ABC", "1234-ABC", "1234ABC"
    PATTERN_MOTORCYCLE = Pattern(
        name="ph_plate_motorcycle",
        regex=r"\b(\d{4})[\s\-]?([A-Z]{3})\b",
        score=0.60,
    )

    # Legacy private plate  e.g. "AB 1234", "AB-1234"
    PATTERN_LEGACY = Pattern(
        name="ph_plate_legacy",
        regex=r"\b([A-Z]{2})[\s\-](\d{4})\b",
        score=0.50,
    )

    # Conduction sticker  e.g. "C1234D56" – used before official plates are issued
    PATTERN_CONDUCTION = Pattern(
        name="ph_plate_conduction",
        regex=r"\b([A-Z]\d{2}[A-Z]\d{3,4})\b",
        score=0.40,
    )

    # ------------------------------------------------------------------ #
    # Context words                                                        #
    # ------------------------------------------------------------------ #

    CONTEXT = [
        # English
        "plate",
        "license",
        "licence",
        "registration",
        "vehicle",
        "car",
        "truck",
        "motorcycle",
        "motorbike",
        "mv",          # motor vehicle
        "lto",         # Land Transportation Office
        "conduction",
        "sticker",
        # Filipino / Tagalog
        "plaka",       # plate (Tagalog)
        "sasakyan",    # vehicle
        "rehistro",    # registration
        "kotse",       # car
        "trak",        # truck
        "motorsiklo",  # motorcycle
    ]

    SUPPORTED_ENTITY = "PH_LICENSE_PLATE"
    SUPPORTED_LANGUAGE = "en"

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = SUPPORTED_LANGUAGE,
        supported_entity: str = SUPPORTED_ENTITY,
    ):
        patterns = patterns or [
            self.PATTERN_MODERN,
            self.PATTERN_MOTORCYCLE,
            self.PATTERN_LEGACY,
            self.PATTERN_CONDUCTION,
        ]
        context = context or self.CONTEXT

        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            global_regex_flags=re.MULTILINE | re.DOTALL,
        )

    # ------------------------------------------------------------------ #
    # Optional: post-processing / invalidation logic                       #
    # ------------------------------------------------------------------ #

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Additional validation applied after a regex match.

        Returns:
            True  – definitely valid (score kept / boosted)
            False – definitely invalid (result invalidated)
            None  – uncertain (score unchanged)
        """
        upper = pattern_text.upper().replace(" ", "").replace("-", "")

        # Reject all-digit or all-letter strings that slipped through
        if upper.isdigit() or upper.isalpha():
            return False

        # Reject known non-plate patterns (e.g. hex colour codes, ISBNs)
        if re.fullmatch(r"[A-F0-9]{6}", upper):
            return False

        return None  # let the base class / context enhancer decide


# --------------------------------------------------------------------------- #
# Quick smoke-test  (run:  python ph_license_plate_recognizer.py)             #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    samples = [
        # Modern plates
        "The vehicle with plate ABC 1234 was seen near EDSA.",
        "Plate number: XYZ-5678",
        "Nakita ang kotse na may plaka na DEF 9012.",          # Tagalog
        # Motorcycle
        "The motorcycle 4567 GHI cut through traffic.",
        # Legacy
        "Old plate PQ 3456 still on the road.",
        # Conduction
        "Conduction sticker C12D345 was affixed to the windshield.",
        # Should NOT match
        "My ZIP code is 90210.",
        "The HTML color is #FF5733.",
    ]

    registry = RecognizerRegistry()
    registry.add_recognizer(PhLicensePlateRecognizer())

    engine = AnalyzerEngine(registry=registry)

    print(f"{'TEXT':<60} {'ENTITY':<20} {'SCORE':<6} {'MATCH'}")
    print("-" * 110)
    for text in samples:
        results = engine.analyze(text=text, language="en",
                                 entities=[PhLicensePlateRecognizer.SUPPORTED_ENTITY])
        if results:
            for r in results:
                matched = text[r.start:r.end]
                print(f"{text:<60} {r.entity_type:<20} {r.score:<6.2f} '{matched}'")
        else:
            print(f"{text:<60} {'(no match)':<20}")
