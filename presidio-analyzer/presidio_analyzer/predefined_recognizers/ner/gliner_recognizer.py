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
        chunk_size: int = 250,
        chunk_overlap: int = 50,
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
        :param chunk_size: Maximum character length for text chunks.
        Text longer than this will be split into chunks to avoid token truncation.
        Default is 250 characters, matching gliner-spacy implementation.
        :param chunk_overlap: Number of characters to overlap between chunks.
        Overlap helps detect entities at chunk boundaries. Default is 50 characters.


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
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

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

        # For short text, process directly
        if len(text) <= self.chunk_size:
            predictions = self.gliner.predict_entities(
                text=text,
                labels=labels,
                flat_ner=self.flat_ner,
                threshold=self.threshold,
                multi_label=self.multi_label,
            )
        else:
            # Chunk long text and process each chunk
            chunks = self._chunk_text(text)
            predictions = []
            offset = 0

            for chunk in chunks:
                chunk_predictions = self.gliner.predict_entities(
                    text=chunk,
                    labels=labels,
                    flat_ner=self.flat_ner,
                    threshold=self.threshold,
                    multi_label=self.multi_label,
                )
                # Adjust offsets to match original text position
                for pred in chunk_predictions:
                    pred["start"] += offset
                    pred["end"] += offset

                predictions.extend(chunk_predictions)
                offset += len(chunk) - self.chunk_overlap

            # Remove duplicate entities from overlapping chunks
            predictions = self._deduplicate_predictions(predictions)

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

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks at word boundaries.

        Based on gliner-spacy chunking strategy with overlap to catch entities
        at chunk boundaries:
        https://github.com/theirstory/gliner-spacy/blob/main/gliner_spacy/pipeline.py#L60-L96

        :param text: The full text to chunk
        :return: List of overlapping text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            # Calculate end position
            end = (
                start + self.chunk_size if start + self.chunk_size < len(text) else len(text)
            )

            # Ensure the chunk ends at a complete word
            while end < len(text) and text[end] not in [" ", "\n"]:
                end += 1

            chunks.append(text[start:end])
            
            # Move start position with overlap (stop if we've covered all text)
            if end >= len(text):
                break
            start = end - self.chunk_overlap

        return chunks

    def _deduplicate_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Remove duplicate entities from overlapping chunks.

        Two entities are considered duplicates if they overlap significantly.
        Keeps the entity with the highest score.

        :param predictions: List of entity predictions with start, end, label, score
        :return: Deduplicated list of predictions
        """
        if not predictions:
            return predictions

        # Sort by score descending to keep highest scoring entities
        sorted_preds = sorted(predictions, key=lambda p: p["score"], reverse=True)
        unique = []

        for pred in sorted_preds:
            # Check if this prediction overlaps significantly with any kept prediction
            is_duplicate = False
            for kept in unique:
                # Check if same entity type and overlapping positions
                if pred["label"] == kept["label"]:
                    overlap_start = max(pred["start"], kept["start"])
                    overlap_end = min(pred["end"], kept["end"])

                    if overlap_start < overlap_end:
                        # Calculate overlap ratio
                        overlap_len = overlap_end - overlap_start
                        pred_len = pred["end"] - pred["start"]
                        kept_len = kept["end"] - kept["start"]

                        # If >50% overlap, consider duplicate
                        if overlap_len / min(pred_len, kept_len) > 0.5:
                            is_duplicate = True
                            break

            if not is_duplicate:
                unique.append(pred)

        # Sort by position for consistent output
        return sorted(unique, key=lambda p: p["start"])

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
