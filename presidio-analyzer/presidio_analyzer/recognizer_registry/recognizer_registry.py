import time
import logging

from presidio_analyzer.recognizer_registry import RecognizerStoreApi
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
)


class RecognizerRegistry:
    """
    Detects, registers and holds all recognizers to be used by the analyzer
    """

    def __init__(self, recognizer_store_api=RecognizerStoreApi(), recognizers=None):
        """
        :param recognizer_store_api: An instance of a class that has custom
               recognizers management functionallity (insert, update, get,
               delete). The default store if nothing is else is provided is
               a store that uses a persistent storage
        :param recognizers: An optional list of recognizers that will be
               available in addition to the predefined recognizers and the
               custom recognizers
        """
        if recognizers:
            self.recognizers = recognizers
        else:
            self.recognizers = []

        # loaded_hash is the hash value of the recognizers in the recognizer
        # store. It is used to avoid fetching recognizers when there hasn't
        # been a change to the recognizers state.
        self.loaded_hash = None
        # the loaded_timestamp is used for debugging purposes, so it will be
        # easy to understand when did the last fetching occured
        self.loaded_timestamp = None
        self.loaded_custom_recognizers = []
        self.store_api = recognizer_store_api

    def load_predefined_recognizers(self, languages=None, nlp_engine="spacy"):
        #   TODO: Change the code to dynamic loading -
        # Task #598:  Support loading of the pre-defined recognizers
        # from the given path.
        # Currently this is not integrated into the init method to speed up
        # loading time if these are not actually needed (SpaCy for example) is
        # time consuming to load

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

    def get_recognizers(self, language, entities=None, all_fields=False):
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

        if self.store_api:
            all_possible_recognizers = self.recognizers.copy()
            custom_recognizers = self.get_custom_recognizers()
            all_possible_recognizers.extend(custom_recognizers)
            logging.info("Found %d (total) custom recognizers", len(custom_recognizers))
        else:
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
            "Returning a total of %d recognizers (predefined + custom)", len(to_return)
        )

        if not to_return:
            raise ValueError("No matching recognizers were found to serve the request.")

        return to_return

    def get_custom_recognizers(self):
        """
        Returns a list of custom recognizers retrieved from the store object
        """
        if not self.store_api:
            return []

        if self.loaded_hash is not None:
            logging.info(
                "Analyzer loaded custom recognizers on: %s [hash %s]",
                time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(int(self.loaded_timestamp))
                ),
                self.loaded_hash,
            )
        else:
            logging.info("Analyzer loaded custom recognizers on: Never")

        latest_hash = self.store_api.get_latest_hash()
        # is update time is not set, no custom recognizers in storage, skip
        if latest_hash:
            logging.info("Persistent storage has hash: %s", latest_hash)
            # check if anything updated since last time
            if self.loaded_hash is None or latest_hash != self.loaded_hash:
                self.loaded_timestamp = int(time.time())
                self.loaded_hash = latest_hash

                self.loaded_custom_recognizers = []
                # read all values
                logging.info("Requesting custom recognizers from the storage...")

                raw_recognizers = self.store_api.get_all_recognizers()
                if raw_recognizers is None or not raw_recognizers:
                    logging.info("No custom recognizers found")
                    return []

                logging.info(
                    "Found %d recognizers in the storage", len(raw_recognizers)
                )
                self.loaded_custom_recognizers = raw_recognizers

        return self.loaded_custom_recognizers
