from analyzer import PatternRecognizer, RemoteRecognizer


class RecognizerRegistry:
    """
    Detects, registers and holds all recognizers to be used by the analyzer
    """

    def __init__(self, recognizers=None, ):
        if recognizers is None:
            recognizers = []
        self.recognizers = recognizers

    def load_pattern_recognizer(self, data):
        """
        Load pattern recognizer from json file
        :param data: a dictionary (possibly created from a json) which holds the parameters of a recognizer
        """
        self.recognizers.append(PatternRecognizer.from_dict(data))

    def load_external_recognizer(self, data):
        '''
        Load external recognizer (in separate container) from json metadata file
        :param data: a dictionary (possibly created from a json) which holds the parameters of a recognizer
        '''
        self.recognizers.append(RemoteRecognizer.from_dict(data))

    def load_local_recognizer(self, path_to_recognizers):
        '''
        Load local recognizer (in python file)
        '''
        pass

    def get_recognizers(self, languages=None, entities=None):
        if languages is None and entities is None:
            return self.recognizers

        if languages is None:
            raise ValueError("No languages provided")

        if entities is None:
            raise ValueError("No entities provided")

        to_return = []
        for language in languages:
            for entity in entities:
                subset = [rec for rec in self.recognizers if
                          entity in rec.supported_entities and language in rec.supported_languages]
                to_return.extend(subset)

        # remove duplicates
        return to_return

    def get_all_recognizers(self):
        return self.recognizers
