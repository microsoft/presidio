import logging
from mimetypes import init
from typing import Optional, Dict

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngine

import transformers
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

@Language.factory("transformers", default_config={"pretrained_model_name_or_path": "dslim/bert-base-NER"})
def create_transformer_component(nlp, name, pretrained_model_name_or_path: str):
    return TransformerComponent(pretrained_model_name_or_path=pretrained_model_name_or_path)


class TransformerComponent:
    def __init__(self, pretrained_model_name_or_path: str) -> None:
        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path)
        model = AutoModelForTokenClassification.from_pretrained(pretrained_model_name_or_path)
        self.nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    
    def __call__(self, doc: Doc) -> Doc:
        res = self.nlp(doc.text)
        ents = []
        for d in res:
            span = doc.char_span(d['start'], d['end'], label=d['entity_group'])
            ents.append(span)
        doc.ents = ents
        return doc


logger = logging.getLogger("presidio-analyzer")


class SpacyTransformerNlpEngine(NlpEngine):
    """
    SpacyNlpEngine is an abstraction layer over the nlp module.

    It provides processing functionality as well as other queries
    on tokens.
    The SpacyNlpEngine uses SpaCy as its NLP module
    """

    engine_name = "transformers"
    is_available = bool(spacy) and bool(transformers)

    def __init__(self, models: Optional[Dict[str, str]] = None):
        """
        Initialize a wrapper on spaCy functionality.

        :param models: Dictionary with the name of the spaCy model per language.
        For example: models = {"en": "en_core_web_lg"}
        """
        if not models:
            models = {"en": "en_core_web_sm"}
        logger.debug(f"Loading SpaCy models: {models.values()}")

        self.nlp = {}
        for lang_code, model_name in models.items():
            nlp = spacy.load(model_name, disable=["parser", "ner"])
            component = nlp.add_pipe("transformers", config={"pretrained_model_name_or_path": "dslim/bert-base-NER"}, last=True)
            self.nlp[lang_code] = nlp

    def process_text(self, text: str, language: str) -> NlpArtifacts:
        """Execute the SpaCy NLP pipeline on the given text and language."""
        doc = self.nlp[language](text)
        return self._doc_to_nlp_artifact(doc, language)

    def is_stopword(self, word: str, language: str) -> bool:
        """
        Return true if the given word is a stop word.

        (within the given language)
        """
        return self.nlp[language].vocab[word].is_stop

    def is_punct(self, word: str, language: str) -> bool:
        """
        Return true if the given word is a punctuation word.

        (within the given language).
        """
        return self.nlp[language].vocab[word].is_punct

    def get_nlp(self, language: str) -> Language:
        """
        Return the language model loaded for a language.

        :param language: Name of language
        :return: Language model from spaCy
        """
        return self.nlp[language]

    def _doc_to_nlp_artifact(self, doc: Doc, language: str) -> NlpArtifacts:
        lemmas = [token.lemma_ for token in doc]
        tokens_indices = [token.idx for token in doc]
        entities = doc.ents
        return NlpArtifacts(
            entities=entities,
            tokens=doc,
            tokens_indices=tokens_indices,
            lemmas=lemmas,
            nlp_engine=self,
            language=language,
        )
