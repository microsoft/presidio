from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer, \
    UsPhoneRecognizer, DomainRecognizer


class RecognizerRegistryMock(RecognizerRegistry):
    """
    A mock that acts as a recognizers registry
    """

    def load_recognizers(self, path):
        self.recognizers.extend(
            [CreditCardRecognizer(), UsPhoneRecognizer(), DomainRecognizer()]
        )
