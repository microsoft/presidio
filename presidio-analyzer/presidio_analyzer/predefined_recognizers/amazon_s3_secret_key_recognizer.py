import re
from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class AmazonS3KeyRecognizer(PatternRecognizer):
    """

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """  # noqa: D205

    PATTERNS = [
        Pattern(
            "AmazonS3Key (Medium)",
            r"\b[A-Za-z0-9/+=]{40}\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "secret key",
        "Amazon S3 key",
        "Amazon S3 secret",
        "Amazon secret key",
        "S3 key",
        "S3 secret",

        "secret",
        "key",
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "AMAZON_S3_KEY",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        regex_flags: int = re.IGNORECASE,
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

        # custom attributes
        self.type = 'alphanumeric'
        self.range = (40,40)
