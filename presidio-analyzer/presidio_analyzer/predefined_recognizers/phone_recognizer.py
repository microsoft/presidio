from typing import Optional, List

import phonenumbers
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
from phonenumbers.geocoder import country_name_for_number

from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult, LocalRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts
# from phonenumberutil import COUNTRY_CODE_TO_REGION_CODE, SUPPORTED_REGIONS


ENTITY_TYPE_SUFFIX = "_PHONE_NUMBER"


class PhoneRecognizer(LocalRecognizer):
    """
    Recognize date using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    CONTEXT = ["phone", "number", "telephone", "cell", "cellphone", "mobile", "call"]

    def __init__(
            self,
            supported_language: str = "en",
            supported_entities: List[str] = None,
    ):
        supported_entities = self.get_supported_entities() if not supported_entities else supported_entities
        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
        )

    def load(self) -> None:
        pass

    def get_supported_entities(self):
        return [value[0] + ENTITY_TYPE_SUFFIX for value in COUNTRY_CODE_TO_REGION_CODE.values()]

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
        for entity in entities:
            region = entity.replace(ENTITY_TYPE_SUFFIX, "")
            for match in phonenumbers.PhoneNumberMatcher(text, region, leniency=0):
                number = match.number
                possible_regions = COUNTRY_CODE_TO_REGION_CODE.get(number.country_code)
                main_region = possible_regions[0]
                international = match.raw_string.startswith("+")
                if (international and entity == "INTERNATIONAL_PHONE_NUMBER") or not international:
                    effective_entity_type = entity if entity == "INTERNATIONAL_PHONE_NUMBER" \
                        else main_region + ENTITY_TYPE_SUFFIX
                    result = RecognizerResult(entity_type=effective_entity_type,
                                                 start=match.start,
                                                 end=match.end,
                                                 score=0.6)
                    region_specific_context = self.CONTEXT + [country_name_for_number(number, self.supported_language)]
                    results += [self.enhance_using_context(text, result, nlp_artifacts, region_specific_context)]

        return results

