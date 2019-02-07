from analyzer import PatternRecognizer, RemoteRecognizer
from analyzer.predefined_recognizers import CreditCardRecognizer, SpacyRecognizer, CryptoRecognizer, DomainRecognizer, EmailRecognizer, IbanRecognizer, IpRecognizer, NhsRecognizer, UsBankRecognizer, UsLicenseRecognizer, UsItinRecognizer, UsPassportRecognizer, UsPhoneRecognizer, UsSsnRecognizer


class RecognizerRegistry:
    """
    Detects, registers and holds all recognizers to be used by the analyzer
    """

    def __init__(self, recognizers=None):
        if recognizers is None:
            recognizers = []
        self.recognizers = recognizers

    def load_recognizers(self, path):
        #   TODO: Change the code to dynamic loading
        self.recognizers.extend([CreditCardRecognizer(), SpacyRecognizer(), CryptoRecognizer(), DomainRecognizer(),
                             EmailRecognizer(), IbanRecognizer(), IpRecognizer(), NhsRecognizer(),
                             UsBankRecognizer(), UsLicenseRecognizer(), UsItinRecognizer(), UsPassportRecognizer(),
                             UsPhoneRecognizer(), UsSsnRecognizer()])

    def get_recognizers(self, language=None, entities=None):
        if language is None and entities is None:
            return self.recognizers

        if language is None:
            raise ValueError("No language provided")

        if entities is None:
            raise ValueError("No entities provided")

        to_return = []
        for entity in entities:
            subset = [rec for rec in self.recognizers if
                      entity in rec.supported_entities and language in rec.supported_languages]
            to_return.extend(subset)

        # remove duplicates
        return to_return

    def get_all_supported_languages(self):
        supported_languages = []
        for recognizer in self.recognizers:
            for lang in recognizer.supported_languages:
                if lang not in supported_languages:
                    supported_languages.append(lang)

        return supported_languages
