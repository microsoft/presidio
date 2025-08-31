import datetime
import logging
from typing import Dict, List, Optional

import regex as re

from presidio_analyzer import (
    AnalysisExplanation,
    EntityRecognizer,
    LocalRecognizer,
    Pattern,
    RecognizerResult,
)
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer.context_aware_enhancers.lemma_context_aware_enhancer import (
    LemmaContextAwareEnhancer,
)

logger = logging.getLogger("presidio-analyzer")


class PatternRecognizer(LocalRecognizer):
    def __init__(
        self,
        supported_entity: str,
        name: str = None,
        supported_language: str = "en",
        patterns: List[Pattern] = None,
        deny_list: List[str] = None,
        context: List[str] = None,
        deny_list_score: float = 1.0,
        global_regex_flags: Optional[int] = re.DOTALL | re.MULTILINE | re.IGNORECASE,
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
        self.global_regex_flags = global_regex_flags

        if deny_list:
            deny_list_pattern = self._deny_list_to_regex(deny_list)
            self.patterns.append(deny_list_pattern)
            self.deny_list = deny_list
        else:
            self.deny_list = []

        # context enhancer instance
        self.context_enhancer = LemmaContextAwareEnhancer(
            context_similarity_factor=0.2,
            min_score_with_context_similarity=0.8,
            context_prefix_count=1,
            context_suffix_count=1,
        )

    def load(self):
        pass

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None,
        regex_flags: Optional[int] = None,
    ) -> List[RecognizerResult]:
        results = []

        if self.patterns:
            pattern_result = self.__analyze_patterns(text, regex_flags)
            results.extend(pattern_result)

        # apply context enhancer agar context words diye gaye hain
        if self.context and results:
            for res in results:
                window = text[max(0, res.start - 20): res.end + 20].lower()
                for ctx in self.context:
                    if ctx.lower() in window:
                        res.score = min(1.0, res.score + 0.2)


        return results

    def _deny_list_to_regex(self, deny_list: List[str]) -> Pattern:
        escaped_deny_list = [re.escape(element) for element in deny_list]
        regex = r"(?:^|(?<=\W))(" + "|".join(escaped_deny_list) + r")(?:(?=\W)|$)"
        return Pattern(name="deny_list", regex=regex, score=self.deny_list_score)

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        return None

    def invalidate_result(self, pattern_text: str) -> Optional[bool]:
        return None

    @staticmethod
    def build_regex_explanation(
        recognizer_name: str,
        pattern_name: str,
        pattern: str,
        original_score: float,
        validation_result: bool,
        regex_flags: int,
    ) -> AnalysisExplanation:
        textual_explanation = (
            f"Detected by `{recognizer_name}` using pattern `{pattern_name}`"
        )
        explanation = AnalysisExplanation(
            recognizer=recognizer_name,
            original_score=original_score,
            pattern_name=pattern_name,
            pattern=pattern,
            validation_result=validation_result,
            regex_flags=regex_flags,
            textual_explanation=textual_explanation,
        )
        return explanation

    def __analyze_patterns(
        self, text: str, flags: int = None
    ) -> List[RecognizerResult]:
        flags = flags if flags else self.global_regex_flags
        results = []
        for pattern in self.patterns:
            match_start_time = datetime.datetime.now()

            if not pattern.compiled_regex or pattern.compiled_with_flags != flags:
                pattern.compiled_with_flags = flags
                pattern.compiled_regex = re.compile(pattern.regex, flags=flags)

            matches = pattern.compiled_regex.finditer(text)
            match_time = datetime.datetime.now() - match_start_time
            logger.debug(
                "--- match_time[%s]: %.6f seconds",
                pattern.name,
                match_time.total_seconds(),
            )

            for match in matches:
                start, end = match.span()
                current_match = text[start:end]

                if current_match == "":
                    continue

                score = pattern.score
                validation_result = self.validate_result(current_match)
                description = self.build_regex_explanation(
                    self.name,
                    pattern.name,
                    pattern.regex,
                    score,
                    validation_result,
                    flags,
                )
                pattern_result = RecognizerResult(
                    entity_type=self.supported_entities[0],
                    start=start,
                    end=end,
                    score=score,
                    analysis_explanation=description,
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                    },
                )

                if validation_result is not None:
                    if validation_result:
                        pattern_result.score = EntityRecognizer.MAX_SCORE
                    else:
                        pattern_result.score = EntityRecognizer.MIN_SCORE

                invalidation_result = self.invalidate_result(current_match)
                if invalidation_result is not None and invalidation_result:
                    pattern_result.score = EntityRecognizer.MIN_SCORE

                if pattern_result.score > EntityRecognizer.MIN_SCORE:
                    results.append(pattern_result)

                description.score = pattern_result.score

        results = EntityRecognizer.remove_duplicates(results)
        return results

    def to_dict(self) -> Dict:
        return_dict = super().to_dict()
        return_dict["patterns"] = [pat.to_dict() for pat in self.patterns]
        return_dict["deny_list"] = self.deny_list
        return_dict["context"] = self.context
        return_dict["supported_entity"] = return_dict["supported_entities"][0]
        del return_dict["supported_entities"]
        return return_dict

    @classmethod
    def from_dict(cls, entity_recognizer_dict: Dict) -> "PatternRecognizer":
        patterns = entity_recognizer_dict.get("patterns")
        if patterns:
            patterns_list = [Pattern.from_dict(pat) for pat in patterns]
            entity_recognizer_dict["patterns"] = patterns_list
        return cls(**entity_recognizer_dict)
