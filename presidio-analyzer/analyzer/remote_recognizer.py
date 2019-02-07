from analyzer import EntityRecognizer


class RemoteRecognizer(EntityRecognizer):
    """
    A configuration for a recognizer that runs on a different process / remote machine
    """

    def __init__(self, **kwargs):
        super().__init__(supported_entities=kwargs.get("supported_entities"),
                         supported_language=kwargs.get("supported_language"),
                         name=kwargs.get("name"),
                         version=kwargs.get("version"))
        pass

    def load(self):
        pass

    def analyze_text(self, text, entities):
        # add code here to connect to the side car
        pass

    def get_supported_entities(self):
        pass
