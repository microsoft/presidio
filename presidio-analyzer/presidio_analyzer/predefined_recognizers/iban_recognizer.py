import string

from presidio_analyzer.predefined_recognizers.iban_patterns import (
    regex_per_country,
    BOS,
    EOS,
)
from presidio_analyzer import (
    Pattern,
    PatternRecognizer,
    RecognizerResult,
    EntityRecognizer,
)

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re
# https://stackoverflow.com/questions/44656264/iban-regex-design


class IbanRecognizer(PatternRecognizer):
    """
    Recognizes IBAN code using regex and checksum
    """

    PATTERNS = [
        Pattern(
            "IBAN Generic",
            # pylint: disable=line-too-long
            r"\b([A-Z]{2}[ \-]?[0-9]{2})(?=(?:[ \-]?[A-Z0-9]){9,30})((?:[ \-]?[A-Z0-9]{3,5}){2,7})([ \-]?[A-Z0-9]{1,3})?\b", # noqa
            0.5,
        ),
    ]

    CONTEXT = ["iban", "bank", "transaction"]

    LETTERS = {
        ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)
    }

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="IBAN_CODE",
        exact_match=False,
        BOSEOS=(BOS, EOS),
        regex_flags=re.DOTALL | re.MULTILINE,
    ):
        self.exact_match = exact_match
        self.BOSEOS = BOSEOS if exact_match else ()
        self.flags = regex_flags
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text):
        pattern_text = pattern_text.replace(" ", "")
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

    # pylint: disable=unused-argument,arguments-differ
    def analyze(self, text, entities, nlp_artifacts=None):
        results = []

        if self.patterns:
            pattern_result = self.__analyze_patterns(text)

            if pattern_result and self.context:
                # try to improve the results score using the surrounding
                # context words
                enhanced_result = self.enhance_using_context(
                    text, pattern_result, nlp_artifacts, self.context
                )
                results.extend(enhanced_result)
            elif pattern_result:
                results.extend(pattern_result)

        return results

    def __analyze_patterns(self, text):
        """
        Evaluates all patterns in the provided text, including words in
         the provided blacklist

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
                        self.supported_entities[0], start, end, score, description
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
    def __number_iban(iban, letters):
        return (iban[4:] + iban[:4]).translate(letters)

    @staticmethod
    def __generate_iban_check_digits(iban, letters):
        transformed_iban = (iban[:2] + "00" + iban[4:]).upper()
        number_iban = IbanRecognizer.__number_iban(transformed_iban, letters)
        return "{:0>2}".format(98 - (int(number_iban) % 97))

    @staticmethod
    def __is_valid_format(iban, BOSEOS=(BOS, EOS), flags=re.DOTALL | re.MULTILINE):
        country_code = iban[:2]
        if country_code in regex_per_country:
            country_regex = regex_per_country.get(country_code, "")
            if BOSEOS and country_regex:
                country_regex = BOSEOS[0] + country_regex + BOSEOS[1]
            return country_regex and re.match(country_regex, iban, flags=flags)

        return False
