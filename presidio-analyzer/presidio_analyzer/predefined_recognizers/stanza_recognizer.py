from presidio_analyzer.predefined_recognizers import SpacyRecognizer


class StanzaRecognizer(SpacyRecognizer):
    def __init__(self, **kwargs):
        self.DEFAULT_EXPLANATION = self.DEFAULT_EXPLANATION.replace("SpaCy", "Stanza")
        super().__init__(**kwargs)
