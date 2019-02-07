from analyzer import EntityRecognizer


class RemoteRecognizer(EntityRecognizer):

    def __init__(self, **kwargs):
        super().__init__(supported_entities=kwargs.get("supported_entities"),
                         supported_language=kwargs.get("supported_language"),
                         version=kwargs.get("version"))
        pass

    def load(self):
        pass

    def analyze_text(self, text, entities):
        # add code here to connect to the side car
        pass

    def get_supported_entities(self):
        pass

    def to_dict(self):
        return_dict = super().to_dict()

        return return_dict

    @classmethod
    def from_dict(cls, entity_recognizer_dict):
        return cls(**entity_recognizer_dict)
