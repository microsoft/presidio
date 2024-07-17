from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple
import re

class EUGPSCoordinatesRecognizer(PatternRecognizer):
    """
    Recognizes EU GPS coordinates using regex.
    
    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "EUGPSCoordinates (Medium)",
            r"""\b(?:
                # Latitude (DD format)
                (([1-8]?\d|90)(\.\d+)?)°\s?[N]
                |
                # Latitude (DMS format)
                (([1-8]?\d|90)°\s?[0-5]?\d'\s?[0-5]?\d(?:\.\d+)?"\s?[N])
                |
                # Longitude (DD format)
                (([1-9]?\d|1[0-7]\d|180)(\.\d+)?)°\s?[E]
                |
                # Longitude (DMS format)
                (([1-9]?\d|1[0-7]\d|180)°\s?[0-5]?\d'\s?[0-5]?\d(?:\.\d+)?"\s?[E]
                )
                )
                \b""",
            0.5,
        ),
    ]

    CONTEXT = [
        "near",
        "around",
        "located at",
        "position",
        "coordinates of",
        "latitude",
        "longitude",
        "site",
        "area",
        "GPS",
        "position",
        "map",
        "route",
        "navigation",
        "waypoint",
        "tracking",
        "Google Maps",
        "GPS device",
        "smartphone",
        "satnav",
        "navigation system",
        "geo-tagged",
        "geolocation",
        "field study",
        "research location",
        "survey coordinates",
        "geographical survey",
        "conservation area",
        "national park",
        "reserve",
        "habitat"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "EU_GPS_COORDINATES",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        regex_flags = re.IGNORECASE | re.MULTILINE
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
            global_regex_flags=regex_flags
        )