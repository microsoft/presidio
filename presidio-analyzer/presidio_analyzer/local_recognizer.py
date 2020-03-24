from presidio_analyzer import EntityRecognizer


class LocalRecognizer(EntityRecognizer):

    # pylint: disable=abstract-method, unused-argument
    def __init__(self, supported_entities, supported_language, name=None,
                 version=None, **kwargs):
        super().__init__(supported_entities=supported_entities,
                         supported_language=supported_language, name=name,
                         version=version)
