# German Language Support – spaCy NLP Configuration

This recipe provides a ready-to-use spaCy NLP configuration for running
Presidio Analyzer with both English and German language models.

## When to use this

Use this configuration when you need to analyze documents in German (or a mix
of English and German) with Presidio's built-in German recognizers.

## Configuration

`spacy_en_de.yaml` configures Presidio's NLP engine to load two spaCy models:

| Language | Model | Notes |
|----------|-------|-------|
| `en` | `en_core_web_lg` | English – large model, good NER accuracy |
| `de` | `de_core_news_md` | German – medium model from spaCy |

### Prerequisites

Install the required spaCy models:

```bash
pip install presidio-analyzer
python -m spacy download en_core_web_lg
python -m spacy download de_core_news_md
```

### Usage

Pass the config file when initializing the `AnalyzerEngine`:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

provider = NlpEngineProvider(conf_file="path/to/spacy_en_de.yaml")
nlp_engine = provider.create_engine()

engine = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en", "de"])
results = engine.analyze(text="Meine KVNR ist A123456787.", language="de")
```

Or set the `NLP_CONF_FILE` environment variable / Docker build arg:

```bash
export NLP_CONF_FILE=path/to/spacy_en_de.yaml
```

## Entity support

With `language="de"` the following German-specific recognizers are active
alongside the generic ones (IBAN, email, phone, …):

| Entity | Recognizer |
|--------|-----------|
| `DE_TAX_ID` | Steueridentifikationsnummer |
| `DE_TAX_NUMBER` | Steuernummer |
| `DE_SOCIAL_SECURITY` | Rentenversicherungsnummer |
| `DE_HEALTH_INSURANCE` | Krankenversicherungsnummer (KVNR) |
| `DE_PASSPORT` | Reisepassnummer |
| `DE_ID_CARD` | Personalausweisnummer |
| `DE_KFZ` | Kfz-Kennzeichen |
| `DE_PLZ` | Postleitzahl |
| `DE_HANDELSREGISTER` | Handelsregisternummer |
| `DE_LANR` | Lebenslange Arztnummer |
| `DE_BSNR` | Betriebsstättennummer |
| `DE_VAT_ID` | Umsatzsteuer-Identifikationsnummer |
| `DE_FUEHRERSCHEIN` | Führerscheinnummer |
