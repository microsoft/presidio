from analyzer import EntityRecognizer


class LocalRecognizer(EntityRecognizer):

    def __init__(self, supported_entities, supported_language, name, version,
                 **kwargs):
        super().__init__(supported_entities, supported_language, name, version)
