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

    # pylint: disable=unused-argument
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

    def get_recognizers(self, entities=None, language=None):
        """
        Returns a list of the recognizer, which supports the specified name and
        language. if no language and entities are given, all the available
        recognizers will be returned
        :param entities: the requested entities
        :param language: the requested language
        :return: A list of the recognizers which supports the supplied entities
        and language
        """
        if language is None and entities is None:
            return self.recognizers

        if language is None:
            raise ValueError("No language provided")

        if entities is None:
            raise ValueError("No entities provided")

        to_return = []
        for entity in entities:
            subset = [rec for rec in self.recognizers if
                      entity in rec.supported_entities
                      and language == rec.supported_language]

            if not subset:
                logging.warning(
                    "Entity " + entity +
                    " doesn't have the corresponding recognizer in language :"
                    + language)
            else:
                to_return.extend(subset)

        if not to_return:
            raise ValueError(
                "No matching recognizers were found to serve the request.")

        return to_return
