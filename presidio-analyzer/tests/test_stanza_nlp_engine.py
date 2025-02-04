""" "Tests taken from the spacy_stanza repo"""

from spacy.lang.en import EnglishDefaults, English
from spacy.lang.de import GermanDefaults
from spacy.lang.es import SpanishDefaults

import stanza
import pytest

from presidio_analyzer.nlp_engine.stanza_nlp_engine import (
    load_pipeline,
    StanzaTokenizer,
)


def tags_equal(act, exp):
    """Check if each actual tag in act is equal to one or more expected tags in exp."""
    return all(a == e if isinstance(e, str) else a in e for a, e in zip(act, exp))


@pytest.mark.skip_engine("stanza_en")
def test_spacy_stanza_english():
    lang = "en"
    stanza.download(lang)
    nlp = load_pipeline(lang)
    assert nlp.Defaults == EnglishDefaults

    doc = nlp("Hello world! This is a test.")

    # Expected POS tags. Note: Different versions of stanza result in different
    # POS tags.
    # fmt: off
    pos_exp = ["INTJ", "NOUN", "PUNCT", ("DET", "PRON"), ("VERB", "AUX"), "DET", "NOUN", "PUNCT"]

    assert [t.text for t in doc] == ["Hello", "world", "!", "This", "is", "a", "test", "."]
    assert [t.lemma_ for t in doc] == ["hello", "world", "!", "this", "be", "a", "test", "."]
    assert tags_equal([t.pos_ for t in doc], pos_exp)

    assert [t.tag_ for t in doc] == ["UH", "NN", ".", "DT", "VBZ", "DT", "NN", '.']
    assert [str(t.morph) for t in doc] == ['', 'Number=Sing', '', 'Number=Sing|PronType=Dem', 'Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin', 'Definite=Ind|PronType=Art', 'Number=Sing', '']
    assert [t.dep_ for t in doc] == ['root', 'vocative', 'punct', 'nsubj', 'cop', 'det', 'root', 'punct']
    assert [t.is_sent_start for t in doc] == [True, False, False, True, False, False, False, False]
    assert any([t.is_stop for t in doc])
    # fmt: on
    assert len(list(doc.sents)) == 2
    assert doc.has_annotation("TAG")
    assert doc.has_annotation("MORPH")
    assert doc.has_annotation("DEP")
    assert doc.has_annotation("SENT_START")

    docs = list(nlp.pipe(["Hello world", "This is a test"]))
    assert docs[0].text == "Hello world"
    assert [t.pos_ for t in docs[0]] == ["INTJ", "NOUN"]
    assert docs[1].text == "This is a test"
    assert tags_equal([t.pos_ for t in docs[1]], pos_exp[3:-1])
    assert doc.ents == tuple()

    # Test NER
    doc = nlp("Barack Obama was born in Hawaii.")
    assert len(doc.ents) == 2
    assert doc.ents[0].text == "Barack Obama"
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[1].text == "Hawaii"
    assert doc.ents[1].label_ == "GPE"

    # Test whitespace alignment
    doc = nlp(" Barack  Obama  was  born\n\nin Hawaii.\n")
    assert [t.pos_ for t in doc] == [
        "SPACE",
        "PROPN",
        "SPACE",
        "PROPN",
        "SPACE",
        "AUX",
        "SPACE",
        "VERB",
        "SPACE",
        "ADP",
        "PROPN",
        "PUNCT",
        "SPACE",
    ]
    assert [t.dep_ for t in doc] == [
        "",
        "nsubj:pass",
        "",
        "flat",
        "",
        "aux:pass",
        "",
        "root",
        "",
        "case",
        "root",
        "punct",
        "",
    ]
    assert [t.head.i for t in doc] == [0, 7, 2, 1, 4, 7, 6, 7, 8, 10, 10, 10, 12]
    assert len(doc.ents) == 2
    assert doc.ents[0].text == "Barack  Obama"
    assert doc.ents[0].label_ == "PERSON"
    assert doc.ents[1].text == "Hawaii"
    assert doc.ents[1].label_ == "GPE"

    # Test trailing whitespace handling
    doc = nlp("a ")
    doc = nlp("a  ")
    doc = nlp("a \n")
    doc = nlp("\n ")
    doc = nlp("\t  ")
    doc = nlp("a\n ")
    doc = nlp("a  \t  ")

    # Test serialization
    reloaded_nlp = load_pipeline(lang).from_bytes(nlp.to_bytes())
    assert reloaded_nlp.config.to_str() == nlp.config.to_str()


@pytest.mark.skip_engine("stanza_en")
def test_spacy_stanza_german():
    lang = "de"
    stanza.download(lang)
    nlp = load_pipeline(lang)
    assert nlp.Defaults == GermanDefaults

    # warning for misaligned ents due to multi-word token expansion
    with pytest.warns(UserWarning):
        doc = nlp("Auf dem Friedhof an der Straße Am Rosengarten")


@pytest.mark.skip_engine("stanza_en")
def test_spacy_stanza_spanish():
    lang = "es"
    stanza.download(lang)
    nlp = load_pipeline(lang)
    snlp = nlp.tokenizer.snlp
    assert nlp.Defaults == SpanishDefaults

    # Example from the training data so that predicted labels are likely correct
    # https://github.com/UniversalDependencies/UD_Spanish-AnCora
    text = "Las reservas en oro se valoran en base a 300 dólares estadounidenses por cada onza troy de oro."
    doc = nlp(text)
    sdoc = snlp(text)

    # In the training data (UD<v2.9), the xpos columns are empty, meaning that
    # xpos = None in stanza. In this case, the pos (upos) should be copied to tag (xpos)
    # UDv2.9 does have xpos tags. So to make sure this test runs successfully, only
    # run it when we know that the original stanza xpos is None (UD<v2.9)
    if all(w.xpos is None for sent in sdoc.sentences for w in sent.words):
        assert (
            [t.pos_ for t in doc]
            == [t.tag_ for t in doc]
            == [
                "DET",
                "NOUN",
                "ADP",
                "NOUN",
                "PRON",
                "VERB",
                "ADP",
                "NOUN",
                "ADP",
                "NUM",
                "NOUN",
                "ADJ",
                "ADP",
                "DET",
                "NOUN",
                "NOUN",
                "ADP",
                "NOUN",
                "PUNCT",
            ]
        )
    else:
        # TODO: update here when new models use UDv2.9 xpos labels
        pass


@pytest.mark.skip_engine("stanza_en")
def test_spacy_stanza_tokenizer_options():
    # whitespace tokens from spacy tokenizer are handled correctly
    lang = "en"
    stanza.download(lang)
    nlp = load_pipeline(lang, processors={"tokenize": "spacy"})

    doc = nlp(" Barack  Obama  was  born\n\nin Hawaii.")
    assert [t.text for t in doc] == [
        " ",
        "Barack",
        " ",
        "Obama",
        " ",
        "was",
        " ",
        "born",
        "\n\n",
        "in",
        "Hawaii",
        ".",
    ]

    # pretokenized text is handled correctly
    nlp = load_pipeline(lang, tokenize_pretokenized=True)
    doc = nlp("Barack Obama was born in Hawaii.\nBarack Obama was born in Hawaii.")
    assert [t.text for t in doc] == [
        "Barack",
        "Obama",
        "was",
        "born",
        "in",
        "Hawaii.",
        "Barack",
        "Obama",
        "was",
        "born",
        "in",
        "Hawaii.",
    ]
    doc = nlp(
        " Barack  Obama  was  born\n\n in Hawaii.\nBarack Obama was born in Hawaii."
    )
    assert [t.text for t in doc] == [
        "Barack",
        "Obama",
        "was",
        "born",
        "in",
        "Hawaii.",
        "Barack",
        "Obama",
        "was",
        "born",
        "in",
        "Hawaii.",
    ]


@pytest.mark.skip_engine("stanza_en")
def test_spacy_stanza_from_config():
    config = {
        "nlp": {
            "tokenizer": {
                "@tokenizers": "PipelineAsTokenizer.v1",
                "lang": "en",
            }
        }
    }
    nlp = English.from_config(config)
    assert nlp.Defaults == EnglishDefaults
    assert type(nlp.tokenizer) == StanzaTokenizer
