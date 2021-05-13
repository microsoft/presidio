# PII detection in different languages

Presidio supports PII detection in multiple languages.
In its default configuration, it contains recognizers and models for English.

To extend Presidio to detect PII in an additional language, these modules require modification:

1. The `NlpEngine` containing the NLP model which performs tokenization,
lemmatization, Named Entity Recognition and other NLP tasks.
2. PII recognizers (different `EntityRecognizer` objects) should be adapted or created.

!!! note "Note"
    While different detection mechanisms such as regular expressions are language agnostic, the context words used to increase the PII detection confidence aren't. Consider updating the list of context words for each recognizer to leverage context words in additional languages.

## Table of contents

- [Configuring the NLP Engine](#configuring-the-nlp-engine)
- [Set up language specific recognizers](#set-up-language-specific-recognizers)
- [Automatically install NLP models into the Docker container](#automatically-install-nlp-models-into-the-docker-container)

### Configuring the NLP Engine

As its internal NLP engine, Presidio supports both [spaCy](https://spacy.io/usage/models)
and [Stanza](https://github.com/stanfordnlp/stanza). To set up new models, follow these two steps:

1. Download the spaCy/Stanza NER models for your desired language.

    - To download a new model with spaCy:

        ```sh
        python -m spacy download es_core_news_md
        ```

        In this example we download the medium size model for Spanish.

    - To download a new model with Stanza:

        <!--pytest-codeblocks:skip-->
        ```python
        import stanza
        stanza.download("en") # where en is the language code of the model.
        ```

    For the available models, follow these links: [spaCy](https://spacy.io/usage/models), [stanza](https://stanfordnlp.github.io/stanza/available_models.html#available-ner-models).

2. Update the models configuration in one of two ways:
    - **Via code**: Create an `NlpEngine` using the `NlpEnginerProvider` class, and pass it to the `AnalyzerEngine` as input:

        ```python
        from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
        from presidio_analyzer.nlp_engine import NlpEngineProvider

        # Create configuration containing engine name and models
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "es", "model_name": "es_core_news_md"},
                       {"lang_code": "en", "model_name": "en_core_web_lg"}],
        }

        # Create NLP engine based on configuration
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine_with_spanish = provider.create_engine()

        # Pass the created NLP engine and supported_languages to the AnalyzerEngine
        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine_with_spanish, 
            supported_languages=["en", "es"]
        )

        # Analyze in different languages
        results_spanish = analyzer.analyze(text="Mi nombre es Morris", language="es")
        print(results_spanish)

        results_english = analyzer.analyze(text="My name is Morris", language="en")
        print(results_english)
        ```

    - **Via configuration**: Set up the models which should be used in the [default `conf` file](https://github.com/microsoft/presidio/blob/master/presidio-analyzer/conf/default.yaml).

        An example Conf file:

        ```yaml
        nlp_engine_name: spacy
        models:
            -
            lang_code: en
            model_name: en_core_web_lg
            -
            lang_code: es
            model_name: es_core_news_md 
        ```

        The default conf file is read during the default initialization of the `AnalyzerEngine`. Alternatively, the path to a custom configuration file can be passed to the `NlpEngineProvider`:

        ```python
        from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
        from presidio_analyzer.nlp_engine import NlpEngineProvider

        LANGUAGES_CONFIG_FILE = "./docs/analyzer/languages-config.yml"

        # Create NLP engine based on configuration file
        provider = NlpEngineProvider(conf_file=LANGUAGES_CONFIG_FILE)
        nlp_engine_with_spanish = provider.create_engine()

        # Pass created NLP engine and supported_languages to the AnalyzerEngine
        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine_with_spanish, 
            supported_languages=["en", "es"]
        )

        # Analyze in different languages
        results_spanish = analyzer.analyze(text="Mi nombre es David", language="es")
        print(results_spanish)

        results_english = analyzer.analyze(text="My name is David", language="en")
        print(results_english)
        ```

    In this examples we create an `NlpEngine` holding two spaCy models (one in English: `en_core_web_lg` and one in Spanish: `es_core_news_md`), define the `supported_languages` parameter accordingly, and can send requests in each of these languages.

### Set up language specific recognizers

Recognizers are language dependent either by their logic or by the context words used while scanning the surrounding of a detected entity.
As these context words are used to increase score, they should be in the expected input language.

Consider updating the context words of existing recognizers or add new recognizers to support new languages.
Each recognizer can support one language. For example:

```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.predefined_recognizers import EmailRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider

LANGUAGES_CONFIG_FILE = "./docs/analyzer/languages-config.yml"

# Create NLP engine based on configuration file
provider = NlpEngineProvider(conf_file=LANGUAGES_CONFIG_FILE)
nlp_engine_with_spanish = provider.create_engine()

# Setting up an English Email recognizer:
email_recognizer_en = EmailRecognizer(supported_language="en",context=["email","mail"])

# Setting up a Spanish Email recognizer
email_recognizer_es = EmailRecognizer(supported_language="es",context=["correo","electrónico"])

registry = RecognizerRegistry()

# Add recognizers to registry
registry.add_recognizer(email_recognizer_en)
registry.add_recognizer(email_recognizer_es)

# Set up analyzer with our updated recognizer registry
analyzer = AnalyzerEngine(
    registry=registry,
    supported_languages=["en","es"],
    nlp_engine=nlp_engine_with_spanish)

analyzer.analyze(text="My name is David", language="en")
```

### Automatically install NLP models into the Docker container

When packaging the code into a Docker container, NLP models are automatically installed.
To define which models should be installed,
update the [conf/default.yaml](https://github.com/microsoft/presidio/blob/master/presidio-analyzer/conf/default.yaml) file. This file is read during
the `docker build` phase and the models defined in it are installed automatically.
