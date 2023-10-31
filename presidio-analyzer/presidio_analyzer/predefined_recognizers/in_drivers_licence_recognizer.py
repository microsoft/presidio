from typing import Optional, List, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class InDriverLicenceRecognizer(PatternRecognizer):
    """
    An Indian driving license Number is a composite key. so your registered driver profile unique universally, not just in India, but universally. Let me explain how.

    It has total 15 characters. Consider following example Eg : MH1420110062821

    Breakdown

    MH -13 - 2011 - 0062821

    First two digits- State Name

    => MH Maharashtra, GJ Gujrat etc etc

    Next two digits - Motor Vehicle Authority branch code

    => MH12 for pune, MH14 for PCMC area even if they are in same city

    Next four digits - License issued year

    Last seven digits - Driver Profile ID

    => the one on your application form.

    The profile ID is unique in the particular branch only. Thats because, as of 2011 the ID was exactly the same number on the application form. Which means, the number may get repeated in some other state.
    """

    
    PATTERNS = [
        Pattern(
            "Indian Driver's License (High)",
            r"\b((?i:AN|AP|AR|AS|BR|CG|CH|DD|DL|GA|GJ|HP|HR|JH|JK|KA|KL|LA|LD|MH|ML|MN|MP|MZ|NL|OD|PB|PY|RJ|SK|TN|TR|TS|UK|UP|WB)\d{2}|(\d{2}[a-zA-Z])(?:19|20)\d{2}\d{7})\b",
            0.8,
        ),
        Pattern(
            "Indian Driver's License (Medium)",
            r"\b([A-Z]{2}\d{2}|(\d{2}[a-zA-Z])\d{11})\b",
            0.6,
        ),
        Pattern(
            "Indian Driver's License (Low)",
            r"\b([A-Za-z]{2}\d{13})\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "driver's license",
        "driving license",
        "license",
        "permit",
        "driver's permit",
        "driving permit",
        "driving credentials",
        "vehicle license",
        "driving ID",
    ]



    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_DRIVING_LICENSE",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
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
        )
