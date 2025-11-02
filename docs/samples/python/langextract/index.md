# LangExtract LLM-based PII Detection Integration

## Introduction

[LangExtract](https://github.com/google/langextract) uses large language models (LLMs) to detect personally identifiable information (PII) in text.
This integration with Presidio currently supports **Ollama for local LLM deployment only**.

## Supported LLM Providers

Currently, only **Ollama** (local model deployment) is supported.

### Setting up Ollama

You have two options to set up Ollama:

1. **Manual setup**: Follow the [official LangExtract Ollama guide](https://github.com/google/langextract?tab=readme-ov-file#using-local-llms-with-ollama).

2. **Docker Compose** (recommended): Use the included configuration:
   ```bash
   docker compose up -d ollama
   ```
   The Ollama service will be available at `http://localhost:11434`.

## Prerequisites

To use LangExtract with Presidio, install the required dependencies:

```sh
pip install presidio-analyzer[langextract]
```

Create your own `langextract_config.yaml` file with the Ollama URL (default: `http://localhost:11434`) or use the [default configuration](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/langextract_config.yaml).

## LangExtract Recognizer

[The implementation of the `LangExtractRecognizer` can be found here](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/third_party/langextract_recognizer.py).

## How to Use

1. Install the package:
   ```sh
   pip install presidio-analyzer[langextract]
   ```

2. Set up Ollama (see above).

3. Add the recognizer to Presidio:
   
   ```python
   from presidio_analyzer import AnalyzerEngine
   from presidio_analyzer.predefined_recognizers.third_party import LangExtractRecognizer
   
   langextract = LangExtractRecognizer()
   
   analyzer = AnalyzerEngine()
   analyzer.registry.add_recognizer(langextract)
   
   analyzer.analyze(text="My email is john.doe@example.com", language="en")
   ```

## Configuration Options

Customize the recognizer in the `langextract_config.yaml` file:

- `enabled`: Enable/disable the recognizer
- `model_id`: The Ollama model to use (e.g., "gemma2:2b")
- `model_url`: Ollama server URL (default: `http://localhost:11434`)
- `supported_entities`: PII entity types to detect
- `entity_mappings`: Map LangExtract entities to Presidio entity names
- `min_score`: Minimum confidence score

See the [configuration file](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/langextract_config.yaml) for all options.
