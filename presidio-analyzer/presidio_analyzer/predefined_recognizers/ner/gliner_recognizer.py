import json
import logging
from typing import Dict, List, Optional

from presidio_analyzer import (
    AnalysisExplanation,
    LocalRecognizer,
    RecognizerResult,
)
from presidio_analyzer.nlp_engine import NerModelConfiguration, NlpArtifacts

try:
    from gliner import GLiNER, GLiNERConfig
except ImportError:
    GLiNER = None
    GLiNERConfig = None


logger = logging.getLogger("presidio-analyzer")


class GLiNERRecognizer(LocalRecognizer):
    """GLiNER model based entity recognizer."""

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        name: str = "GLiNERRecognizer",
        supported_language: str = "en",
        version: str = "0.0.1",
        context: Optional[List[str]] = None,
        entity_mapping: Optional[Dict[str, str]] = None,
        model_name: str = "urchade/gliner_multi_pii-v1",
        flat_ner: bool = True,
        multi_label: bool = False,
        threshold: float = 0.30,
        map_location: str = "cpu",
    ):
        """GLiNER model based entity recognizer.

        The model is based on the GLiNER library.

        :param supported_entities: List of supported entities for this recognizer.
        If None, all entities in Presidio's default configuration will be used.
        see `NerModelConfiguration`
        :param name: Name of the recognizer
        :param supported_language: Language code to use for the recognizer
        :param version: Version of the recognizer
        :param context: N/A for this recognizer
        :param model_name: The name of the GLiNER model to load
        :param flat_ner: Whether to use flat NER or not (see GLiNER's documentation)
        :param multi_label: Whether to use multi-label classification or not
        (see GLiNER's documentation)
        :param threshold: The threshold for the model's output
        (see GLiNER's documentation)
        :param map_location: The device to use for the model


        """

        if entity_mapping:
            if supported_entities:
                raise ValueError(
                    "entity_mapping and supported_entities cannot be used together"
                )

            self.model_to_presidio_entity_mapping = entity_mapping
        else:
            if not supported_entities:
                logger.info(
                    "No supported entities provided, "
                    "using default entities from NerModelConfiguration"
                )
                self.model_to_presidio_entity_mapping = (
                    NerModelConfiguration().model_to_presidio_entity_mapping
                )
            else:
                self.model_to_presidio_entity_mapping = {
                    entity: entity for entity in supported_entities
                }

        logger.info("Using entity mapping %s", json.dumps(entity_mapping, indent=2))
        supported_entities = list(set(self.model_to_presidio_entity_mapping.values()))
        self.model_name = model_name
        self.map_location = map_location
        self.flat_ner = flat_ner
        self.multi_label = multi_label
        self.threshold = threshold

        self.gliner = None

        super().__init__(
            supported_entities=supported_entities,
            name=name,
            supported_language=supported_language,
            version=version,
            context=context,
        )

        self.gliner_labels = list(self.model_to_presidio_entity_mapping.keys())

    def load(self) -> None:
        """Load the GLiNER model."""
        if not GLiNER:
            raise ImportError("GLiNER is not installed. Please install it.")
        self.gliner = GLiNER.from_pretrained(self.model_name)

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None,
    ) -> List[RecognizerResult]:
        """Analyze text to identify entities using a GLiNER model.

        :param text: The text to be analyzed
        :param entities: The list of entities this recognizer is requested to return
        :param nlp_artifacts: N/A for this recognizer
        """

        # combine the input labels as this model allows for ad-hoc labels
        labels = self.__create_input_labels(entities)

        predictions = self.gliner.predict_entities(
            text=text,
            labels=labels,
            flat_ner=self.flat_ner,
            threshold=self.threshold,
            multi_label=self.multi_label,
        )
        recognizer_results = []
        for prediction in predictions:
            presidio_entity = self.model_to_presidio_entity_mapping.get(
                prediction["label"], prediction["label"]
            )
            if entities and presidio_entity not in entities:
                continue

            analysis_explanation = AnalysisExplanation(
                recognizer=self.name,
                original_score=prediction["score"],
                textual_explanation=f"Identified as {presidio_entity} by GLiNER",
            )

            recognizer_results.append(
                RecognizerResult(
                    entity_type=presidio_entity,
                    start=prediction["start"],
                    end=prediction["end"],
                    score=prediction["score"],
                    analysis_explanation=analysis_explanation,
                )
            )

        return recognizer_results

    def __create_input_labels(self, entities):
        """Append the entities requested by the user to the list of labels if it's not there."""  # noqa: E501
        labels = self.gliner_labels
        for entity in entities:
            if (
                entity not in self.model_to_presidio_entity_mapping.values()
                and entity not in self.gliner_labels
            ):
                labels.append(entity)
        return labels
