from analyzer import EntityRecognizer


class LocalRecognizer(EntityRecognizer):

    def __init__(self, **kwargs):
        super().__init__(supported_entities=kwargs.get("supported_entities"),
                         supported_language=kwargs.get("supported_language"),
                         name=kwargs.get("name"),
                         version=kwargs.get("version"))
