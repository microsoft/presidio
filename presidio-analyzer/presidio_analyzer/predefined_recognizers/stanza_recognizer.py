from presidio_analyzer.predefined_recognizers import SpacyRecognizer


class StanzaRecognizer(SpacyRecognizer):
    """
    Recognize entities using the Stanza NLP package.

    See https://stanfordnlp.github.io/stanza/.
    Uses the spaCy-Stanza package (https://github.com/explosion/spacy-stanza) to align
    Stanza's interface with spaCy's
    """

    def __init__(self, **kwargs):  # noqa ANN003
        self.DEFAULT_EXPLANATION = self.DEFAULT_EXPLANATION.replace("Spacy", "Stanza")
        super().__init__(**kwargs)
