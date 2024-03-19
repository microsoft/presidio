import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from spacy.util import load_config
from spacy_llm.util import assemble_from_config

from presidio_analyzer.nlp_engine import SpacyNlpEngine, NerModelConfiguration, \
    NlpEngineProvider

try:
    import spacy_llm
except ImportError:
    spacy_llm = None

logger = logging.getLogger("presidio-analyzer")


class SpacyLLMNlpEngine(SpacyNlpEngine):
    engine_name = "spacy-llm"
    is_available = bool(spacy_llm)

    def __init__(
        self,
        models: Optional[List[Dict[str, str]]] = None,
        ner_model_configuration: Optional[NerModelConfiguration] = None,
        path_to_config: Optional[str] = "spacy_llm.cfg",
        path_to_examples: Optional[str] = "spacy_llm_examples.json"
    ):
        super().__init__(models, ner_model_configuration)
        self.path_to_config = Path(path_to_config)
        self.path_to_examples = path_to_examples

    def load(self) -> None:
        """Load the NLP model."""

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("Could not find the API key to access the OpenAI API. "
                             "Ensure you have an API key set up via "
                             "https://platform.openai.com/account/api-keys, "
                             "then make it available as "
                             "an environment variable 'OPENAI_API_KEY'.")

        labels = list(
            self.ner_model_configuration.model_to_presidio_entity_mapping.keys()
        )

        self.nlp = {}
        for model in self.models:
            self._validate_model_params(model)
            language = model["lang_code"]
            overrides = self._get_overrides(language=language,
                                            labels=labels,
                                            examples_path=self.path_to_examples)
            config = load_config(self.path_to_config,
                                 overrides=overrides,
                                 interpolate=True)

            nlp = assemble_from_config(config)
            self.nlp[model["lang_code"]] = nlp

    @staticmethod
    def _get_overrides(
        language: str,
        labels: List[str],
        examples_path: Optional[str] = None,
        llm_models: str = "spacy.GPT-3-5.v2",
        model_name: str = "gpt-3.5-turbo",
        llm_tasks: str = "spacy.NER.v3",
    ) -> Dict[str, Any]:
        """Create a config dict for the NER model which overrides the defaults."""

        return {
            "nlp.lang": language,
            "components.llm.task.labels": labels,
            "components.llm.task.examples.path": examples_path,
            "components.llm.model.@llm_models": llm_models,
            "components.llm.model.name": model_name,
            "components.llm.task.@llm_tasks": llm_tasks,
        }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    nlp_engine = NlpEngineProvider(conf_file=Path("../../conf/spacy_llm.yaml")).create_engine() # noqa E501
    nlp_artifacts = nlp_engine.process_text("My name is John Doe and I live in New York.", "en")
    print(nlp_artifacts)
