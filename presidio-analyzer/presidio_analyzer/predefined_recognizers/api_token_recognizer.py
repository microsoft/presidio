from typing import List, Optional
from presidio_analyzer import Pattern, PatternRecognizer
import unittest

class APIKeyRecognizer(PatternRecognizer):
    """
    Recognizes API Keys using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "API Key",
            (
                r"\b(?i)([A-Za-z0-9]{20,40}|[A-Za-z0-9]{6}-[A-Za-z0-9]{6}-[A-Za-z0-9]{6})\b"
            ),
            0.2 # low confidence
        ),
    ]
    CONTEXT = ["api", "api key", "token", "secret", "access key", "access_token"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "API_KEY",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def analyze(self, text: str) -> List:
        """
        Analyze function for API key recognition.

        :param text: Text to analyze
        :return: List of recognition results
        """
        return super().analyze(text)


class TestAPIKeyRecognizer(unittest.TestCase):

    def setUp(self):
        self.recognizer = APIKeyRecognizer()

    def test_recognizer_exists(self):
        self.assertIsNotNone(self.recognizer)

    def test_pattern_exists(self):
        self.assertTrue(len(self.recognizer.PATTERNS) > 0)

    def test_pattern_attributes(self):
        for pattern in self.recognizer.PATTERNS:
            self.assertIsInstance(pattern, Pattern)
            self.assertIsNotNone(pattern.name)
            self.assertIsNotNone(pattern.regex)
            self.assertIsNotNone(pattern.score)

    def test_context(self):
        self.assertTrue(len(self.recognizer.CONTEXT) > 0)

    def test_recognize_api_key(self):
        text_with_api_key = "Here is my API key: w9aKPvHhu1zeD4Tb65G2rQfXNlYU0WJc" # Fake Token
        results = self.recognizer.analyze(text_with_api_key)
        self.assertTrue(len(results) > 0)
        for result in results:
            self.assertEqual(result.entity_type, "API_KEY")


if __name__ == '__main__':
    unittest.main()
