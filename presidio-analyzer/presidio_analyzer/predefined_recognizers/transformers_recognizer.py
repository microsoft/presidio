from typing import Tuple, Set
import logging
from presidio_analyzer.predefined_recognizers.spacy_recognizer import SpacyRecognizer
from presidio_analyzer import RecognizerResult

logger = logging.getLogger("presidio-analyzer")


class TransformersRecognizer(SpacyRecognizer):
    """
    Recognize entities using the transformers package.

    The recognizer doesn't run transformers models,
    but loads the output from the NlpArtifacts
    See https://huggingface.co/docs/transformers/main/en/index
    Uses the transformers package
    (https://huggingface.co/docs/transformers/main/en/installation) to align
    transformers interface with spaCy
    """

    def __init__(self, **kwargs):  # noqa ANN003
        self.DEFAULT_EXPLANATION = self.DEFAULT_EXPLANATION.replace(
            "Spacy", "Transfromers"
        )
        super().__init__(**kwargs)

    def analyze(self, text, entities, nlp_artifacts=None):  # noqa D102
        results = []
        if not nlp_artifacts:
            logger.warning("Skipping SpaCy, nlp artifacts not provided...")
            return results

        ner_entities = nlp_artifacts.entities

        for entity in entities:
            if entity not in self.supported_entities:
                continue
            for ent in ner_entities:
                if not self.__check_label(entity, ent.label_, self.check_label_groups):
                    continue
                if not ent.has_extension("confidence_score"):
                    raise ValueError(
                        "confidence score not available as a spaCy span extension "
                        "(ent._.confidence_score)"
                    )
                confidence_score = ent._.confidence_score
                textual_explanation = self.DEFAULT_EXPLANATION.format(ent.label_)
                explanation = self.build_spacy_explanation(
                    confidence_score, textual_explanation
                )
                spacy_result = RecognizerResult(
                    entity_type=entity,
                    start=ent.start_char,
                    end=ent.end_char,
                    score=confidence_score,
                    analysis_explanation=explanation,
                    recognition_metadata={
                        RecognizerResult.RECOGNIZER_NAME_KEY: self.name,
                        RecognizerResult.RECOGNIZER_IDENTIFIER_KEY: self.id,
                    },
                )
                results.append(spacy_result)

        return results

    @staticmethod
    def __check_label(
        entity: str, label: str, check_label_groups: Tuple[Set, Set]
    ) -> bool:
        return any(
            [entity in egrp and label in lgrp for egrp, lgrp in check_label_groups]
        )
