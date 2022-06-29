import logging
from typing import Optional, Dict

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span

from presidio_analyzer.nlp_engine import SpacyNlpEngine


try:
    import transformers
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        pipeline,
    )
except ImportError:
    transformers = None

logger = logging.getLogger("presidio-analyzer")


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
        Span.set_extension("confidence_score", default=1.0, force=True)
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
            span._.confidence_score = d["score"]
            ents.append(span)
        doc.ents = ents
        return doc


class SpacyTransformerNlpEngine(SpacyNlpEngine):
    """
    SpacyTransformersNlpEngine is a transformers based NlpEngine.
    It comprises a spacy pipeline used for tokenization,
    lemmatization, pos, and a transformers component for NER.
    Both the underlying spacy pipeline and the transformers engine could be
    configured by the user.
    :param models: a dictionary containing the model names per language.
    Example:
    {
        "lang_code": "en",
        "model_name": {
             "spacy": "en_core_web_sm",
             "transformers": "dslim/bert-base-NER"
         }
     }
    Note that since the spaCy model is not used for NER,
    we recommend using a simple model, such as en_core_web_sm for English.
    For potential Transformers models, see a list of models here:
    https://huggingface.co/models?pipeline_tag=token-classification
    It is further recommended to fine-tune these models 
    to the specific scenario in hand.
    """

    engine_name = "transformers"
    is_available = bool(spacy) and bool(transformers)

    def __init__(self, models: Optional[Dict[str, Dict[str, str]]] = None):
        if not models:
            models = {
                "en": {"spacy": "en_core_web_sm", "transformers": "dslim/bert-base-NER"}
            }
        # chack that model dict includes the keys: "spacy" and "transformers"
        elif any(
            [
                any([key not in model_dict for key in ("spacy", "transformers")])
                for model_lang, model_dict in models.items()
            ]
        ):
            logger.error("'model_name' must contains 'spacy' and 'transformers' keys")
            raise KeyError(
                "Expected keys ('spacy' and 'transformers') was not found in model_name dict"
            )

        # TODO: add defaults and input validation
        logger.debug(f"Loading SpaCy models: {models.values()}")

        self.nlp = {}
        for lang_code, model_name in models.items():
            nlp = spacy.load(model_name["spacy"], disable=["parser", "ner"])
            nlp.add_pipe(
                "transformers",
                config={"pretrained_model_name_or_path": model_name["transformers"]},
                last=True,
            )
            self.nlp[lang_code] = nlp
