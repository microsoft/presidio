# Customizing the NLP models in Presidio Analyzer

Presidio uses NLP engines for two main tasks: NER based PII identification, 
and feature extraction for custom rule based logic (such as leveraging context words for improved detection).
While Presidio comes with an open-source model (the `en_core_web_lg` model from spaCy), 
it can be customized by leveraging other NLP models, either public or proprietary.
These models can be trained or downloaded from existing NLP frameworks like [spaCy](https://spacy.io/usage/models), 
[Stanza](https://github.com/stanfordnlp/stanza) and 
[transformers](https://github.com/huggingface/transformers).

In addition, other types of NLP frameworks [can be integrated into Presidio](developing_recognizers.md#machine-learning-ml-based-or-rule-based).

## Setting up a custom NLP model

- [spaCy or stanza](nlp_engines/spacy_stanza.md)
- [transformers](nlp_engines/transformers.md)

## Configure Presidio to use the new model

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

## Leverage frameworks other than spaCy, Stanza and transformers for ML based PII detection

In addition to the built-in spaCy/Stanza/transformers capabitilies, it is possible to create new recognizers which serve as interfaces to other models.
For more information:
- [Remote recognizer documentation](adding_recognizers.md#creating-a-remote-recognizer) and [samples](../samples/python/integrating_with_external_services.ipynb).
- [Flair recognizer example](../samples/python/flair_recognizer.py)

For considerations for creating such recognizers, see the [best practices for adding ML recognizers documentation](developing_recognizers.md#machine-learning--ml--based-or-rule-based).
