import copy
import logging
from typing import Optional, List

import torch
from presidio_analyzer import (
    RecognizerResult,
    EntityRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.nlp_engine import NlpArtifacts

from .configuration import BERT_DEID_CONFIGURATION


logger = logging.getLogger("presidio-analyzer")

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        pipeline,
        TokenClassificationPipeline,
    )

except ImportError:
    logger.error("transformers is not installed")


class TransformersRecognizer(EntityRecognizer):
    """
    Wrapper for a transformers model, if needed to be used within Presidio Analyzer.
    The class loads models hosted on HuggingFace - https://huggingface.co/
    and loads the model and tokenizer into a TokenClassification pipeline.
    Samples are split into short text chunks, ideally shorter than max_length input_ids of the individual model,
    to avoid truncation by the Tokenizer and loss of information

    A configuration object should be maintained for each dataset-model combination and translate
    entities names into a standardized view. A sample of a configuration file is attached in
    the example.
    :param supported_entities: List of entities to run inference on
    :type supported_entities: Optional[List[str]]
    :param pipeline: Instance of a TokenClassificationPipeline including a Tokenizer and a Model, defaults to None
    :type pipeline: Optional[TokenClassificationPipeline], optional
    :param model_path: string referencing a HuggingFace uploaded model to be used for Inference, defaults to None
    :type model_path: Optional[str], optional

    :example
    >from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
    >model_path = "obi/deid_roberta_i2b2"
    >transformers_recognizer = TransformersRecognizer(model_path=model_path,
    >supported_entities = model_configuration.get("PRESIDIO_SUPPORTED_ENTITIES"))
    >transformers_recognizer.load_transformer(**model_configuration)
    >registry = RecognizerRegistry()
    >registry.add_recognizer(transformers_recognizer)
    >analyzer = AnalyzerEngine(registry=registry)
    >sample = "My name is Christopher and I live in Irbid."
    >results = analyzer.analyze(sample, language="en",return_decision_process=True)

    >for result in results:
    >    print(result,'----', sample[result.start:result.end])
    """

    def load(self) -> None:
        pass

    def __init__(
        self,
        model_path: Optional[str] = None,
        pipeline: Optional[TokenClassificationPipeline] = None,
        supported_entities: Optional[List[str]] = None,
    ):
        if not supported_entities:
            supported_entities = BERT_DEID_CONFIGURATION[
                "PRESIDIO_SUPPORTED_ENTITIES"
            ]
        super().__init__(
            supported_entities=supported_entities,
            name=f"Transformers model {model_path}",
        )

        self.model_path = model_path
        self.pipeline = pipeline
        self.is_loaded = False

        self.aggregation_mechanism = None
        self.ignore_labels = None
        self.model_to_presidio_mapping = None
        self.entity_mapping = None
        self.default_explanation = None
        self.text_overlap_length = None
        self.chunk_length = None
        self.id_entity_name = None
        self.id_score_reduction = None

    def load_transformer(self, **kwargs) -> None:
        """Load external configuration parameters and set default values.

        :param kwargs: define default values for class attributes and modify pipeline behavior
        **DATASET_TO_PRESIDIO_MAPPING (dict) - defines mapping entity strings from dataset format to Presidio format
        **MODEL_TO_PRESIDIO_MAPPING (dict) -  defines mapping entity strings from chosen model format to Presidio format
        **SUB_WORD_AGGREGATION(str) - define how to aggregate sub-word tokens into full words and spans as defined
        in HuggingFace https://huggingface.co/transformers/v4.8.0/main_classes/pipelines.html#transformers.TokenClassificationPipeline # noqa
        **CHUNK_OVERLAP_SIZE (int) - number of overlapping characters in each text chunk
        when splitting a single text into multiple inferences
        **CHUNK_SIZE (int) - number of characters in each chunk of text
        **LABELS_TO_IGNORE (List(str)) - List of entities to skip evaluation. Defaults to ["O"]
        **DEFAULT_EXPLANATION (str) - string format to use for prediction explanations
        **ID_ENTITY_NAME (str) - name of the ID entity
        **ID_SCORE_REDUCTION (float) - score multiplier for ID entities
        """

        self.entity_mapping = kwargs.get("DATASET_TO_PRESIDIO_MAPPING", {})
        self.model_to_presidio_mapping = kwargs.get("MODEL_TO_PRESIDIO_MAPPING", {})
        self.ignore_labels = kwargs.get("LABELS_TO_IGNORE", ["O"])
        self.aggregation_mechanism = kwargs.get("SUB_WORD_AGGREGATION", "simple")
        self.default_explanation = kwargs.get("DEFAULT_EXPLANATION", None)
        self.text_overlap_length = kwargs.get("CHUNK_OVERLAP_SIZE", 40)
        self.chunk_length = kwargs.get("CHUNK_SIZE", 600)
        self.id_entity_name = kwargs.get("ID_ENTITY_NAME", "ID")
        self.id_score_reduction = kwargs.get("ID_SCORE_REDUCTION", 0.5)

        if not self.pipeline:
            if not self.model_path:
                self.model_path = "obi/deid_roberta_i2b2"
                logger.warning(
                    f"Both 'model' and 'model_path' arguments are None. Using default model_path={self.model_path}"
                )

        self._load_pipeline()

    def _load_pipeline(self) -> None:
        """Initialize NER transformers pipeline using the model_path provided"""

        logging.debug(f"Initializing NER pipeline using {self.model_path} path")
        device = 0 if torch.cuda.is_available() else -1
        self.pipeline = pipeline(
            "ner",
            model=AutoModelForTokenClassification.from_pretrained(self.model_path),
            tokenizer=AutoTokenizer.from_pretrained(self.model_path),
            # Will attempt to group sub-entities to word level
            aggregation_strategy=self.aggregation_mechanism,
            device=device,
            framework="pt",
            ignore_labels=self.ignore_labels,
        )

        self.is_loaded = True

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
        Analyze text using transformers model to produce NER tagging.
        :param text : The text for analysis.
        :param entities: Not working properly for this recognizer.
        :param nlp_artifacts: Not used by this recognizer.
        :return: The list of Presidio RecognizerResult constructed from the recognized
            transformers detections.
        """

        results = list()
        # Run transformer model on the provided text
        ner_results = self._get_ner_results_for_text(text)

        for res in ner_results:
            res["entity_group"] = self.__check_label_transformer(res["entity_group"])
            if not res["entity_group"]:
                continue

            if res["entity_group"] == self.id_entity_name:
                print(f"ID entity found, multiplying score by {self.id_score_reduction}")
                res["score"] = res["score"] * self.id_score_reduction

            textual_explanation = self.default_explanation.format(res["entity_group"])
            explanation = self.build_transformers_explanation(
                float(round(res["score"], 2)), textual_explanation, res["word"]
            )
            transformers_result = self._convert_to_recognizer_result(res, explanation)

            results.append(transformers_result)

        return results

    @staticmethod
    def split_text_to_word_chunks(
        input_length: int, chunk_length: int, overlap_length: int
    ) -> List[List]:
        """The function calculates chunks of text with size chunk_length. Each chunk has overlap_length number of
        words to create context and continuity for the model

        :param input_length: Length of input_ids for a given text
        :type input_length: int
        :param chunk_length: Length of each chunk of input_ids.
        Should match the max input length of the transformer model
        :type chunk_length: int
        :param overlap_length: Number of overlapping words in each chunk
        :type overlap_length: int
        :return: List of start and end positions for individual text chunks
        :rtype: List[List]
        """
        if input_length < chunk_length:
            return [[0, input_length]]
        if chunk_length <= overlap_length:
            logger.warning(
                "overlap_length should be shorter than chunk_length, setting overlap_length to by half of chunk_length"
            )
            overlap_length = chunk_length // 2
        return [
            [i, min([i + chunk_length, input_length])]
            for i in range(
                0, input_length - overlap_length, chunk_length - overlap_length
            )
        ]

    def _get_ner_results_for_text(self, text: str) -> List[dict]:
        """The function runs model inference on the provided text.
        The text is split into chunks with n overlapping characters.
        The results are then aggregated and duplications are removed.

        :param text: The text to run inference on
        :type text: str
        :return: List of entity predictions on the word level
        :rtype: List[dict]
        """
        model_max_length = self.pipeline.tokenizer.model_max_length
        # calculate inputs based on the text
        text_length = len(text)
        # split text into chunks
        if text_length <= model_max_length:
            predictions = self.pipeline(text)
        else:
            logger.info(
                f"splitting the text into chunks, length {text_length} > {model_max_length}"
            )
            predictions = list()
            chunk_indexes = TransformersRecognizer.split_text_to_word_chunks(
                text_length, self.chunk_length, self.text_overlap_length
                )

            # iterate over text chunks and run inference
            for chunk_start, chunk_end in chunk_indexes:
                chunk_text = text[chunk_start:chunk_end]
                chunk_preds = self.pipeline(chunk_text)

                # align indexes to match the original text - add to each position the value of chunk_start
                aligned_predictions = list()
                for prediction in chunk_preds:
                    prediction_tmp = copy.deepcopy(prediction)
                    prediction_tmp["start"] += chunk_start
                    prediction_tmp["end"] += chunk_start
                    aligned_predictions.append(prediction_tmp)

                predictions.extend(aligned_predictions)

        # remove duplicates
        predictions = [dict(t) for t in {tuple(d.items()) for d in predictions}]
        return predictions

    @staticmethod
    def _convert_to_recognizer_result(
        prediction_result: dict, explanation: AnalysisExplanation
    ) -> RecognizerResult:
        """The method parses NER model predictions into a RecognizerResult format to enable down the stream analysis

        :param prediction_result: A single example of entity prediction
        :type prediction_result: dict
        :param explanation: Textual representation of model prediction
        :type explanation: str
        :return: An instance of RecognizerResult which is used to model evaluation calculations
        :rtype: RecognizerResult
        """

        transformers_results = RecognizerResult(
            entity_type=prediction_result["entity_group"],
            start=prediction_result["start"],
            end=prediction_result["end"],
            score=float(round(prediction_result["score"], 2)),
            analysis_explanation=explanation,
        )

        return transformers_results

    def build_transformers_explanation(
        self,
        original_score: float,
        explanation: str,
        pattern: str,
    ) -> AnalysisExplanation:
        """
        Create explanation for why this result was detected.
        :param original_score: Score given by this recognizer
        :param explanation: Explanation string
        :param pattern: Regex pattern used
        :return Structured explanation and scores of a NER model prediction
        :rtype: AnalysisExplanation
        """
        explanation = AnalysisExplanation(
            recognizer=self.__class__.__name__,
            original_score=float(original_score),
            textual_explanation=explanation,
            pattern=pattern,
        )
        return explanation

    def __check_label_transformer(self, label: str) -> Optional[str]:
        """The function validates the predicted label is identified by Presidio
        and maps the string into a Presidio representation
        :param label: Predicted label by the model
        :return: Returns the adjusted entity name
        """

        # convert model label to presidio label
        entity = self.model_to_presidio_mapping.get(label, None)

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
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    import spacy

    model_path = "obi/deid_roberta_i2b2"
    supported_entities = BERT_DEID_CONFIGURATION.get(
        "PRESIDIO_SUPPORTED_ENTITIES")
    transformers_recognizer = TransformersRecognizer(model_path=model_path,
                                                     supported_entities=supported_entities)

    # This would download a large (~500Mb) model on the first run
    transformers_recognizer.load_transformer(**BERT_DEID_CONFIGURATION)

    # Add transformers model to the registry
    registry = RecognizerRegistry()
    registry.add_recognizer(transformers_recognizer)
    registry.remove_recognizer("SpacyRecognizer")

    # Use small spacy model, for faster inference.
    if not spacy.util.is_package("en_core_web_sm"):
        spacy.cli.download("en_core_web_sm")

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }

    nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

    analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)

    sample = "My name is John and I live in NY"
    results = analyzer.analyze(sample, language="en",
                               return_decision_process=True,
                               )
    print("Found the following entities:")
    for result in results:
        print(result, '----', sample[result.start:result.end])

    # Found the following entities:
    # type: PERSON, start: 11, end: 15, score: 1.0 ---- John
    # type: LOCATION, start: 30, end: 32, score: 1.0 ---- NY
