import logging
from typing import Dict, List, Optional

from presidio_analyzer import (
    AnalysisExplanation,
    LocalRecognizer,
    RecognizerResult,
)
from presidio_analyzer.chunkers import BaseTextChunker
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer.nlp_engine import device_detector

try:
    from transformers import pipeline as hf_pipeline
except ImportError:
    hf_pipeline = None

logger = logging.getLogger("presidio-analyzer")

DEFAULT_MEDICAL_ENTITY_MAPPING: Dict[str, str] = {
    "DISEASE_DISORDER": "MEDICAL_DISEASE_DISORDER",
    "MEDICATION": "MEDICAL_MEDICATION",
    "THERAPEUTIC_PROCEDURE": "MEDICAL_THERAPEUTIC_PROCEDURE",
    "CLINICAL_EVENT": "MEDICAL_CLINICAL_EVENT",
    "BIOLOGICAL_ATTRIBUTE": "MEDICAL_BIOLOGICAL_ATTRIBUTE",
    "BIOLOGICAL_STRUCTURE": "MEDICAL_BIOLOGICAL_STRUCTURE",
    "FAMILY_HISTORY": "MEDICAL_FAMILY_HISTORY",
    "HISTORY": "MEDICAL_HISTORY",
}


class MedicalNERRecognizer(LocalRecognizer):
    """Transformer-based medical NER recognizer using HuggingFace pipelines.

    Detects clinical entities such as diseases, medications, and procedures
    using a token-classification model.
    """

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        name: str = "MedicalNERRecognizer",
        supported_language: str = "en",
        version: str = "0.0.1",
        context: Optional[List[str]] = None,
        entity_mapping: Optional[Dict[str, str]] = None,
        model_name: str = "blaze999/Medical-NER",
        score_threshold: float = 0.30,
        text_chunker: Optional[BaseTextChunker] = None,
    ):
        """Transformer-based medical NER recognizer.

        :param supported_entities: List of supported entities for this recognizer.
            If None, all entities in DEFAULT_MEDICAL_ENTITY_MAPPING will be used.
        :param name: Name of the recognizer
        :param supported_language: Language code to use for the recognizer
        :param version: Version of the recognizer
        :param context: N/A for this recognizer
        :param entity_mapping: Custom mapping from model labels to Presidio entity
            types. Cannot be used together with supported_entities.
        :param model_name: The name of the HuggingFace token-classification model
        :param score_threshold: Minimum confidence score to include a prediction
        :param text_chunker: Custom text chunking strategy. If None, uses
            CharacterBasedTextChunker with default settings (chunk_size=250,
            chunk_overlap=50)
        """

        if entity_mapping:
            if supported_entities:
                raise ValueError(
                    "entity_mapping and supported_entities cannot be used together"
                )
            self.model_to_presidio_entity_mapping = entity_mapping
        else:
            if not supported_entities:
                self.model_to_presidio_entity_mapping = (
                    DEFAULT_MEDICAL_ENTITY_MAPPING.copy()
                )
            else:
                self.model_to_presidio_entity_mapping = {
                    entity: entity for entity in supported_entities
                }

        supported_entities = list(set(self.model_to_presidio_entity_mapping.values()))
        self.model_name = model_name
        self.score_threshold = score_threshold

        if text_chunker is not None:
            self.text_chunker = text_chunker
        else:
            from presidio_analyzer.chunkers import CharacterBasedTextChunker

            self.text_chunker = CharacterBasedTextChunker(
                chunk_size=250,
                chunk_overlap=50,
            )

        self.pipeline = None

        super().__init__(
            supported_entities=supported_entities,
            name=name,
            supported_language=supported_language,
            version=version,
            context=context,
        )

    def load(self) -> None:
        """Load the HuggingFace token-classification pipeline."""
        if not hf_pipeline:
            raise ImportError(
                "The transformers package is not installed. "
                "Install it with: pip install presidio-analyzer[medical-ner]"
            )

        device_str = device_detector.get_device()
        device = 0 if device_str == "cuda" else -1

        self.pipeline = hf_pipeline(
            "token-classification",
            model=self.model_name,
            aggregation_strategy="max",
            device=device,
        )

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None,
    ) -> List[RecognizerResult]:
        """Analyze text to identify medical entities.

        :param text: The text to be analyzed
        :param entities: The list of entities this recognizer is requested to return
        :param nlp_artifacts: N/A for this recognizer
        """

        def predict_func(text: str) -> List[RecognizerResult]:
            predictions = self.pipeline(text)

            results = []
            for pred in predictions:
                label = pred["entity_group"]
                score = pred["score"]

                if score < self.score_threshold:
                    continue

                presidio_entity = self.model_to_presidio_entity_mapping.get(
                    label, label
                )

                if entities and presidio_entity not in entities:
                    continue

                analysis_explanation = AnalysisExplanation(
                    recognizer=self.name,
                    original_score=score,
                    textual_explanation=(
                        f"Identified as {presidio_entity} by MedicalNERRecognizer"
                    ),
                )

                results.append(
                    RecognizerResult(
                        entity_type=presidio_entity,
                        start=pred["start"],
                        end=pred["end"],
                        score=score,
                        analysis_explanation=analysis_explanation,
                    )
                )
            return results

        return self.text_chunker.predict_with_chunking(
            text=text,
            predict_func=predict_func,
        )
