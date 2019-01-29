from entity_recognizer import EntityRecognizer 



class LocalRecognizer(EntityRecognizer):


    def __init__(self, entity_name, patterns, context, language, version):
        self.entity_name = entity_name
        self.patterns = patterns
        self.context = context
        self.language = language
        self.version = version


    def load(self):
        pass

    def analyze_text(self, text, entities):
        pass
    
    def get_supported_entities(self):
        pass

      
