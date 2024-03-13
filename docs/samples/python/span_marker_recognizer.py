import logging
from typing import Optional, List, Dict

from presidio_analyzer import (
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.nlp_engine import NlpArtifacts

try:
    from span_marker import SpanMarkerModel
except ImportError:
    print("Span Marker is not installed")


logger = logging.getLogger("presidio-analyzer")


class SpanMarkerRecognizer(EntityRecognizer):
    """
    Wrapper for a span marker models, if needed to be used within Presidio Analyzer.
    :param supported_language: The language supported by the model,
    default is set to English (en).
    :param model: A string referencing a Span Marker model name or path.
    :param supported_entities: A list of entities supported by Presidio.
    :param presidio_equivalences: Mapping of model-defined entities with
    Presidio-supported entities.
    :param ignore_labels: A list of entities specified by the model that
    should not be extracted.

    :example:
    >from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    >span_marker_recognizer = SpanMarkerRecognizer()

    >registry = RecognizerRegistry()
    >registry.add_recognizer(span_marker_recognizer)

    >analyzer = AnalyzerEngine(registry=registry)

    >results = analyzer.analyze(
    >    "My name is Vijay and I live in Pune.",
    >    language="en",
    >    return_decision_process=True,
    >)
    >for result in results:
    >    print(result)
    >    print(result.analysis_explanation)


    """

    ENTITIES = [
        "PERSON",
        "LOCATION",
        "ORGANIZATION",
        # "MISCELLANEOUS"   # - There are no direct correlation with Presidio entities.
    ]

    DEFAULT_MODEL = "tomaarsen/span-marker-bert-base-fewnerd-fine-super"

    DEFAULT_EXPLANATION = "Identified as {} by Span Marker's Named Entity Recognition"

    PRESIDIO_EQUIVALENCES = {
        "person-other": "PERSON",
        "location-GPE": "LOCATION",
        "organization-company": "ORGANIZATION",
        # 'MISC': 'MISCELLANEOUS'   # - Probably not PII
    }

    IGNORE_LABELS = ["O"]

    def __init__(
        self,
        supported_language: str = "en",
        model: str = None,
        supported_entities: Optional[List[str]] = None,
        presidio_equivalences: Optional[Dict[str, str]] = None,
        ignore_labels: Optional[List[str]] = None,
    ):
        self.model = (
            model
            if model
            else self.DEFAULT_MODEL
        )

        self.presidio_equivalences = (
            presidio_equivalences
            if presidio_equivalences
            else self.PRESIDIO_EQUIVALENCES
        )

        supported_entities = (
            supported_entities if supported_entities else self.ENTITIES
        )

        self.ignore_labels = (
            ignore_labels if ignore_labels else self.IGNORE_LABELS
        )

        labels = list(self.presidio_equivalences.keys())
        self.span_marker_model = SpanMarkerModel.from_pretrained(
            self.model,
            labels=labels
        )

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="Span Marker Analytics",
        )

    def load(self) -> None:
        """Load the model, not used. Model is loaded during initialization."""
        pass

    def get_supported_entities(self) -> List[str]:
        """
        Return supported entities by this model.

        :return: List of the supported entities.
        """
        return self.supported_entities

    # Class to use Span Marker with Presidio as an external recognizer.
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using Text Analytics.

        :param text: The text for analysis.
        :param entities: Not working properly for this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :return: The list of Presidio RecognizerResult constructed from the recognized
            Span Marker detections.
        """

        results = []
        ner_res = self.span_marker_model.predict(text)

        for res in ner_res:
            if not self.__check_label(
                res['label']
            ):
                continue
            textual_explanation = self.DEFAULT_EXPLANATION.format(
                res['label']
            )
            explanation = self.build_span_marker_explanation(
                round(res['score'], 2), textual_explanation
            )
            span_marker_result = self._convert_to_recognizer_result(res, explanation)
            results.append(span_marker_result)

        return results

    def _convert_to_recognizer_result(self, entity, explanation) -> RecognizerResult:

        entity_type = self.presidio_equivalences.get(entity['label'], entity['label'])
        span_marker_score = round(entity['score'], 2)

        span_marker_results = RecognizerResult(
            entity_type=entity_type,
            start=entity['char_start_index'],
            end=entity['char_end_index'],
            score=span_marker_score,
            analysis_explanation=explanation,
        )

        return span_marker_results

    def build_span_marker_explanation(
        self, original_score: float, explanation: str
    ) -> AnalysisExplanation:
        """
        Create explanation for why this result was detected.

        :param original_score: Score given by this recognizer
        :param explanation: Explanation string
        :return:
        """
        explanation = AnalysisExplanation(
            recognizer=self.__class__.__name__,
            original_score=original_score,
            textual_explanation=explanation,
        )
        return explanation

    def __check_label(
        self, label: str
    ) -> bool:
        entity = self.presidio_equivalences.get(label, None)

        if entity in self.ignore_labels:
            return None

        if entity is None:
            logger.warning(f"Found unrecognized label {label}, returning entity as is")
            return label

        if entity not in self.supported_entities:
            logger.warning(f"Found entity {entity} which is not supported by Presidio")
            return entity
        return entity


if __name__ == "__main__":

    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    span_marker_recognizer = (
        SpanMarkerRecognizer()
    )

    registry = RecognizerRegistry()
    registry.add_recognizer(span_marker_recognizer)

    analyzer = AnalyzerEngine(registry=registry)

    results = analyzer.analyze(
        "My name is Vijay and I live in Pune.",
        language="en",
        return_decision_process=True,
    )
    for result in results:
        print(result)
        print(result.analysis_explanation)
