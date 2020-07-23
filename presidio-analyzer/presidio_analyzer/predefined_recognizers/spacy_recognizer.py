from presidio_analyzer import RecognizerResult, LocalRecognizer, AnalysisExplanation


class SpacyRecognizer(LocalRecognizer):

    ENTITIES = ["DATE_TIME", "NRP", "LOCATION", "PERSON"]

    DEFAULT_EXPLANATION = "Identified as {} by Spacy's Named Entity Recognition"

    CHECK_LABEL_GROUPS = [
        ({"LOCATION"}, {"GPE", "LOC"}),
        ({"PERSON", "PER"}, {"PERSON", "PER"}),
        ({"DATE_TIME"}, {"DATE", "TIME"}),
        ({"NRP"}, {"NORP"}),
    ]

    def __init__(
        self,
        supported_language="en",
        supported_entities=None,
        ner_strength=0.85,
        check_label_groups=None,
    ):
        self.ner_strength = ner_strength
        self.check_label_groups = (
            check_label_groups if check_label_groups else self.CHECK_LABEL_GROUPS
        )
        supported_entities = supported_entities if supported_entities else self.ENTITIES
        super().__init__(
            supported_entities=supported_entities, supported_language=supported_language
        )

    def load(self):
        # no need to load anything as the analyze method already receives
        # preprocessed nlp artifacts
        pass

    @staticmethod
    def build_spacy_explanation(recognizer_name, original_score, explanation):
        explanation = AnalysisExplanation(
            recognizer=recognizer_name,
            original_score=original_score,
            textual_explanation=explanation,
        )
        return explanation

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        if not nlp_artifacts:
            self.logger.warning("Skipping SpaCy, nlp artifacts not provided...")
            return results

        ner_entities = nlp_artifacts.entities

        for entity in entities:
            if entity not in self.supported_entities:
                continue
            for ent in ner_entities:
                if not self.__check_label(entity, ent.label_, self.check_label_groups):
                    continue
                textual_explanation = self.DEFAULT_EXPLANATION.format(ent.label_)
                explanation = self.build_spacy_explanation(
                    self.__class__.__name__, self.ner_strength, textual_explanation
                )
                spacy_result = RecognizerResult(
                    entity, ent.start_char, ent.end_char, self.ner_strength, explanation
                )
                results.append(spacy_result)

        return results

    @staticmethod
    def __check_label(entity, label, check_label_groups):
        return any(
            [entity in egrp and label in lgrp for egrp, lgrp in check_label_groups]
        )
