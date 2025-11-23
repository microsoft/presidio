# Language Model-based PII/PHI Detection

## Introduction

Presidio supports language model-based PII/PHI detection for flexible entity recognition using language models (LLMs, SLMs, etc.). This approach enables detection of both:
- **PII (Personally Identifiable Information)**: Names, emails, phone numbers, SSN, credit cards, etc.
- **PHI (Protected Health Information)**: Medical records, health identifiers, etc.

The current implementation uses [LangExtract](https://github.com/google/langextract) with **Ollama** for local model deployment. Additional provider integrations will be added soon.

## Entity Detection Capabilities

Unlike pattern-based recognizers, language model-based detection is flexible and depends on:
- The language model being used
- The prompt description provided
- The few-shot examples configured

The default configuration includes examples for common PII/PHI entities such as PERSON, EMAIL_ADDRESS, PHONE_NUMBER, US_SSN, CREDIT_CARD, MEDICAL_LICENSE, and more. 
**You can customize the prompts and examples to detect any entity types relevant to your use case**.

For the default entity mappings and examples, see the [default configuration](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/langextract_config_ollama.yaml).

## Prerequisites

### Setting up Ollama

You have two options to set up Ollama:

**Option 1: Docker Compose** (recommended)
```bash
# Start Ollama service
docker compose up -d ollama

# Pull the language model (required - takes ~1-2 minutes)
docker exec -it presidio-ollama-1 ollama pull gemma2:2b
```

**Option 2: Manual setup**
Follow the [official LangExtract Ollama guide](https://github.com/google/langextract?tab=readme-ov-file#using-local-llms-with-ollama).

!!! note "Note"
    The model must be pulled before using the recognizer. The default model is `gemma2:2b` (~1.6GB).

## Language Model-based Recognizer Implementation

Presidio provides a hierarchy of recognizers for language model-based PII/PHI detection:

- **`LMRecognizer`**: Abstract base class for all language model recognizers (LLMs, SLMs, etc.)
- **`LangExtractRecognizer`**: Abstract base class for LangExtract library integration (model-agnostic)
- **`OllamaLangExtractRecognizer`**: Concrete implementation for Ollama local language models

[The implementation can be found here](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/third_party/ollama_langextract_recognizer.py).

## How to integrate Language Model-based detection into Presidio

### Option 1: Enable in Configuration (Recommended)

1. Install with langextract support and set up Ollama (see Prerequisites above):
   ```sh
   pip install presidio-analyzer[langextract]
   ```

2. Enable the recognizer in `default_recognizers.yaml`:
   ```yaml
   - name: OllamaLangExtractRecognizer
     enabled: true  # Change from false to true
   ```

### Option 2: Add Programmatically

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(OllamaLangExtractRecognizer())

results = analyzer.analyze(text="My email is john.doe@example.com", language="en")
```

### Custom Configuration

To use a custom configuration file:

```python
analyzer.registry.add_recognizer(
    OllamaLangExtractRecognizer(config_path="/path/to/custom_config.yaml")
)
```

!!! note "Note"
    The recognizer is disabled by default in `default_recognizers.yaml` to avoid requiring Ollama for basic Presidio usage. Enable it when you have Ollama set up and running.

## Configuration Options

The `langextract_config_ollama.yaml` file supports the following options:

- **`model_id`**: The Ollama model to use (default: `"gemma2:2b"`)
- **`model_url`**: Ollama server URL (default: `"http://localhost:11434"`)
- **`temperature`**: Model temperature for generation (default: `null` for model default)
- **`supported_entities`**: PII/PHI entity types to detect
- **`entity_mappings`**: Map LangExtract entity classes to Presidio entity names
- **`min_score`**: Minimum confidence score (default: `0.5`)

See the [default configuration](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/langextract_config_ollama.yaml) for complete examples.

## Troubleshooting

**ConnectionError: "Ollama server not reachable"**
- Ensure Ollama is running: `docker ps` or check `http://localhost:11434`
- Verify the `model_url` in your configuration matches your Ollama server address

**RuntimeError: "Model 'gemma2:2b' not found"**
- Pull the model: `docker exec -it presidio-ollama-1 ollama pull gemma2:2b`
- Or for manual setup: `ollama pull gemma2:2b`
- Verify the model name matches the `model_id` in your configuration
