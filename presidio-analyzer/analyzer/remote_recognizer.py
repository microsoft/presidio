from analyzer import EntityRecognizer


class RemoteRecognizer(EntityRecognizer):

    def __init__(self, **kwargs):
        super().__init__(supported_entities=kwargs.get("supported_entities"),
                         supported_languages=kwargs.get("supported_languages"),
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
        return __dict__

    @classmethod
    def from_dict(cls, data):
        cls(**data)
