import logging
from typing import Optional, Dict

import spacy
from spacy.tokens import Doc, SpanGroup

try:
    import spacy_huggingface_pipelines
    import transformers
except ImportError:
    spacy_huggingface_pipelines = None
    transformers = None

from presidio_analyzer.nlp_engine import (
    SpacyNlpEngine,
    NlpArtifacts,
    NerModelConfiguration,
)

logger = logging.getLogger("presidio-analyzer")


class TransformersNlpEngine(SpacyNlpEngine):
    """

    TransformersNlpEngine is a transformers based NlpEngine.

    It comprises a spacy pipeline used for tokenization,
    lemmatization, pos, and a transformers component for NER.

    Both the underlying spacy pipeline and the transformers engine could be
    configured by the user.
    :param models: A dict holding the model's configuration.
    :example:
    [{"lang_code": "en", "model_name": {
            "spacy": "en_core_web_sm",
            "transformers": "dslim/bert-base-NER"
            }
    }]
    :param ner_model_configuration: Parameters for the NER model.
    See conf/transformers.yaml for an example


    Note that since the spaCy model is not used for NER,
    we recommend using a simple model, such as en_core_web_sm for English.
    For potential Transformers models, see a list of models here:
    https://huggingface.co/models?pipeline_tag=token-classification
    It is further recommended to fine-tune these models
    to the specific scenario in hand.

    """

    engine_name = "transformers"
    is_available = bool(spacy_huggingface_pipelines)

    def __init__(
        self,
        models: Optional[Dict] = None,
        ner_model_configuration: Optional[NerModelConfiguration] = None,
    ):
        if not models:
            models = [
                {
                    "lang_code": "en",
                    "model_name": {
                        "spacy": "en_core_web_sm",
                        "transformers": "obi/deid_roberta_i2b2",
                    },
                }
            ]
        super().__init__(models=models, ner_model_configuration=ner_model_configuration)
        self.entity_key = "bert-base-ner"

    def load(self) -> None:
        """Load the spaCy and transformers models."""

        logger.debug(f"Loading SpaCy and transformers models: {self.models}")
        self.nlp = {}

        for model in self.models:
            self._validate_model_params(model)
            spacy_model = model["model_name"]["spacy"]
            transformers_model = model["model_name"]["transformers"]
            self._download_spacy_model_if_needed(spacy_model)

            nlp = spacy.load(spacy_model, disable=["parser", "ner"])
            nlp.add_pipe(
                "hf_token_pipe",
                config={
                    "model": transformers_model,
                    "annotate": "spans",
                    "stride": self.ner_model_configuration.stride,
                    "alignment_mode": self.ner_model_configuration.alignment_mode,
                    "aggregation_strategy": self.ner_model_configuration.aggregation_strategy,  # noqa E501
                    "annotate_spans_key": self.entity_key,
                },
            )
            self.nlp[model["lang_code"]] = nlp

    @staticmethod
    def _validate_model_params(model: Dict) -> None:
        if "lang_code" not in model:
            raise ValueError("lang_code is missing from model configuration")
        if "model_name" not in model:
            raise ValueError("model_name is missing from model configuration")
        if not isinstance(model["model_name"], dict):
            raise ValueError("model_name must be a dictionary")
        if "spacy" not in model["model_name"]:
            raise ValueError("spacy model name is missing from model configuration")
        if "transformers" not in model["model_name"]:
            raise ValueError(
                "transformers model name is missing from model configuration"
            )

    def process_text(self, text: str, language: str) -> NlpArtifacts:
        """Execute the SpaCy NLP pipeline on the given text and language."""
        if not self.nlp:
            raise ValueError("NLP engine is not loaded. Consider calling .load()")

        doc = self.nlp[language](text)
        return self._doc_to_nlp_artifact(doc, language)

    def _get_entities(self, doc: Doc) -> SpanGroup:
        """
        Get an updated list of entities based on the ner model configuration.

        Remove entities that are in labels_to_ignore,
        update entity names based on model_to_presidio_entity_mapping.

        :param doc: Output of a spaCy model
        :return: SpanGroup holding on the entities and confidence scores
        """

        current_ents = doc.spans[self.entity_key]
        current_scores = doc.spans[self.entity_key].attrs["scores"]

        output_spans = SpanGroup(doc, attrs={"scores": []})

        mapping = self.ner_model_configuration.model_to_presidio_entity_mapping
        to_ignore = self.ner_model_configuration.labels_to_ignore
        for i, ent in enumerate(current_ents):
            # Remove model labels in the ignore list
            if ent.label_ in to_ignore:
                continue

            # Update entity label based on mapping
            if ent.label_ in mapping:
                ent.label_ = mapping[ent.label_]
            else:
                logger.warning(
                    f"Entity {ent.label_} is not mapped to a Presidio entity, "
                    f"but keeping anyway"
                )

            # Remove presidio entities in the ignore list
            if ent.label_ in to_ignore:
                continue

            output_spans.append(ent)

            score = current_scores[i]
            # Update score if entity is in low score entity names
            if ent.label_ in self.ner_model_configuration.low_score_entity_names:
                score *= self.ner_model_configuration.low_confidence_score_multiplier

            # Update scores list
            output_spans.attrs["scores"].append(score)

        return output_spans
