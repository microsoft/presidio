import datetime
from abc import abstractmethod

from analyzer import LocalRecognizer
from analyzer import Pattern
from analyzer import RecognizerResult

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re


class PatternRecognizer(LocalRecognizer):

    def __init__(self, supported_entities, supported_language='en', patterns=None,
                 black_list=None, context=None, version="0.0.1"):
        """
            :param patterns: the list of patterns to detect
            :param black_list: the list of words to detect
            :param context: list of context words
        """
        if supported_entities and len(supported_entities) > 1:
            raise ValueError("Pattern recognizer supports only one entity")

        if not patterns and not black_list:
            raise ValueError("Pattern recognizer should be initialized with patterns or with black list")

        super().__init__(supported_entities=supported_entities, supported_language=supported_language, version=version)
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

    def analyze(self, text, entities):
        results = []

        if len(self.patterns) > 0:
            pattern_result = self.__analyze_patterns(text)

            if pattern_result:
                results.extend(pattern_result)

        return results

    @staticmethod
    def __black_list_to_regex(black_list):
        """
        Converts a list of word to a matching regex, to be analyzed by the regex engine as a part of the
        analyze logic

        :param black_list: the list of words to detect
        :return:the regex of the words for detection
        """
        regex = r"(?:^|(?<= ))(" + '|'.join(black_list) + r")(?:(?= )|$)"
        return Pattern(name="black_list", pattern=regex, strength=1.0)

    @abstractmethod
    def validate_result(self, pattern_text, pattern_result):
        """
        Validates the pattern logic, for example for running checksum on a detected pattern.

        :param pattern_text: the text to validated. Only the part in text that was detected by the regex engine
        :param pattern_result: The output of a specific pattern detector that needs to be validated
        :return: the updated result of the pattern. For example,
        if a validation logic increased or decreased the score that was given by a regex pattern.
        """
        return pattern_result

    def __analyze_patterns(self, text):
        """
        Evaluates all patterns in the provided text, including words in the provided blacklist

        :param text: text to analyze
        :return: A list of RecognizerResult
        """
        results = []
        for pattern in self.patterns:
            match_start_time = datetime.datetime.now()
            matches = re.finditer(
                pattern.pattern,
                text,
                flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
            match_time = datetime.datetime.now() - match_start_time
            self.logger.debug('--- match_time[{}]: {}.{} seconds'.format(
                pattern.name, match_time.seconds, match_time.microseconds))

            for match in matches:
                start, end = match.span()
                current_match = text[start:end]

                # Skip empty results
                if current_match == '':
                    continue

                res = RecognizerResult(start, end, pattern.strength, self.supported_entities[0])
                res = self.validate_result(current_match, res)

                if res:
                    results.append(res)
                

        return results

    def to_dict(self):
        return __dict__

    @classmethod
    def from_dict(cls, data):
        patterns = data.get("patterns")
        patterns_list = []

        if patterns:
            for p in patterns:
                patterns_list.append(Pattern(name=p.get('name'),
                                             strength=p.get('strength'), pattern=p.get('pattern')))

        return cls(supported_entities=data.get('supported_entities'),
                   supported_language=data.get('supported_language'),
                   patterns=patterns_list,
                   black_list=data.get("black_list"),
                   context=data.get("context"),
                   version=data.get("version"))
