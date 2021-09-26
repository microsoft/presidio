from typing import List, Optional

import phonenumbers
from phonenumbers.geocoder import country_name_for_number

from presidio_analyzer import (
    RecognizerResult,
    LocalRecognizer,
    AnalysisExplanation,
    EntityRecognizer,
)
from presidio_analyzer.nlp_engine import NlpArtifacts


class PhoneRecognizer(LocalRecognizer):
    """Recognize multi-regional phone numbers.

     Using python-phonenumbers, along with fixed and regional context words.
    :param context: Base context words for enhancing the assurance scores.
    :param supported_language: Language this recognizer supports
    :param supported_regions: The regions for phone number matching and validation
    """

    SCORE = 0.4
    CONTEXT = ["phone", "number", "telephone", "cell", "cellphone", "mobile", "call"]
    DEFAULT_SUPPORTED_REGIONS = ("US", "UK", "DE", "FE", "IL", "IN", "CA", "BR")

    def __init__(
        self,
        context: Optional[List[str]] = CONTEXT,
        supported_language: str = "en",
        # For all regions, use phonenumbers.SUPPORTED_REGIONS
        supported_regions=DEFAULT_SUPPORTED_REGIONS,
    ):
        self.context = context
        self.supported_regions = supported_regions
        super().__init__(
            supported_entities=self.get_supported_entities(),
            supported_language=supported_language,
        )

    def load(self) -> None:  # noqa D102
        pass

    def get_supported_entities(self):  # noqa D102
        return ["PHONE_NUMBER"]

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """Analyzes text to detect phone numbers using python-phonenumbers.

        Iterates over entities, fetching regions, then matching regional
        phone numbers patterns against the text.
        :param text: Text to be analyzed
        :param entities: Entities this recognizer can detect
        :param nlp_artifacts: Additional metadata from the NLP engine
        :return: List of phone numbers RecognizerResults
        """
        results = []
        for region in self.supported_regions:
            for match in phonenumbers.PhoneNumberMatcher(text, region, leniency=1):
                results += [
                    self._get_recognizer_result(match, text, region, nlp_artifacts)
                ]

        return EntityRecognizer.remove_duplicates(results)

    def _get_recognizer_result(self, match, text, region, nlp_artifacts):
        number = match.number
        result = RecognizerResult(
            entity_type="PHONE_NUMBER",
            start=match.start,
            end=match.end,
            score=self.SCORE,
            analysis_explanation=self._get_analysis_explanation(region),
        )

        # Enhance confidence using 'phone' related context and region code and name.
        return self.enhance_using_context(
            text,
            [result],
            nlp_artifacts,
            self._get_region_specific_context(number, region),
        )[0]

    def _get_region_specific_context(self, number, region):
        country_name = country_name_for_number(number, self.supported_language)
        country_name_in_words = country_name.lower().split(" ")
        return self.context + country_name_in_words + [region.lower()]

    def _get_analysis_explanation(self, region):
        return AnalysisExplanation(
            recognizer=PhoneRecognizer.__class__.__name__,
            original_score=self.SCORE,
            textual_explanation=f"Recognized as {region} region phone number, "
            f"using PhoneRecognizer",
        )
