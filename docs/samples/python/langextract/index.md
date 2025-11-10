# Language Model-based PII/PHI Detection using LangExtract

## Introduction

Presidio supports Language Model-based PII/PHI detection for flexible, zero-shot entity recognition using various language models (LLMs, SLMs, etc.).

**Detects both:**
- **PII (Personally Identifiable Information)**: Names, emails, phone numbers, SSN, credit cards, etc.
- **PHI (Protected Health Information)**: Medical records, health identifiers, etc.

This approach uses [LangExtract](https://github.com/google/langextract) under the hood to integrate with language model providers.
Currently, this integration supports **Ollama for local language model deployment only**.

## Supported Language Model Providers

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

Create your own `ollama_config.yaml` file with the Ollama URL (default: `http://localhost:11434`) or use the [default configuration](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/ollama_config.yaml).

## Language Model-based Recognizer Implementation

Presidio provides a hierarchy of recognizers for Language Model-based PII/PHI detection:

- **`LMRecognizer`**: Abstract base class for all language model recognizers (LLMs, SLMs, etc.)
- **`LangExtractRecognizer`**: Abstract base class for LangExtract library integration (model-agnostic)
- **`OllamaLangExtractRecognizer`**: Concrete implementation for Ollama local language models

The `OllamaLangExtractRecognizer` is the recommended recognizer for using Language Model-based PII/PHI detection with local Ollama models.
[The implementation can be found here](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/third_party/ollama_langextract_recognizer.py).

## How to Use

1. Install the package:
   ```sh
   pip install presidio-analyzer[langextract]
   ```

2. Set up Ollama (see above).

3. Add the recognizer to Presidio:
   
   ```python
   from presidio_analyzer import AnalyzerEngine
   from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
   
   ollama = OllamaLangExtractRecognizer()
   
   analyzer = AnalyzerEngine()
   analyzer.registry.add_recognizer(ollama)
   
   analyzer.analyze(text="My email is john.doe@example.com", language="en")
   ```

## Configuration Options

Customize the recognizer in the `ollama_config.yaml` file:

- `model_id`: The Ollama model to use (e.g., "gemma3:1b")
- `model_url`: Ollama server URL (default: `http://localhost:11434`)
- `supported_entities`: PII/PHI entity types to detect
- `entity_mappings`: Map LangExtract entities to Presidio entity names
- `min_score`: Minimum confidence score

See the [configuration file](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/ollama_config.yaml) for all options.
