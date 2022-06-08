import logging
from typing import Optional, List, Tuple, Set

from presidio_analyzer import (
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        pipeline,
        models,
    )
    from transformers.models.bert.modeling_bert import BertForTokenClassification
except ImportError:
    logger.error("transformers is not installed")



class TransformersRecognizer(EntityRecognizer):
    """
    Wrapper for a transformers model, if needed to be used within Presidio Analyzer.

    :example:
    >from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    >transformers_recognizer = TransformersRecognizer()

    >registry = RecognizerRegistry()
    >registry.add_recognizer(transformers_recognizer)

    >analyzer = AnalyzerEngine(registry=registry)

    >results = analyzer.analyze(
    >    "My name is Christopher and I live in Irbid.",
    >    language="en",
    >    return_decision_process=True,
    >)
    >for result in results:
    >    print(result)
    >    print(result.analysis_explanation)


    """

    ENTITIES = [
        "LOCATION",
        "PERSON",
        "ORGANIZATION",
    ]

    DEFAULT_EXPLANATION = "Identified as {} by transformers's Named Entity Recognition"

    CHECK_LABEL_GROUPS = [
        ({"LOCATION"}, {"LOC"}),
        ({"PERSON"}, {"PER"}),
        ({"ORGANIZATION"}, {"ORG"}),
    ]

    PRESIDIO_EQUIVALENCES = {
        "PER": "PERSON",
        "LOC": "LOCATION",
        "ORG": "ORGANIZATION",
    }

    DEFAULT_MODEL_PATH = "dslim/bert-base-NER"

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        check_label_groups: Optional[Tuple[Set, Set]] = None,
        model: Optional[BertForTokenClassification] = None,
        model_path: Optional[str] = None,
    ):
        if not model and not model_path:
            model_path = self.DEFAULT_MODEL_PATH
            logger.warning(
                f"Both 'model' and 'model_path' arguments are None. Using default model_path={model_path}"
            )
        
        if model and model_path:
            logger.warning(
                f"Both 'model' and 'model_path' arguments were provided. Ignoring the model_path"
            )

        self.check_label_groups = (
            check_label_groups if check_label_groups else self.CHECK_LABEL_GROUPS
        )

        supported_entities = supported_entities if supported_entities else self.ENTITIES
        self.model = (
            model
            if model
            else pipeline(
                "ner",
                model=AutoModelForTokenClassification.from_pretrained(model_path),
                tokenizer=AutoTokenizer.from_pretrained(model_path),
                aggregation_strategy="simple",
            )
        )

        super().__init__(
            supported_entities=supported_entities, name="transformers Analytics",
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

    # Class to use transformers with Presidio as an external recognizer.
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        """
        Analyze text using Text Analytics.

        :param text: The text for analysis.
        :param entities: Not working properly for this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :return: The list of Presidio RecognizerResult constructed from the recognized
            transformers detections.
        """

        results = []
        ner_results = self.model(text)

        # If there are no specific list of entities, we will look for all of it.
        if not entities:
            entities = self.supported_entities

        for entity in entities:
            if entity not in self.supported_entities:
                continue

            for res in ner_results:
                if not self.__check_label(
                    entity, res["entity_group"], self.check_label_groups
                ):
                    continue
                textual_explanation = self.DEFAULT_EXPLANATION.format(
                    res["entity_group"]
                )
                explanation = self.build_transformers_explanation(
                    round(res["score"], 2), textual_explanation
                )
                transformers_result = self._convert_to_recognizer_result(
                    res, explanation
                )

                results.append(transformers_result)

        return results

    def _convert_to_recognizer_result(self, res, explanation) -> RecognizerResult:

        entity_type = self.PRESIDIO_EQUIVALENCES.get(
            res["entity_group"], res["entity_group"]
        )
        transformers_score = round(res["score"], 2)

        transformers_results = RecognizerResult(
            entity_type=entity_type,
            start=res["start"],
            end=res["end"],
            score=transformers_score,
            analysis_explanation=explanation,
        )

        return transformers_results

    def build_transformers_explanation(
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

    @staticmethod
    def __check_label(
        entity: str, label: str, check_label_groups: Tuple[Set, Set]
    ) -> bool:
        return any(
            [entity in egrp and label in lgrp for egrp, lgrp in check_label_groups]
        )


if __name__ == "__main__":

    from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

    transformers_recognizer = (
        TransformersRecognizer()
    )  # This would download a large (~500Mb) model on the first run

    registry = RecognizerRegistry()
    registry.add_recognizer(transformers_recognizer)

    analyzer = AnalyzerEngine(registry=registry)

    results = analyzer.analyze(
        "My name is Christopher and I live in Irbid.",
        language="en",
        return_decision_process=True,
    )
    for result in results:
        print(result)
        print(result.analysis_explanation)
