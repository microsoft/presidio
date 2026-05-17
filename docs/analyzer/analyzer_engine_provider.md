# Configuring the Analyzer Engine from file

Presidio uses `AnalyzerEngineProvider` to load `AnalyzerEngine` configuration from file.

## Using the unified configuration file (recommended)

The recommended approach is to use a **single configuration file** (`analyzer.yaml`) that contains all settings: supported languages, NLP engine configuration, and recognizer registry.

```python
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider

provider = AnalyzerEngineProvider(
    analyzer_engine_conf_file="./analyzer-config.yaml"
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

You can also load and validate the configuration using the Pydantic-based `AnalyzerConfiguration` model:

```python
from presidio_analyzer.configuration import AnalyzerConfiguration

config = AnalyzerConfiguration.from_yaml("./analyzer-config.yaml")
```

## Using the default configuration

Create an `AnalyzerEngineProvider` without any parameters. This will load the default configuration from the built-in [analyzer.yaml](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/analyzer.yaml):

```python
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider

analyzer = AnalyzerEngineProvider().create_engine()

results = analyzer.analyze(text="My name is Morris", language="en")
print(results)
```

## Using multiple files (deprecated)

!!! warning "Deprecated"

    Using separate configuration files for the NLP engine and recognizer registry is deprecated.
    Use the unified configuration file instead – place the `nlp_configuration` and
    `recognizer_registry` sections inside the analyzer configuration file.

The `nlp_engine_conf_file` and `recognizer_registry_conf_file` parameters are still supported for backward compatibility, but will be removed in a future version.

```python
from presidio_analyzer import AnalyzerEngine, AnalyzerEngineProvider

provider = AnalyzerEngineProvider(
    analyzer_engine_conf_file="./analyzer-config.yml",
    nlp_engine_conf_file="./nlp-config.yml",           # deprecated
    recognizer_registry_conf_file="./recognizers.yml",  # deprecated
)
analyzer = provider.create_engine()
```

## Enabling and disabling recognizers
In general, recognizers that are not added to the configuration would not be created, with one exception.

### Enabling/Disabling the NLP recognizer
One exception to this is the recognizer which extracts the `NlpEngine` entities (e.g. `SpacyRecognizer` when the `NlpEngine` is `SpacyNlpEngine`; `TransformersRecognizer` when the engine is `TransformersNlpEngine` and `StanzaRecognizer` when the engine is `StanzaNlpEngine`). 

Recognizers (including the NLP recognizer) could be disabled by defining `enabled=false` in the YAML configuration. For example:
```yaml
recognizer_registry:
  global_regex_flags: 26
  recognizers:
    - name: SpacyRecognizer
      type: predefined
      enabled: false
    - name: CreditCardRecognizer
      type: predefined
      enabled: true

supported_languages:
  - en
default_score_threshold: 0.7

nlp_configuration:
  nlp_engine_name: spacy
  models:
    -
      lang_code: en
      model_name: en_core_web_lg
```

In this example, the `SpacyRecognizer` is disabled, and the `CreditCardRecognizer` is enabled, resulting in only the `CREDIT_CARD` PII entity to be returned if detected.

### Adding context words in YAML recognizers

Recognizers defined in YAML can also include a `context` field.  
When used with `AnalyzerEngine` and a context enhancer, these words boost the score if they appear near the detected entity.

Example:

```yaml
recognizers:
  - name: "Date of Birth Recognizer"
    supported_entity: "DATE_TIME"
    supported_language: "en"
    patterns:
      - name: "DOB without slashes"
        regex: "((19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01]))"
        score: 0.8
    context:
      - DOB
```
```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.context_aware_enhancers.lemma_context_aware_enhancer import LemmaContextAwareEnhancer

# Save the DOB recognizer YAML to disk
dob_yaml = """
recognizers:
  - name: "Date of Birth Recognizer"
    supported_entity: "DATE_TIME"
    supported_language: "en"
    patterns:
      - name: "DOB without slashes"
        regex: "((19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01]))"
        score: 0.8
    context:
      - DOB
"""
with open("dob_recognizer.yml", "w") as f:
    f.write(dob_yaml)

# Configure NLP engine
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

# Load recognizer from YAML
registry = RecognizerRegistry()
registry.add_recognizers_from_yaml("dob_recognizer.yml")

# Analyzer with custom registry
analyzer = AnalyzerEngine(
    registry=registry,
    nlp_engine=nlp_engine,
    supported_languages=["en"]
)

text = "DOB: 19571012"

# Run base analysis
results = analyzer.analyze(text=text, language="en")
print("Base results:", results)

# Apply context enhancer
enhancer = LemmaContextAwareEnhancer()
nlp_artifacts = analyzer.nlp_engine.process_text(text, language="en")

boosted = enhancer.enhance_using_context(
    text=text,
    raw_results=results,
    nlp_artifacts=nlp_artifacts,
    recognizers=registry.recognizers,
    context=["DOB"]
)
print("Boosted results:", boosted)
```
