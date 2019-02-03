import datetime
from abc import abstractmethod

from analyzer import EntityRecognizer
from analyzer import Pattern
from analyzer import RecognizerResult

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re


class PatternRecognizer(EntityRecognizer):

    def __init__(self, supported_entities, supported_languages='en', patterns=None,
                 black_list=None, context=None, version="0.0.1"):
        """
            :param patterns: the list of patterns to detect
            :param black_list: the list of words to detect
            :param context: list of context words
        """
        if supported_entities and len(supported_entities) > 1 and patterns and len(patterns) > 0:
            raise ValueError("Pattern recognizer supports only one entity")

        super().__init__(supported_entities, supported_languages, version)
        if patterns is None:
            self.patterns = []
        else:
            self.patterns = patterns
        self.context = context

        if black_list:
            black_list_pattern = PatternRecognizer.__black_list_to_regex(black_list)
            self.patterns.append(black_list_pattern)

    def load(self):
        pass

    @abstractmethod
    def analyze_text(self, text, entities):
        """
        This is the core method for analyzing text, assuming entities are
        the subset of the supported entities types.

        :param text: The text to be analyzed
        :param entities: The list of entities to be detected
        :return: list of RecognizerResult
        :rtype: [RecognizerResult]
        """
        pass

    def analyze_all(self, text, entities):
        """
        The full recognition logic, calling all patterns + custom analyze_text logic to come up with all detected
        PIIs for this recognizer.
        :param text: the text to analyze
        :param entities: the entities to be detected
        :return: the analyze result- the detected entities and their location in the text
        """
        results = []

        if len(self.patterns) > 0:
            pattern_result = self.__analyze_regex_patterns(text)

            if pattern_result:
                results.extend(pattern_result)

        analyzed_text = self.analyze_text(text, entities)
        if analyzed_text:
            results.extend(analyzed_text)

        return results

    @staticmethod
    def __black_list_to_regex(black_list):
        """
        Converts a list of word to a matching regex, to be analyzed by the regex engine as a part of the
        analyze_all logic

        :param black_list: the list of words to detect
        :return:the regex of the words for detection
        """
        regex = r"(?:^|(?<= ))(" + '|'.join(black_list) + r")(?:(?= )|$)"
        return Pattern("black_list", 1.0, regex)

    def validate_pattern_logic(self, pattern_text, pattern_result):
        """
        Validates the pattern logic, for example for running checksum on a detected pattern.

        :param pattern_text: the text to validated. Only the part in text that was detected by the regex engine
        :param pattern_result: The output of a specific pattern detector that needs to be validated
        :return: the updated result of the pattern. For example,
        if a validation logic increased or decreased the score that was given by a regex pattern.
        """
        return pattern_result

    def __analyze_regex_patterns(self, input_text):
        """
        Evaluates all regex patterns in the provided input_text, including words in the provided blacklist

        :param input_text: text to analyze
        :return: A list of RecognizerResult
        """
        results = []
        for pattern in self.patterns:
            match_start_time = datetime.datetime.now()
            matches = re.finditer(
                pattern.pattern,
                input_text,
                flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
            match_time = datetime.datetime.now() - match_start_time
            self.logger.debug('--- match_time[{}]: {}.{} seconds'.format(
                pattern.name, match_time.seconds, match_time.microseconds))

            for match in matches:
                start, end = match.span()
                current_match = input_text[start:end]

                # Skip empty results
                if current_match == '':
                    continue

                res = RecognizerResult(start, end, pattern.strength, self.supported_entities[0])
                res = self.validate_pattern_logic(current_match, res)

                if res is None or res.score == 0:
                    continue

                results.append(res)

        return results
