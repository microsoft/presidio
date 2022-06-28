import logging
from mimetypes import init
from typing import Optional, Dict

import spacy
from spacy.language import Language
from spacy.tokens import Doc

from presidio_analyzer.nlp_engine import SpacyNlpEngine

import transformers
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline


@Language.factory(
    "transformers",
    default_config={"pretrained_model_name_or_path": "dslim/bert-base-NER"},
)
def create_transformer_component(nlp, name, pretrained_model_name_or_path: str):
    return TransformerComponent(
        pretrained_model_name_or_path=pretrained_model_name_or_path
    )


class TransformerComponent:
    def __init__(self, pretrained_model_name_or_path: str) -> None:
        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path)
        model = AutoModelForTokenClassification.from_pretrained(
            pretrained_model_name_or_path
        )
        self.nlp = pipeline(
            "ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple"
        )

    def __call__(self, doc: Doc) -> Doc:
        res = self.nlp(doc.text)
        ents = []
        for d in res:
            span = doc.char_span(d["start"], d["end"], label=d["entity_group"])
            ents.append(span)
        doc.ents = ents
        return doc


logger = logging.getLogger("presidio-analyzer")


class SpacyTransformerNlpEngine(SpacyNlpEngine):
    engine_name = "transformers"
    is_available = bool(spacy) and bool(transformers)

    def __init__(self, models: Optional[Dict[str, str]] = None):
        if not models:
            models = {"en": "en_core_web_sm"}
        logger.debug(f"Loading SpaCy models: {models.values()}")

        self.nlp = {}
        for lang_code, model_name in models.items():
            nlp = spacy.load(model_name, disable=["parser", "ner"])
            component = nlp.add_pipe(
                "transformers",
                config={"pretrained_model_name_or_path": "dslim/bert-base-NER"},
                last=True,
            )
            self.nlp[lang_code] = nlp
