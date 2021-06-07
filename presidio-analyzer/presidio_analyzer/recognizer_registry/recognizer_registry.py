import copy
import logging
from typing import Optional, List, Iterable, Union, Type

from presidio_analyzer import EntityRecognizer
from presidio_analyzer.nlp_engine import NlpEngine, SpacyNlpEngine, StanzaNlpEngine
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer,
    CryptoRecognizer,
    DateRecognizer,
    DomainRecognizer,
    EmailRecognizer,
    IbanRecognizer,
    IpRecognizer,
    MedicalLicenseRecognizer,
    NhsRecognizer,
    UsBankRecognizer,
    UsLicenseRecognizer,
    UsItinRecognizer,
    UsPassportRecognizer,
    UsPhoneRecognizer,
    UsSsnRecognizer,
    SgFinRecognizer,
    SpacyRecognizer,
    EsNifRecognizer,
    StanzaRecognizer,
)

logger = logging.getLogger("presidio-analyzer")


class RecognizerRegistry:
    """
    Detect, register and hold all recognizers to be used by the analyzer.

    :param recognizers: An optional list of recognizers,
    that will be available instead of the predefined recognizers
    """

    def __init__(self, recognizers: Optional[Iterable[EntityRecognizer]] = None):

        if recognizers:
            self.recognizers = recognizers
        else:
            self.recognizers = []

    def load_predefined_recognizers(
        self, languages: Optional[List[str]] = None, nlp_engine: NlpEngine = None
    ) -> None:
        """
        Load the existing recognizers into memory.

        :param languages: List of languages for which to load recognizers
        :param nlp_engine: The NLP engine to use.
        :return: None
        """
        if not languages:
            languages = ["en"]

        nlp_recognizer = self._get_nlp_recognizer(nlp_engine)
        recognizers_map = {
            "en": [
                UsBankRecognizer,
                UsLicenseRecognizer,
                UsItinRecognizer,
                UsPassportRecognizer,
                UsPhoneRecognizer,
                UsSsnRecognizer,
                NhsRecognizer,
                SgFinRecognizer,
            ],
            "es": [EsNifRecognizer],
            "ALL": [
                CreditCardRecognizer,
                CryptoRecognizer,
                DateRecognizer,
                DomainRecognizer,
                EmailRecognizer,
                IbanRecognizer,
                IpRecognizer,
                MedicalLicenseRecognizer,
                nlp_recognizer,
            ],
        }
        for lang in languages:
            lang_recognizers = [rc() for rc in recognizers_map.get(lang, [])]
            self.recognizers.extend(lang_recognizers)
            all_recognizers = [
                rc(supported_language=lang) for rc in recognizers_map.get("ALL", [])
            ]
            self.recognizers.extend(all_recognizers)

    @staticmethod
    def _get_nlp_recognizer(
        nlp_engine: NlpEngine,
    ) -> Union[Type[SpacyRecognizer], Type[StanzaRecognizer]]:
        """Return the recognizer leveraging the selected NLP Engine."""

        if not nlp_engine or type(nlp_engine) == SpacyNlpEngine:
            return SpacyRecognizer
        if isinstance(nlp_engine, StanzaNlpEngine):
            return StanzaRecognizer
        else:
            logger.warning(
                "nlp engine should be either SpacyNlpEngine or StanzaNlpEngine"
            )
            # Returning default
            return SpacyRecognizer

    def get_recognizers(
        self,
        language: str,
        entities: Optional[List[str]] = None,
        all_fields: bool = False,
        ad_hoc_recognizers: Optional[List[EntityRecognizer]] = None,
    ) -> List[EntityRecognizer]:
        """
        Return a list of recognizers which supports the specified name and language.

        :param entities: the requested entities
        :param language: the requested language
        :param all_fields: a flag to return all fields of a requested language.
        :param ad_hoc_recognizers: Additional recognizers provided by the user
        as part of the request
        :return: A list of the recognizers which supports the supplied entities
        and language
        """
        if language is None:
            raise ValueError("No language provided")

        if entities is None and all_fields is False:
            raise ValueError("No entities provided")

        all_possible_recognizers = copy.copy(self.recognizers)
        if ad_hoc_recognizers:
            all_possible_recognizers.extend(ad_hoc_recognizers)

        # filter out unwanted recognizers
        to_return = set()
        if all_fields:
            to_return = [
                rec
                for rec in all_possible_recognizers
                if language == rec.supported_language
            ]
        else:
            for entity in entities:
                subset = [
                    rec
                    for rec in all_possible_recognizers
                    if entity in rec.supported_entities
                    and language == rec.supported_language
                ]

                if not subset:
                    logger.warning(
                        "Entity %s doesn't have the corresponding"
                        " recognizer in language : %s",
                        entity,
                        language,
                    )
                else:
                    to_return.update(set(subset))

        logger.debug(
            "Returning a total of %s recognizers",
            str(len(to_return)),
        )

        if not to_return:
            raise ValueError("No matching recognizers were found to serve the request.")

        return list(to_return)

    def add_recognizer(self, recognizer: EntityRecognizer) -> None:
        """
        Add a new recognizer to the list of recognizers.

        :param recognizer: Recognizer to add
        """
        if not isinstance(recognizer, EntityRecognizer):
            raise ValueError("Input is not of type EntityRecognizer")

        self.recognizers.append(recognizer)

    def remove_recognizer(self, recognizer_name: str) -> None:
        """
        Remove a recognizer based on its name.

        :param recognizer_name: Name of recognizer to remove
        """
        new_recognizers = [
            rec for rec in self.recognizers if rec.name != recognizer_name
        ]
        logger.info(
            "Removed %s recognizers which had the name %s",
            str(len(self.recognizers) - len(new_recognizers)),
            recognizer_name,
        )
        self.recognizers = new_recognizers
