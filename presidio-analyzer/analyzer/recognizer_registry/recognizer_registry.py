import logging

from analyzer import PatternRecognizer
from analyzer.predefined_recognizers import CreditCardRecognizer, \
    SpacyRecognizer, CryptoRecognizer, DomainRecognizer, \
    EmailRecognizer, IbanRecognizer, IpRecognizer, NhsRecognizer, \
    UsBankRecognizer, UsLicenseRecognizer, \
    UsItinRecognizer, UsPassportRecognizer, UsPhoneRecognizer, UsSsnRecognizer


class RecognizerRegistry:
    """
    Detects, registers and holds all recognizers to be used by the analyzer
    """

    def __init__(self, recognizers=None):
        if recognizers is None:
            recognizers = []
        self.recognizers = recognizers

    def load_recognizers(self, path):
        #   TODO: Change the code to dynamic loading -
        # Task #598:  Support loading of the pre-defined recognizers
        # from the given path.
        self.recognizers.extend([CreditCardRecognizer(),
                                 SpacyRecognizer(),
                                 CryptoRecognizer(), DomainRecognizer(),
                                 EmailRecognizer(), IbanRecognizer(),
                                 IpRecognizer(), NhsRecognizer(),
                                 UsBankRecognizer(), UsLicenseRecognizer(),
                                 UsItinRecognizer(), UsPassportRecognizer(),
                                 UsPhoneRecognizer(), UsSsnRecognizer()])

    def add_pattern_recognizer_from_dict(self, recognizer_dict):
        """
        Creates a pattern recognizer from a dictionary
         and adds it to the recognizers list
        :param recognizer_dict: A pattern recognizer serialized
         into a dictionary
        """

        pattern_recognizer = PatternRecognizer.from_dict(recognizer_dict)

        for rec in self.recognizers:
            if rec.name == pattern_recognizer.name:
                raise ValueError(
                    "Recognizer of name {} is already defined".format(
                        rec.name))

        self.recognizers.append(pattern_recognizer)

    def remove_recognizer(self, name):
        """
        Removes a recognizer by the given name, from the recognizers list.
        :param name: The recognizer name
        """
        found = False
        for index, rec in enumerate(self.recognizers):
            if rec.name == name:
                found = True
                self.recognizers.pop(index)

        if not found:
            raise ValueError("Requested recognizer was not found")

    def get_recognizers(self, language, entities=None, all_fields=False):
        """
        Returns a list of the recognizer, which supports the specified name and
        language.
        :param entities: the requested entities
        :param language: the requested language
        :param all_fields: a flag to return all fields of the requested language.
        :return: A list of the recognizers which supports the supplied entities
        and language
        """
        if language is None:
            raise ValueError("No language provided")

        if entities is None and all_fields is False:
            raise ValueError("No entities provided")

        to_return = []
        if all_fields:
            to_return = [rec for rec in self.recognizers if
                         language == rec.supported_language]
        else:
            for entity in entities:
                subset = [rec for rec in self.recognizers if
                          entity in rec.supported_entities
                          and language == rec.supported_language]

                if len(subset) == 0:
                    logging.warning(
                        "Entity " + entity +
                        " doesn't have the corresponding recognizer in language :"
                        + language)
                else:
                    to_return.extend(subset)

        if len(to_return) == 0:
            raise ValueError(
                "No matching recognizers were found to serve the request.")

        return to_return

