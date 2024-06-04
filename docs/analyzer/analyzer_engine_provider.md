# Configuring the Analyzer Engine from file

Presidio uses `AnalyzerEngineProvider` to load `AnalyzerEngine` configuration from file. 
Configuration can be loaded in three different ways:

## Using a single file

Create an `AnalyzerEngineProvider` using a single configuration file and set its path to `analyzer_engine_conf_file`, then create `AnalyzerEngine` based on it:

```python
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider

analyzer_conf_file = "./analyzer/analyzer-config-all.yml"

provider = AnalyzerEngineProvider(
    analyzer_engine_conf_file=analyzer_conf_file
    )
analyzer = provider.create_engine()

results = analyzer.analyze(text="My name is Morris", language="en")
print(results)
```

An example configuration file:

```yaml
supported_languages: 
- en
default_score_threshold: 0

nlp_configuration:
  nlp_engine_name: spacy
  models:
  -
    lang_code: en
    model_name: en_core_web_lg
  -
    lang_code: es
    model_name: es_core_news_md
  ner_model_configuration:
    model_to_presidio_entity_mapping:
      PER: PERSON
      PERSON: PERSON
      LOC: LOCATION
      LOCATION: LOCATION
      GPE: LOCATION
      ORG: ORGANIZATION
      DATE: DATE_TIME
      TIME: DATE_TIME
      NORP: NRP

    low_confidence_score_multiplier: 0.4
    low_score_entity_names:
    - ORGANIZATION
    - ORG
    default_score: 0.85

recognizer_registry:
  global_regex_flags: 26
  recognizers: 
  - name: CreditCardRecognizer
    supported_languages: 
      - en
    supported_entity: IT_FISCAL_CODE
    type: predefined

  - name: ItFiscalCodeRecognizer
    type: predefined
```

The configuration file contains the following parameters:

  - `supported_languages`: A list of supported languages that the analyzer will support.
  - `default_score_threshold`: A score that determines the minimal threshold for detection.
  - `nlp_configuration`: Configuration given to the NLP engine which will detect the PIIs and extract features for the downstream logic.
  - `recognizer_registry`: All the recognizers that will be used by the analyzer. 

!!! note "Note"

    `supported_languages` must be identical to the same field in recognizer_registry

## Using multiple files

Create an `AnalyzerEngineProvider` using three different configuration files for each of the following components:

  - Analyzer
  - NLP Engine
  - Recognizer Registry

!!! note "Note"

    Each of these parameters is optional and in case it's not set, the default configuration will be used. 


```python
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider

analyzer_conf_file = "./analyzer/analyzer-config.yml"
nlp_engine_conf_file = "./analyzer/nlp-config.yml"
recognizer_registry_conf_file = "./analyzer/recognizers-config.yml"

provider = AnalyzerEngineProvider(
    analyzer_engine_conf_file=analyzer_conf_file,
    nlp_engine_conf_file=nlp_engine_conf_file,
    recognizer_registry_conf_file=recognizer_registry_conf_file,
    )
analyzer = provider.create_engine()

results = analyzer.analyze(text="My name is Morris", language="en")
print(results)
```

The structure of the configuration files is as follows:

- Analyzer engine configuration file:

    ```yaml
    supported_languages: 
    - en
    default_score_threshold: 0
    ```

- NLP engine configuration file structure is examined thoroughly in the [Customizing the NLP model](customizing_nlp_models.md) section.

- Recognizer registry configuration file structure is examined thoroughly in the [Customizing recognizer registry from file](recognizer_registry_provider.md) section.

## Using the default configuration

Create an `AnalyzerEngineProvider` without any parameters. This will load the default configuration:

```python
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider

provider = AnalyzerEngineProvider().create_engine()

results = analyzer.analyze(text="My name is Morris", language="en")
print(results)
```

The default configuration of `AnalyzerEngine` is defined in the following files: 

  -  [Analyzer Engine](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/default_analyzer.yaml)
  -  [NLP Engine](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/default.yaml)
  -  [Recognizer Registry](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/default_recognizers.yaml)
