from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeHandelsregisterRecognizer(PatternRecognizer):
    """
    Recognizes German commercial register numbers (Handelsregisternummer).

    The Handelsregisternummer identifies legal entities and sole traders registered
    in the German Handelsregister (commercial register), maintained by local
    Amtsgerichte (district courts). It is divided into two sections:

        - Abteilung A (HRA): Einzelkaufleute (sole traders) and Personengesellschaften
          (partnerships: OHG, KG, GmbH & Co. KG, etc.). For Einzelkaufleute, the HRA
          number directly identifies a natural person, making it personal data under
          DSGVO Art. 4 Nr. 1.

        - Abteilung B (HRB): Kapitalgesellschaften (corporations: GmbH, AG, KGaA,
          UG (haftungsbeschränkt), etc.). Identifies legal entities; not personal data
          unless the entity is a sole shareholder / sole director whose identity is
          directly derivable.

    Legal basis: § 9, § 14 HGB (Handelsgesetzbuch), Handelsregisterverordnung (HRV).
    Data protection: DSGVO Art. 4 Nr. 1 for HRA entries linked to natural persons; BDSG.

    Format:
        HR[AB] [optional space] [1–6 digits]
        Examples: HRA 12345, HRB 123456, HRA12345, HRB 1234 Köln

    The `HR[AB]` prefix makes the pattern highly specific, resulting in low false
    positive rates even without a checksum. No formal accuracy evaluation has been
    performed on a labelled dataset.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Handelsregisternummer HRA/HRB",
            r"\bHR[AB]\s*\d{1,6}\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "handelsregister",
        "handelsregisternummer",
        "amtsgericht",
        "registergericht",
        "hra",
        "hrb",
        "hr-nummer",
        "registerauszug",
        "handelsregistereintrag",
        "firma",
        "gesellschaft",
        "gmbh",
        "ag",
        "ug",
        "kg",
        "ohg",
        "einzelkaufmann",
        "einzelkauffrau",
        "handelsregisterblattnummer",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_HANDELSREGISTER",
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
