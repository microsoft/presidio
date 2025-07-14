import ipaddress
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class IpRecognizer(PatternRecognizer):
    """
    Recognize IP address using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "IPv4",
            r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "IPv6",
            r"\b[0-9a-fA-F:]+\b",
            0.6,
        ),
        Pattern(
            "IPv6_loopback",
            r"(?<![0-9a-fA-F:])::(?![0-9a-fA-F:])",
            0.1,
        ),
    ]

    CONTEXT = ["ip", "ipv4", "ipv6"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IP_ADDRESS",
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
        Check if the pattern text cannot be validated as an IP address.

        :param pattern_text: Text detected as pattern by regex
        :return: True if invalidated
        """
        try:
            ipaddress.ip_address(pattern_text)
        except ValueError:
            return True

    def analyze(self, text: str, entities: List[str], nlp_artifacts=None):
        """
        Analyze text to find IP addresses, with special handling for IPv6 addresses
        to prefer longer valid matches over shorter ones.
        """
        results = super().analyze(text, entities, nlp_artifacts)
        
        # Check for IPv6 addresses that might have been matched partially
        # and try to extend them to find the longest valid IPv6 match
        improved_results = []
        
        for result in results:
            matched_text = text[result.start:result.end]
            
            # If this looks like an IPv6 with :, try to extend it
            if ":" in matched_text and result.end < len(text):
                # Try to find a longer valid IPv6 starting from the same position
                longest_end = result.end
                
                # Extend character by character to find the longest valid IPv6
                for end_pos in range(result.end + 1, len(text) + 1):
                    candidate = text[result.start:end_pos]
                    try:
                        ipaddress.ip_address(candidate)
                        longest_end = end_pos
                    except ValueError:
                        # Stop extending when we hit an invalid IP
                        break
                
                # Update the result if we found a longer valid match
                if longest_end > result.end:
                    result.end = longest_end
            
            improved_results.append(result)
        
        return improved_results
