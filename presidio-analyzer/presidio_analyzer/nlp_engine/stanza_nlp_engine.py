import logging
from typing import Dict, List, Optional

try:
    import spacy_stanza
    import stanza
except ImportError:
    stanza = None

from presidio_analyzer.nlp_engine import NerModelConfiguration, SpacyNlpEngine

logger = logging.getLogger("presidio-analyzer")


class StanzaNlpEngine(SpacyNlpEngine):
    """
    StanzaNlpEngine is an abstraction layer over the nlp module.

    It provides processing functionality as well as other queries
    on tokens.
    The StanzaNlpEngine uses spacy-stanza and stanza as its NLP module

    :param models: Dictionary with the name of the spaCy model per language.
    For example: models = [{"lang_code": "en", "model_name": "en"}]
    :param ner_model_configuration: Parameters for the NER model.
    See conf/stanza.yaml for an example

    """

    engine_name = "stanza"
    is_available = bool(stanza)

    def __init__(
        self,
        models: Optional[List[Dict[str, str]]] = None,
        ner_model_configuration: Optional[NerModelConfiguration] = None,
        download_if_missing: bool = True,
    ):
        super().__init__(models, ner_model_configuration)
        self.download_if_missing = download_if_missing

    def load(self) -> None:
        """Load the NLP model."""

        logger.debug(f"Loading Stanza models: {self.models}")

        self.nlp = {}
        for model in self.models:
            self._validate_model_params(model)
            self.nlp[model["lang_code"]] = spacy_stanza.load_pipeline(
                model["model_name"],
                processors="tokenize,pos,lemma,ner",
                download_method="DOWNLOAD_RESOURCES"
                if self.download_if_missing
                else None,
            )
