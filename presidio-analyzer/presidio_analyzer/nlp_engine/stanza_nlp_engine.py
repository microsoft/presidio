import logging
from typing import Optional, Dict, List

try:
    import stanza
    import spacy_stanza
except ImportError:
    stanza = None

from presidio_analyzer.nlp_engine import SpacyNlpEngine

logger = logging.getLogger("presidio-analyzer")


class StanzaNlpEngine(SpacyNlpEngine):
    """
    StanzaNlpEngine is an abstraction layer over the nlp module.

    It provides processing functionality as well as other queries
    on tokens.
    The StanzaNlpEngine uses spacy-stanza and stanza as its NLP module

    """

    engine_name = "stanza"
    is_available = bool(stanza)

    def load(self):
        """Load the NLP model."""

        logger.debug(f"Loading Stanza models: {self.models}")

        self.nlp = {}
        for model in self.models:
            self._validate_model_params(model)
            self.nlp[model["lang_code"]] = spacy_stanza.load_pipeline(
                model["model_name"],
                processors="tokenize,pos,lemma,ner",
            )
