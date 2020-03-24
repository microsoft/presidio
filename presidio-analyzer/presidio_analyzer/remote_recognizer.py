from presidio_analyzer import EntityRecognizer

# pylint: disable=abstract-method, unused-argument
# User Sroty: #498: Adding a new external recognizer


class RemoteRecognizer(EntityRecognizer):
    """
    A configuration for a recognizer that runs on a different process
     / remote machine
    """

    def __init__(self, supported_entities, supported_language, name=None, version=None,
                 **kwargs):
        super().__init__(supported_entities=supported_entities,
                         supported_language=supported_language,
                         name=name, version=version)

    def load(self):
        pass

    def get_supported_entities(self):
        pass
