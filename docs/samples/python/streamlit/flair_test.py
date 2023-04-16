# Import generic wrappers
from transformers import AutoModel, AutoTokenizer


if __name__ == "__main__":

    from flair.data import Sentence
    from flair.models import SequenceTagger

    # load tagger
    tagger = SequenceTagger.load("flair/ner-english-large")

    # make example sentence
    sentence = Sentence("George Washington went to Washington")

    # predict NER tags
    tagger.predict(sentence)

    # print sentence
    print(sentence)

    # print predicted NER spans
    print('The following NER tags are found:')
    # iterate over entities and print
    for entity in sentence.get_spans('ner'):
        print(entity)

