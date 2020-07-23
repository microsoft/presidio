class NlpArtifacts():
    """ NlpArtifacts is an abstraction layer over the results of an NLP pipeline
        processing over a given text, it holds attributes such as entities,
        tokens and lemmas which can be used by any recognizer
    """

    # pylint: disable=abstract-method, unused-argument
    def __init__(self, entities, tokens, tokens_indices, lemmas, nlp_engine,
                 language):
        self.entities = entities
        self.tokens = tokens
        self.lemmas = lemmas
        self.tokens_indices = tokens_indices
        self.keywords = self.set_keywords(nlp_engine, lemmas, language)

    @staticmethod
    def set_keywords(nlp_engine, lemmas, language):
        if not nlp_engine:
            return []
        keywords = [k.lower() for k in lemmas if
                    not nlp_engine.is_stopword(k, language) and
                    not nlp_engine.is_punct(k, language) and
                    k != '-PRON-' and
                    k != 'be']

        # best effort, try even further to break tokens into sub tokens,
        # this can result in reducing false negatives
        keywords = [i.split(':') for i in keywords]

        # splitting the list can, if happened, will result in list of lists,
        # we flatten the list
        keywords = \
            [item for sublist in keywords for item in sublist]
        return keywords

    def to_json(self):
        return str(self.__dict__)
