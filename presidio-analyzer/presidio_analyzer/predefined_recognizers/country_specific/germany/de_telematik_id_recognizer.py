from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeTelematikIdRecognizer(PatternRecognizer):
    """
    Recognize German Telematik-ID using regex.

    The Telematik-ID is a unique electronic identifier in Germany's Telematics
    Infrastructure (TI) for healthcare, used for:
    - Healthcare professionals (eHBA - elektronischer Heilberufsausweis)
    - Patients (Gesundheits-ID since 2026)
    - Healthcare institutions (SMC-B cards)

    Critical for ePA (electronic patient records) and E-Rezept (e-prescriptions).

    Format: [Prefix][Separator][Continuation]
    - Prefix 1-: Healthcare professionals (doctors, nurses, therapists) - LIFELONG
    - Prefix 10-: Patients (Versicherte) - PRIMARY digital patient identifier since 2026
    - Prefix 5-2: Hospital institutions (includes IK-Nummer)
    - Prefix 9: Organization cards issued by gematik
    - Max length: 128 characters
    - Character set: 0-9, A-Z, -, .

    The Gesundheits-ID (prefix 10-) is replacing the physical health card in
    digital contexts and is CRITICAL PII for patient anonymization.

    Legal basis: gemSpec_PKI (gematik specification)
    Issuing authority: Gematik, Chambers (Kammern), KV/KZV

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://wiki.gematik.de/display/DIRSERV/Telematik-ID+Mapping
    PATTERNS = [
        Pattern(
            "Telematik-ID (Healthcare professional or Patient)",
            r"\b(?:1|10)-[A-Z0-9.]{5,125}\b",
            0.4,
        ),
        Pattern(
            "Telematik-ID (Institution - Hospital)",
            r"\b5-2-[A-Z0-9.]{5,125}\b",
            0.3,
        ),
        Pattern(
            "Telematik-ID (with context)",
            r"(?i)(?:telematik-id|gesundheits-id|ehba|smc-b)[\s:]*(?:1|10|5-2|9)-[A-Z0-9.]{5,125}\b",
            0.6,
        ),
    ]

    CONTEXT = [
        "telematik-id",
        "telematikid",
        "gesundheits-id",
        "gesundheitsid",
        "ehba",
        "smc-b",
        "heilberufsausweis",
        "elektronischer heilberufsausweis",
        "health id",
        "patient id",
        "versicherten-id",
        "ti-id",
        "telematics id",
        "e-rezept",
        "epa",
        "elektronische patientenakte",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_TELEMATIK_ID",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [(" ", "")]
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

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate the Telematik-ID format.

        Since there is no standard checksum algorithm and the format is highly
        variable across sectors, we perform basic format validation only.

        :param pattern_text: Text detected as pattern by regex
        :return: False if invalid format, None if format valid
        """
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        # Length validation (max 128 characters per spec)
        if len(pattern_text) > 128:
            return False

        # Must contain valid characters only: 0-9, A-Z, -, .
        import re
        if not re.match(r'^[0-9A-Z.\-]+$', pattern_text):
            return False

        # Must start with valid prefix
        valid_prefixes = ["1-", "10-", "5-2-", "9-", "11-"]
        if not any(pattern_text.startswith(prefix) for prefix in valid_prefixes):
            return False

        # Must have content after prefix (at least 5 chars)
        if len(pattern_text) < 7:  # Prefix (2-4 chars) + separator + min 3 chars
            return False

        # No publicly documented checksum algorithm available
        # Return None to use pattern score with context enhancement
        return None
