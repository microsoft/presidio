from presidio_analyzer import RecognizerRegistry
from presidio_analyzer.predefined_recognizers import (
    CreditCardRecognizer,
    PhoneRecognizer,
    UrlRecognizer,
)


class RecognizerRegistryMock(RecognizerRegistry):
    """
    A mock that acts as a recognizers registry
    """

    def load_predefined_recognizers(self, languages=None, nlp_engine=None):
        self.recognizers.extend(
            [CreditCardRecognizer(), PhoneRecognizer(), UrlRecognizer()]
        )
