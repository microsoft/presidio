import logging
from typing import Optional, Dict, Iterator, Tuple, Union, List

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span, SpanGroup

from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngine, NerModelConfiguration

logger = logging.getLogger("presidio-analyzer")


class SpacyNlpEngine(NlpEngine):
    """
    SpacyNlpEngine is an abstraction layer over the nlp module.

    It provides processing functionality as well as other queries
    on tokens.
    The SpacyNlpEngine uses SpaCy as its NLP module
    """

    engine_name = "spacy"
    is_available = bool(spacy)
    DEFAULT_CONFIDENCE = 0.85

    def __init__(
        self,
        models: Optional[List[Dict[str, str]]] = None,
        ner_model_configuration: Optional[NerModelConfiguration] = None,
    ):
        """
        Initialize a wrapper on spaCy functionality.

        :param models: Dictionary with the name of the spaCy model per language.
        For example: models = [{"lang_code": "en", "model_name": "en_core_web_lg"}]
        :param ner_model_configuration: Parameters for the NER model. See conf/spacy.yaml for an example
        """
        if not models:
            models = [{"lang_code": "en", "model_name": "en_core_web_lg"}]
        self.models = models

        if not ner_model_configuration:
            ner_model_configuration = NerModelConfiguration(self.engine_name)
        self.ner_model_configuration = ner_model_configuration

        self.nlp = None

    def load(self) -> None:
        """Load the spaCy NLP model."""
        logger.debug(f"Loading SpaCy models: {self.models}")

        self.nlp = {}
        # Download spaCy model if missing
        for model in self.models:
            self._validate_model_params(model)
            self._download_spacy_model_if_needed(model["model_name"])
            self.nlp[model["lang_code"]] = spacy.load(model["model_name"])

    @staticmethod
    def _download_spacy_model_if_needed(model_name):
        if not spacy.util.is_package(model_name):
            logger.warning(f"Model {model_name} is not installed. Downloading...")
            spacy.cli.download(model_name)
            logger.info(f"Finished downloading model {model_name}")

    @staticmethod
    def _validate_model_params(model: Dict):
        if "lang_code" not in model:
            raise ValueError("lang_code is missing from model configuration")
        if "model_name" not in model:
            raise ValueError("model_name is missing from model configuration")
        if not isinstance(model["model_name"], str):
            raise ValueError("model_name must be a string")

    def get_supported_entities(self) -> List[str]:
        """Return the supported entities for this NLP engine."""
        if not self.ner_model_configuration.model_to_presidio_entity_mapping:
            raise ValueError(
                "model_to_presidio_entity_mapping is missing from model configuration"
            )
        return list(
            set(self.ner_model_configuration.model_to_presidio_entity_mapping.values())
        )

    def is_loaded(self) -> bool:
        """Return True if the model is already loaded."""
        return self.nlp is not None

    def process_text(self, text: str, language: str) -> NlpArtifacts:
        """Execute the SpaCy NLP pipeline on the given text and language."""
        if not self.nlp:
            raise ValueError("NLP engine is not loaded. Consider calling .load()")

        doc = self.nlp[language](text)
        return self._doc_to_nlp_artifact(doc, language)

    def process_batch(
        self,
        texts: Union[List[str], List[Tuple[str, object]]],
        language: str,
        as_tuples: bool = False,
    ) -> Iterator[Optional[NlpArtifacts]]:
        """Execute the NLP pipeline on a batch of texts using spacy pipe.
        :param texts: A list of texts to process.
        :param language: The language of the texts.
        :param as_tuples: If set to True, inputs should be a sequence of
            (text, context) tuples. Output will then be a sequence of
            (doc, context) tuples. Defaults to False.
        """

        if not self.nlp:
            raise ValueError("NLP engine is not loaded. Consider calling .load()")

        texts = (str(text) for text in texts)
        docs = self.nlp[language].pipe(texts, as_tuples=as_tuples)
        for doc in docs:
            yield doc.text, self._doc_to_nlp_artifact(doc, language)

    def is_stopword(self, word: str, language: str) -> bool:
        """
        Return true if the given word is a stop word.

        (within the given language)
        """
        return self.nlp[language].vocab[word].is_stop

    def is_punct(self, word: str, language: str) -> bool:
        """
        Return true if the given word is a punctuation word.

        (within the given language).
        """
        return self.nlp[language].vocab[word].is_punct

    def get_nlp(self, language: str) -> Language:
        """
        Return the language model loaded for a language.

        :param language: Language
        :return: Model from spaCy
        """
        return self.nlp[language]

    def _doc_to_nlp_artifact(self, doc: Doc, language: str) -> NlpArtifacts:
        lemmas = [token.lemma_ for token in doc]
        tokens_indices = [token.idx for token in doc]

        entities = self._get_entities(doc)
        scores = entities.attrs["scores"]

        entities_as_spans = [ent for ent in entities]

        return NlpArtifacts(
            entities=entities_as_spans,
            tokens=doc,
            tokens_indices=tokens_indices,
            lemmas=lemmas,
            nlp_engine=self,
            language=language,
            scores=scores,
        )

    def _get_entities(self, doc: Doc) -> SpanGroup:
        """
        Get an updated list of entities based on the ner model configuration.
        Remove entities that are in labels_to_ignore,
        update entity names based on model_to_presidio_entity_mapping
        :param doc: Output of a spaCy model
        :return: SpanGroup holding on the entities and confidence scores
        """
        output_spans = SpanGroup(doc, attrs={"scores": []})

        mapping = self.ner_model_configuration.model_to_presidio_entity_mapping
        for ent in doc.ents:
            # Remove model labels in the ignore list
            if ent.label_ in self.ner_model_configuration.labels_to_ignore:
                continue

            # Update entity label based on mapping
            if ent.label_ in mapping:
                ent.label_ = mapping[ent.label_]
            else:
                logger.warning(
                    f"Entity {ent.label_} is not mapped to a Presidio entity, but keeping anyway"
                )

            # Remove presidio entities in the ignore list
            if ent.label_ in self.ner_model_configuration.labels_to_ignore:
                continue

            output_spans.append(ent)

            # Set default confidence (spaCy models don't have built in confidence scores)
            score = self.DEFAULT_CONFIDENCE

            # Update score if entity is in low score entity names
            if ent.label_ in self.ner_model_configuration.low_score_entity_names:
                score *= self.ner_model_configuration.low_confidence_score_multiplier

            output_spans.attrs["scores"].append(score)

        return output_spans
