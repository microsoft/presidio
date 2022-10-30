import logging
from typing import Optional, Dict

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span

from presidio_analyzer.nlp_engine import SpacyNlpEngine


try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        pipeline,
    )
except ImportError:
    torch = None
    transformers = None

logger = logging.getLogger("presidio-analyzer")


@Language.factory(
    "transformers",
    default_config={"pretrained_model_name_or_path": "dslim/bert-base-NER"},
)
def create_transformer_component(nlp, name, pretrained_model_name_or_path: str):
    """Spacy Language factory for creating custom component."""
    return TransformersComponent(
        pretrained_model_name_or_path=pretrained_model_name_or_path
    )


class TransformersComponent:
    """
    Custom component to use in spacy pipeline.

    Using HaggingFace transformers pretrained models for entity recognition.
    :param pretrained_model_name_or_path: HaggingFace pretrained_model_name_or_path
    """

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
        """Write transformers results to doc entities."""

        res = self.nlp(doc.text)
        ents = []
        for d in res:
            span = doc.char_span(
                d["start"], d["end"], label=d["entity_group"], alignment_mode="expand"
            )
            if span is not None:
                span._.confidence_score = d["score"]
                ents.append(span)
            else:
                logger.warning(
                    f"Transformers model returned {d} but no valid span was found."
                )
        doc.ents = ents
        return doc


class TransformersNlpEngine(SpacyNlpEngine):
    """

    SpacyTransformersNlpEngine is a transformers based NlpEngine.

    It comprises a spacy pipeline used for tokenization,
    lemmatization, pos, and a transformers component for NER.

    Both the underlying spacy pipeline and the transformers engine could be
    configured by the user.

    :param models: a dictionary containing the model names per language.
    :example:
    {
        "en": {
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
        # default models if not specified
        if not models:
            models = {
                "en": {"spacy": "en_core_web_sm", "transformers": "dslim/bert-base-NER"}
            }
        # validate models type
        elif type(models) is not dict:
            logger.error(f"''models' argument must be dict, not {type(models)}")
            raise KeyError(f"Expected 'models' argument to be dict, not {type(models)}")
        # validate models[model_lang] type is dict for all model_lang
        elif any(
            [type(model_dict) is not dict for model_lang, model_dict in models.items()]
        ):
            # elif type(models["model_name"]) is not dict:
            logger.error(
                "'models.model_name' argument must be dict,"
                f"not {type(models['model_name'])}"
            )
            raise KeyError(
                "Expected 'models.model_name' argument to be dict,"
                f"not {type(models['model_name'])}"
            )
        # chack that model_name dict includes the keys: "spacy" and "transformers"
        elif any(
            [
                any([key not in model_dict for key in ("spacy", "transformers")])
                for model_lang, model_dict in models.items()
            ]
        ):
            logger.error(
                "'models.model_name' must contains 'spacy' and 'transformers' keys"
            )
            raise KeyError(
                "Expected keys ('spacy' and 'transformers') was not found in "
                "models.model_name dict"
            )

        logger.debug(f"Loading SpaCy and transformers models: {models.values()}")

        self.nlp = {}
        for lang_code, model_name in models.items():
            nlp = spacy.load(model_name["spacy"], disable=["parser", "ner"])
            nlp.add_pipe(
                "transformers",
                config={"pretrained_model_name_or_path": model_name["transformers"]},
                last=True,
            )
            self.nlp[lang_code] = nlp
