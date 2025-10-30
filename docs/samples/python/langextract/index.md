# LangExtract LLM-based PII Detection Integration

## Introduction

LangExtract is a library that enables LLM-based extraction of structured information from text,
including PII detection. It provides a flexible way to use various LLM providers (Google Gemini,
OpenAI, Ollama for local models) for detecting personally identifiable information.
This document demonstrates Presidio integration with LangExtract.

## Supported LLM Providers

LangExtract supports multiple LLM providers:
- **Google Gemini** (default)
- **OpenAI** (including Azure OpenAI)
- **Ollama** (for local model deployment)

## Prerequisites

To use LangExtract with Presidio, install the required dependencies:

```sh
pip install presidio-analyzer[langextract]
```

### Configuration

LangExtract requires configuration through environment variables or the YAML configuration file:

- For **Google Gemini**: Set `LANGEXTRACT_API_KEY` environment variable
- For **OpenAI**: Configure `api_key` and optionally `base_url` in the config file
- For **Ollama**: Configure `model_url` to point to your local Ollama instance

Configuration is managed through `presidio-analyzer/presidio_analyzer/conf/langextract_config.yaml`.

## LangExtract Recognizer

[The implementation of the `LangExtractRecognizer` can be found here](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/third_party/langextract_recognizer.py).

## How to integrate LangExtract into Presidio

1. Install the package with the langextract extra:
   ```sh
   pip install presidio-analyzer[langextract]
   ```

2. Set up environment variables (for Gemini):
   ```bash
   export LANGEXTRACT_API_KEY=your_api_key
   ```

3. Add the `LangExtractRecognizer` to the recognizer registry:
   
   ```python
   from presidio_analyzer import AnalyzerEngine
   from presidio_analyzer.predefined_recognizers.third_party import LangExtractRecognizer
   
   langextract = LangExtractRecognizer()
   
   analyzer = AnalyzerEngine()
   analyzer.registry.add_recognizer(langextract)
   
   analyzer.analyze(text="My email is john.doe@example.com", language="en")
   ```

## Configuration Options

The recognizer can be customized through the `langextract_config.yaml` file. Key configuration options include:

- `enabled`: Enable/disable the recognizer
- `model_id`: The LLM model to use (e.g., "gemini-2.5-flash", "gpt-4")
- `supported_entities`: List of PII entity types to detect
- `entity_mappings`: Map between LangExtract and Presidio entity names
- `min_score`: Minimum confidence score threshold

For detailed configuration options, refer to the [configuration file](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/langextract_config.yaml).
