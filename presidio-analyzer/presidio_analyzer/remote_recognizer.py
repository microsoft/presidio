from presidio_analyzer import EntityRecognizer

# pylint: disable=abstract-method, unused-argument
# User Sroty: #498: Adding a new external recognizer


class RemoteRecognizer(EntityRecognizer):
    """
    A configuration for a recognizer that runs on a different process
     / remote machine
    """

    def __init__(self, supported_entities, name, supported_language, version,
                 **kwargs):
        super().__init__(supported_entities, name, supported_language, version)

    def load(self):
        pass

    def analyze_text(self, text, entities):
        # add code here to connect to the side car
        pass

    def get_supported_entities(self):
        pass
