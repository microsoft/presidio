import logging
from typing import Optional, List, Iterable

from presidio_analyzer import EntityRecognizer
from presidio_analyzer.predefined_recognizers import (
    NLP_RECOGNIZERS,
    CreditCardRecognizer,
    CryptoRecognizer,
    DomainRecognizer,
    EmailRecognizer,
    IbanRecognizer,
    IpRecognizer,
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
)


class RecognizerRegistry:
    """
    Detects, registers and holds all recognizers to be used by the analyzer
    """

    def __init__(self, recognizers: Optional[Iterable[EntityRecognizer]] = None):
        """
        :param recognizers: An optional list of recognizers that will be
               available in addition to the predefined recognizers and the
               custom recognizers
        """
        if recognizers:
            self.recognizers = recognizers
        else:
            self.recognizers = []

    def load_predefined_recognizers(self, languages=None, nlp_engine="spacy"):

        if not languages:
            languages = ["en"]

        NlpRecognizer = NLP_RECOGNIZERS.get(nlp_engine, SpacyRecognizer)
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
            "es": [EsNifRecognizer, ],
            "ALL": [
                CreditCardRecognizer,
                CryptoRecognizer,
                DomainRecognizer,
                EmailRecognizer,
                IbanRecognizer,
                IpRecognizer,
                NlpRecognizer,
            ],
        }
        for lang in languages:
            lang_recognizers = [rc() for rc in recognizers_map.get(lang, [])]
            self.recognizers.extend(lang_recognizers)
            all_recognizers = [
                rc(supported_language=lang) for rc in recognizers_map.get("ALL", [])
            ]
            self.recognizers.extend(all_recognizers)

    def get_recognizers(
        self,
        language: str,
        entities: Optional[List[str]] = None,
        all_fields: bool = False,
    ):
        """
        Returns a list of the recognizer, which supports the specified name and
        language.
        :param entities: the requested entities
        :param language: the requested language
        :param all_fields: a flag to return all fields of a requested language.
        :return: A list of the recognizers which supports the supplied entities
        and language
        """
        if language is None:
            raise ValueError("No language provided")

        if entities is None and all_fields is False:
            raise ValueError("No entities provided")

        all_possible_recognizers = self.recognizers

        # filter out unwanted recognizers
        to_return = []
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
                    logging.warning(
                        "Entity %s doesn't have the corresponding"
                        " recognizer in language : %s",
                        entity,
                        language,
                    )
                else:
                    to_return.extend(subset)

        logging.info(
            "Returning a total of %s recognizers (predefined + custom)",
            str(len(to_return)),
        )

        if not to_return:
            raise ValueError("No matching recognizers were found to serve the request.")

        return to_return

    def add_recognizer(self, recognizer: EntityRecognizer):
        """
        Adds a new recognizer to the list of recognizers
        :param recognizer: Recognizer to add
        """
        if not isinstance(recognizer, EntityRecognizer):
            raise ValueError("Input is not of type EntityRecognizer")

        self.recognizers.append(recognizer)

    def remove_recognizer(self, recognizer_name: str):
        """
        Remove a recognizer based on its name.
        :param recognizer_name: Name of recognizer to remove
        """
        new_recognizers = [
            rec for rec in self.recognizers if rec.name != recognizer_name
        ]
        logging.info(
            "Removed %s recognizers which had the name %s",
            str(len(self.recognizers) - len(new_recognizers)),
            recognizer_name,
        )
        self.recognizers = new_recognizers
