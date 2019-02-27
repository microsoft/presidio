
from analyzer.pattern import Pattern
from analyzer.pattern_recognizer import PatternRecognizer


class CustomRecognizer(PatternRecognizer):
    """
    A genereic regex based, pattern recognizer, initiated to hold customer
    custom regonizers which are uploaded using a dedicated API
    """

    def __init__(self, name, patterns, entity, language, black_list,
                 context=[]):
        patterns_list = []
        for pat in patterns:
            patterns_list.extend([Pattern(pat.name, pat.regex, pat.score)])
        super().__init__(name=name, supported_entity=entity,
                         patterns=patterns_list,
                         context=context, supported_language=language,
                         black_list=black_list)
