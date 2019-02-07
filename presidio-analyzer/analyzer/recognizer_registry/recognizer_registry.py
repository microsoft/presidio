import logging
from analyzer.predefined_recognizers import CreditCardRecognizer, SpacyRecognizer, CryptoRecognizer, DomainRecognizer, \
    EmailRecognizer, IbanRecognizer, IpRecognizer, NhsRecognizer, UsBankRecognizer, UsLicenseRecognizer, \
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
        # Task #598:  Support dynamic loading of the pre-defined recognizers
        self.recognizers.extend([CreditCardRecognizer(), SpacyRecognizer(), CryptoRecognizer(), DomainRecognizer(),
                                 EmailRecognizer(), IbanRecognizer(), IpRecognizer(), NhsRecognizer(),
                                 UsBankRecognizer(), UsLicenseRecognizer(), UsItinRecognizer(), UsPassportRecognizer(),
                                 UsPhoneRecognizer(), UsSsnRecognizer()])

    def get_recognizers(self, entities=None, language=None):
        if language is None and entities is None:
            return self.recognizers

        if language is None:
            raise ValueError("No language provided")

        if entities is None:
            raise ValueError("No entities provided")

        to_return = []
        for entity in entities:
            subset = [rec for rec in self.recognizers if
                      entity in rec.supported_entities and language == rec.supported_language]

            if len(subset) == 0:
                logging.warning(
                    "Entity " + entity + " doesn't have the corresponding recognizer in language" + language)
            else:
                to_return.extend(subset)

        for recognizer in to_return:
            # Lazy loading of the relevant recognizers

            if not recognizer.is_loaded:
                recognizer.load()
                recognizer.is_loaded = True

        if len(to_return) == 0:
            raise ValueError("No matching recognizers were found to serve the request.")

        return to_return
