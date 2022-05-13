# Customizing the NLP models in Presidio Analyzer

Presidio uses NLP engines for two main tasks: NER based PII identification, and feature extraction for custom rule based logic (such as leveraging context words for improved detection).
While Presidio comes with an open-source model (the `en_core_web_lg` model from spaCy), it can be customized by leveraging other NLP models, either public or proprietary.
These models can be trained or downloaded from existing NLP frameworks like [spaCy](https://spacy.io/usage/models) and [Stanza](https://github.com/stanfordnlp/stanza).
In addition, other types of NLP frameworks can be integrated into Presidio.

## Replacing the default NLP model with a different model

### Setting up a new NLP model

As mentioned before, Presidio supports both [spaCy](https://spacy.io/usage/models)
and [Stanza](https://github.com/stanfordnlp/stanza) as its internal NLP engine.
This section describes how new models from either spaCy or Stanza could be obtained,
and how to configure Presidio to use them.

#### Download / create the new model

##### Using a public spaCy/Stanza model

To replace the default model with a different public model, first download the desired spaCy/Stanza NER models.

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

!!! tip "Tip"
    For Person, Location and Organization detection, it could be useful to try out the `en_core_web_trf` model which uses a more modern deep-learning architecture, but is slower than the default `en_core_web_lg` model.

##### Training your own model

!!! note "Note"
    A labeled dataset containing text and labeled PII entities is required for training a new model.

To train your own model, see these links on spaCy and Stanza:

- [Train your own spaCy model](https://spacy.io/usage/training).
- [Train your own Stanza model](https://stanfordnlp.github.io/stanza/training.html).

Once models are trained, they should be installed locally in the same environment as Presidio Analyzer.

#### Configure Presidio to use the new model

Configuration can be done in two ways:

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

- **Via configuration**: Set up the models which should be used in the [default `conf` file](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/conf/default.yaml).

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

    In this examples we:
        a. create an `NlpEngine` holding two spaCy models (one in English: `en_core_web_lg` and one in Spanish: `es_core_news_md`).
        b. define the `supported_languages` parameter accordingly.
        c. pass requests in each of these languages.

    !!! note "Note"
        Presidio can currently use one NLP model per language.

## Using a previously loaded NLP model

If the app is already loading an NLP model, it can be re-used to prevent presidio from loading it again by extending the relevant engine.

    ```python
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import SpacyNlpEngine
    import spacy

    # Create a class inheriting from SpacyNlpEngine
    class LoadedSpacyNlpEngine(SpacyNlpEngine):
        def __init__(self, loaded_spacy_model):
            self.nlp = {"en": loaded_spacy_model}

    # Load a model a-priori
    nlp = spacy.load("en_core_web_sm")

    # Pass the loaded model to the new LoadedSpacyNlpEngine
    loaded_nlp_engine = LoadedSpacyNlpEngine(loaded_spacy_model = nlp)

    # Pass the engine to the analyzer
    analyzer = AnalyzerEngine(nlp_engine = loaded_nlp_engine)

    # Analyze text
    analyzer.analyze(text="My name is Bob", language="en")
    ```

## Leverage frameworks other than spaCy or Stanza for ML based PII detection

In addition to the built-in spaCy/Stanza capabitilies, it is possible to create new recognizers which serve as interfaces to other models.
See the [Remote recognizer documentation](adding_recognizers.md#creating-a-remote-recognizer) and [samples](../samples/python/integrating_with_external_services.ipynb) for more information.

For considerations for creating such recognizers, see the [best practices for adding ML recognizers documentation](developing_recognizers.md#machine-learning--ml--based-or-rule-based).
