import re
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class MacAddressRecognizer(PatternRecognizer):
    """
    Recognize MAC (Media Access Control) address using regex.

    Supports three common MAC address formats:
    - Colon-separated: 00:1A:2B:3C:4D:5E
    - Hyphen-separated: 00-1A-2B-3C-4D-5E
    - Cisco format (dot-separated groups of 4): 0012.3456.789A
    """

    PATTERNS = [
        Pattern(
            "MAC_ADDRESS",
            r"\b([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}\b",
            0.6,
        ),
        Pattern(
            "MAC_CISCO",
            r"\b[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\b",
            0.6,
        ),
    ]

    CONTEXT = ["mac", "mac address", "hardware address", "physical address", "ethernet"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "MAC_ADDRESS",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def invalidate_result(self, pattern_text: str) -> bool:
        """
        Check if the pattern text is a valid MAC address format.

        :param pattern_text: Text detected as pattern by regex
        :return: True if invalidated (invalid MAC address)
        """
        # Remove separators and validate hex characters and length
        cleaned = re.sub(r'[:\-.]', '', pattern_text)

        # MAC address must be exactly 12 hex characters
        if len(cleaned) != 12:
            return True

        # All characters must be valid hex
        if not all(c in '0123456789ABCDEFabcdef' for c in cleaned):
            return True

        # Optionally reject broadcast/multicast addresses if needed
        # Broadcast: FF:FF:FF:FF:FF:FF
        if cleaned.upper() == 'FFFFFFFFFFFF':
            return True

        return False
