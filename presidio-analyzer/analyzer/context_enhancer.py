import spacy

CONTEXT_SIMILARITY_THRESHOLD = 0.65
CONTEXT_SIMILARITY_FACTOR = 0.35
MIN_SCORE_WITH_CONTEXT_SIMILARITY = 0.6
NER_STRENGTH = 0.85
CONTEXT_PREFIX_COUNT = 5
CONTEXT_SUFFIX_COUNT = 0


class ContextEnhancer:

    def __init__(self):
        # Load spaCy small model
        self.nlp = spacy.load('en_core_web_sm')

    def __context_to_keywords(self, context):
        """Convert context text to relevant keywords

        Args:
           context: words prefix of specified pattern
        """

        nlp_context = self.nlp(context)

        # Remove punctuation, stop words and take lemma form and remove
        # duplicates
        keywords = list(
          filter(
            lambda k: not self.nlp.vocab[k.text].is_stop and not k.is_punct
                      and k.lemma_ != '-PRON-' and k.lemma_ != 'be',  # noqa: E501
            nlp_context))
        keywords = list(set(map(lambda k: k.lemma_.lower(), keywords)))

        return keywords

    def __calculate_context_similarity(self, context, pattern):
        """Context similarity is 1 if there's exact match between a keyword in
           context and any keyword in field.context

        Args:
          context: words prefix of specified pattern
          pattern: current pattern
        """

        context_keywords = self.__context_to_keywords(context)
       
        # TODO: remove after supporting keyphrases (instead of keywords)
        if 'card' in pattern.context:
            pattern.context.remove('card')
        if 'number' in pattern.context:
            pattern.context.remove('number')

        similarity = 0.0
        for context_keyword in context_keywords:
            if context_keyword in pattern.context:
                similarity = 1
                break

        return similarity

    @staticmethod
    def __extract_context(text, start, end):
        """Extract context for a specified match

        Args:
          text: the text to analyze
          start: match start offset
          end: match end offset
        """

        prefix = text[0:start].split()
        suffix = text[end + 1:].split()
        context = ''

        context += ' '.join(
          prefix[max(0,
                     len(prefix) - CONTEXT_PREFIX_COUNT):len(prefix)])
        context += ' '
        context += ' '.join(suffix[0:min(CONTEXT_SUFFIX_COUNT, len(suffix))])

        return context

    def enhance_score(self, text, result):
        """Calculate score of match by context

        Args:
          text: the text to analyze
          result: the current result to evaluate its score

        """

        if result.score == 1.0:
            return result

        score = result.score

        # Add context similarity
        context = ContextEnhancer.__extract_context(text, result.start, result.end)
        context_similarity = self.__calculate_context_similarity(context, result.entity_type)
        if context_similarity >= CONTEXT_SIMILARITY_THRESHOLD:
            score += context_similarity * CONTEXT_SIMILARITY_FACTOR
            score = max(score, MIN_SCORE_WITH_CONTEXT_SIMILARITY)

        result.score = min(score, 1)
        return result
