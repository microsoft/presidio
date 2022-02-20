import logging
import string
from typing import Tuple, List, Dict, Optional

import regex as re

from presidio_analyzer import (
    Pattern,
    PatternRecognizer,
    RecognizerResult,
    EntityRecognizer,
)
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer.predefined_recognizers.iban_patterns import (
    regex_per_country,
    BOS,
    EOS,
)

logger = logging.getLogger("presidio-analyzer")


class IbanRecognizer(PatternRecognizer):
    """
    Recognize IBAN code using regex and checksum.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param exact_match: Whether patterns should be exactly matched or not
    :param bos_eos: Tuple of strings for beginning of string (BOS)
    and end of string (EOS)
    :param regex_flags: Regex flags options
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "IBAN Generic",
            r"\b([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30})((?:[ \-]?[A-Z0-9]{3,5}){2})"  # noqa
            r"([ \-]?[A-Z0-9]{3,5})?([ \-]?[A-Z0-9]{3,5})?([ \-]?[A-Z0-9]{3,5})?([ \-]?[A-Z0-9]{3,5})?([ \-]?[A-Z0-9]{3,5})?"  # noqa
            r"([ \-]?[A-Z0-9]{1,3})?\b",  # noqa
            0.5,
        ),
    ]

    CONTEXT = ["iban", "bank", "transaction"]

    LETTERS: Dict[int, str] = {
        ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)
    }

    def __init__(
        self,
        patterns: List[str] = None,
        context: List[str] = None,
        supported_language: str = "en",
        supported_entity: str = "IBAN_CODE",
        exact_match: bool = False,
        bos_eos: Tuple[str, str] = (BOS, EOS),
        regex_flags: int = re.DOTALL | re.MULTILINE,
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = replacement_pairs or [("-", ""), (" ", "")]
        self.exact_match = exact_match
        self.BOSEOS = bos_eos if exact_match else ()
        self.flags = regex_flags
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str):  # noqa D102
        try:
            pattern_text = self.__sanitize_value(pattern_text, self.replacement_pairs)
            is_valid_checksum = (
                self.__generate_iban_check_digits(pattern_text, self.LETTERS)
                == pattern_text[2:4]
            )
            # score = EntityRecognizer.MIN_SCORE
            result = False
            if is_valid_checksum:
                if self.__is_valid_format(pattern_text, self.BOSEOS):
                    result = True
                elif self.__is_valid_format(pattern_text.upper(), self.BOSEOS):
                    result = None
            return result
        except ValueError:
            logger.error("Failed to validate text %s", pattern_text)
            return False

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: NlpArtifacts = None,
        regex_flags: int = None,
    ) -> List[RecognizerResult]:
        """Analyze IBAN."""
        results = []

        if self.patterns:
            pattern_result = self.__analyze_patterns(text)
            results.extend(pattern_result)

        return results

    def __analyze_patterns(self, text: str, flags: int = None):
        """
        Evaluate all patterns in the provided text.

        Logic includes detecting words in the provided deny list.
        In a sentence we could get a false positive at the end of our regex, were we
        want to find the IBAN but not the false positive at the end of the match.

        i.e. "I want my deposit in DE89370400440532013000 2 days from today."

        :param text: text to analyze
        :param flags: regex flags
        :return: A list of RecognizerResult
        """
        results = []
        for pattern in self.patterns:
            matches = re.finditer(pattern.regex, text, flags=self.flags)

            for match in matches:
                for grp_num in reversed(range(1, len(match.groups()) + 1)):
                    start = match.span(0)[0]
                    end = (
                        match.span(grp_num)[1]
                        if match.span(grp_num)[1] > 0
                        else match.span(0)[1]
                    )
                    current_match = text[start:end]

                    # Skip empty results
                    if current_match == "":
                        continue

                    score = pattern.score

                    validation_result = self.validate_result(current_match)
                    description = PatternRecognizer.build_regex_explanation(
                        self.name, pattern.name, pattern.regex, score, validation_result
                    )
                    pattern_result = RecognizerResult(
                        entity_type=self.supported_entities[0],
                        start=start,
                        end=end,
                        score=score,
                        analysis_explanation=description,
                        recognition_metadata={
                            RecognizerResult.RECOGNIZER_NAME_KEY: self.name
                        },
                    )

                    if validation_result is not None:
                        if validation_result:
                            pattern_result.score = EntityRecognizer.MAX_SCORE
                        else:
                            pattern_result.score = EntityRecognizer.MIN_SCORE

                    if pattern_result.score > EntityRecognizer.MIN_SCORE:
                        results.append(pattern_result)
                        break

        return results

    @staticmethod
    def __number_iban(iban: str, letters: Dict[int, str]) -> str:
        return (iban[4:] + iban[:4]).translate(letters)

    @staticmethod
    def __generate_iban_check_digits(iban: str, letters: Dict[int, str]) -> str:
        transformed_iban = (iban[:2] + "00" + iban[4:]).upper()
        number_iban = IbanRecognizer.__number_iban(transformed_iban, letters)
        return "{:0>2}".format(98 - (int(number_iban) % 97))

    @staticmethod
    def __is_valid_format(
        iban: str,
        bos_eos: Tuple[str, str] = (BOS, EOS),
        flags: int = re.DOTALL | re.MULTILINE,
    ) -> bool:
        country_code = iban[:2]
        if country_code in regex_per_country:
            country_regex = regex_per_country.get(country_code, "")
            if bos_eos and country_regex:
                country_regex = bos_eos[0] + country_regex + bos_eos[1]
            return country_regex and re.match(country_regex, iban, flags=flags)

        return False

    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
