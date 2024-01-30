import datetime
import logging
from typing import List, Dict
from regex import Match

import regex as re

from presidio_analyzer import (
    LocalRecognizer,
    Pattern,
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
    ImprovablePattern,
)

from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class ImprovablePatternRecognizer(LocalRecognizer):
    """
    PII entity recognizer using regular expressions or deny-lists.
    Analysis explanations can be improved by a pattern or by the recognizer.

    :param patterns: A list of patterns to detect
    :param deny_list: A list of words to detect,
    in case our recognizer uses a predefined list of words (deny list)
    :param context: list of context words
    :param deny_list_score: confidence score for a term
    identified using a deny-list
    """

    def __init__(
        self,
        supported_entity: str,
        name: str = None,
        supported_language: str = "en",
        patterns: List[ImprovablePattern] = None,
        deny_list: List[str] = None,
        context: List[str] = None,
        deny_list_score: float = 1.0,
        version: str = "0.0.1",
    ):

        if not supported_entity:
            raise ValueError("Pattern recognizer should be initialized with entity")

        if not patterns and not deny_list:
            raise ValueError(
                "Pattern recognizer should be initialized with patterns"
                " or with deny list"
            )

        super().__init__(
            supported_entities=[supported_entity],
            supported_language=supported_language,
            name=name,
            version=version,
        )
        if patterns is None:
            self.patterns = []
        else:
            self.patterns = patterns
        self.context = context
        self.deny_list_score = deny_list_score

        if deny_list:
            deny_list_pattern = self._deny_list_to_regex(deny_list)
            self.patterns.append(deny_list_pattern)
            self.deny_list = deny_list
        else:
            self.deny_list = []

    def load(self):  # noqa D102
        pass

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: NlpArtifacts = None,
        regex_flags: int = None,
    ) -> List[RecognizerResult]:
        """
        Analyzes text to detect PII using regular expressions or deny-lists.

        :param text: Text to be analyzed
        :param entities: Entities this recognizer can detect
        :param nlp_artifacts: Output values from the NLP engine
        :param regex_flags:
        :return:
        """
        results = []

        if self.patterns:
            pattern_result = self.__analyze_patterns(text, regex_flags)
            results.extend(pattern_result)

        return results

    def _deny_list_to_regex(self, deny_list: List[str]) -> Pattern:
        """
        Convert a list of words to a matching regex.

        To be analyzed by the analyze method as any other regex patterns.

        :param deny_list: the list of words to detect
        :return:the regex of the words for detection
        """
        # Escape deny list elements as preparation for regex
        escaped_deny_list = [re.escape(element) for element in deny_list]
        regex = r"(?:^|(?<=\W))(" + "|".join(escaped_deny_list) + r")(?:(?=\W)|$)"
        return Pattern(name="deny_list", regex=regex, score=self.deny_list_score)

    @staticmethod
    def build_regex_explanation(
        recognizer_name: str,
        pattern_name: str,
        pattern: str,
        original_score: float,
        validation_result: bool,
    ) -> AnalysisExplanation:
        """
        Construct an explanation for why this entity was detected.

        :param recognizer_name: Name of recognizer detecting the entity
        :param pattern_name: Regex pattern name which detected the entity
        :param pattern: Regex pattern logic
        :param original_score: Score given by the recognizer
        :param validation_result: Whether validation was used and its result
        :return: Analysis explanation
        """
        explanation = AnalysisExplanation(
            recognizer=recognizer_name,
            original_score=original_score,
            pattern_name=pattern_name,
            pattern=pattern,
            validation_result=validation_result,
        )
        return explanation

    def __analyze_patterns(
        self, text: str, flags: int = None
    ) -> List[RecognizerResult]:
        """
        Evaluate all patterns in the provided text.

        Including words in the provided deny-list

        :param text: text to analyze
        :param flags: regex flags
        :return: A list of RecognizerResult
        """
        flags = flags if flags else re.DOTALL | re.MULTILINE
        results = []
        for pattern in self.patterns:
            match_start_time = datetime.datetime.now()
            matches = re.finditer(pattern.regex, text, flags=flags)
            match_time = datetime.datetime.now() - match_start_time
            logger.debug(
                "--- match_time[%s]: %s.%s seconds",
                pattern.name,
                match_time.seconds,
                match_time.microseconds,
            )

            for match in matches:
                start, end = match.span()

                current_match = text[start:end]

                # Skip empty results
                if current_match == "":
                    continue

                description = self.build_regex_explanation(
                    self.name, pattern.name, pattern.regex, pattern.score, False
                )

                pattern.improve_score(current_match, match, description)
                self.improve_score(pattern, current_match, match, description)

                pattern_result = RecognizerResult(
                    entity_type=self.supported_entities[0],
                    start=start,
                    end=end,
                    score=description.score,
                    analysis_explanation=description,
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                    },
                )

                if pattern_result.score > EntityRecognizer.MIN_SCORE:
                    results.append(pattern_result)

                # Update analysis explanation score following validation or invalidation
                description.score = pattern_result.score

        results = EntityRecognizer.remove_duplicates(results)
        return results

    def to_dict(self) -> Dict:
        """Serialize instance into a dictionary."""
        return_dict = super().to_dict()

        return_dict["patterns"] = [pat.to_dict() for pat in self.patterns]
        return_dict["deny_list"] = self.deny_list
        return_dict["context"] = self.context
        return_dict["supported_entity"] = return_dict["supported_entities"][0]
        del return_dict["supported_entities"]

        return return_dict

    @classmethod
    def from_dict(cls, entity_recognizer_dict: Dict) -> "ImprovablePatternRecognizer":
        """Create instance from a serialized dict."""
        patterns = entity_recognizer_dict.get("patterns")
        if patterns:
            patterns_list = [Pattern.from_dict(pat) for pat in patterns]
            entity_recognizer_dict["patterns"] = patterns_list

        return cls(**entity_recognizer_dict)

    def improve_score(
        self,
        pattern: ImprovablePattern,
        matched_text: str,
        match: Match,
        analysis_explanation: AnalysisExplanation,
    ):
        """
        Logic to improve the recognizer score.

        Override this method if is needed an improvement
        of the score at recognizer level. It will be applied
        to all patterns.

        :param pattern: the pattern that matched.
        :param pattern_text: the text matched.
        :param match: the regex match info.
        :param analysis_explanation: the analysis explanation that should improved.
        Modify the score and explanation.
        """
        pass
