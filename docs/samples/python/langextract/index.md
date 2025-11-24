# Language Model-based PII/PHI Detection

## Introduction

Presidio supports language model-based PII/PHI detection for flexible entity recognition using language models (LLMs, SLMs, etc.). This approach enables detection of both:
- **PII (Personally Identifiable Information)**: Names, emails, phone numbers, SSN, credit cards, etc.
- **PHI (Protected Health Information)**: Medical records, health identifiers, etc.

This approach uses [LangExtract](https://github.com/google/langextract) under the hood to integrate with language model providers.

## Entity Detection Capabilities

Unlike pattern-based recognizers, language model-based detection is flexible and depends on:

- The language model being used
- The prompt description provided
- The few-shot examples configured

The default configuration includes examples for common PII/PHI entities such as PERSON, EMAIL_ADDRESS, PHONE_NUMBER, US_SSN, CREDIT_CARD, MEDICAL_LICENSE, and more. 
**You can customize the prompts and examples to detect any entity types relevant to your use case**.

For the default entity mappings and examples, see the [default configuration](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/langextract_config_ollama.yaml).

## Supported Language Model Providers

Presidio supports the following language model providers through LangExtract:

1. **Ollama** - Local language model deployment (open-source models like Gemma, Llama, etc.)
2. **Azure OpenAI** - Cloud-based Azure OpenAI Service (GPT-4o, GPT-4, GPT-3.5-turbo)

## Language Model-based Recognizer Implementation

Presidio provides a hierarchy of recognizers for language model-based PII/PHI detection:

- **`LMRecognizer`**: Abstract base class for all language model recognizers (LLMs, SLMs, etc.)
- **`LangExtractRecognizer`**: Abstract base class for LangExtract library integration (model-agnostic)
- **`OllamaLangExtractRecognizer`**: Concrete implementation for Ollama local language models
- **`AzureOpenAILangExtractRecognizer`**: Concrete implementation for Azure OpenAI Service

[OllamaLangExtractRecognizer implementation](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/third_party/ollama_langextract_recognizer.py) | [AzureOpenAILangExtractRecognizer implementation](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/predefined_recognizers/third_party/azure_openai_langextract_recognizer.py)

---

## Using Ollama (Local Models)

### Prerequisites
## How to integrate Language Model-based detection into Presidio

### Option 1: Enable in Configuration (Recommended)

1. **Install Presidio with LangExtract support**:
   ```sh
   pip install presidio-analyzer[langextract]
   ```

2. **Set up Ollama** - Choose one option:

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

3. **Configuration** (optional): Create your own `ollama_config.yaml` or use the [default configuration](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/ollama_config.yaml)

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

### Configuration Options

The `langextract_config_ollama.yaml` file supports the following options:

- **`model_id`**: The Ollama model to use (default: `"gemma2:2b"`)
- **`model_url`**: Ollama server URL (default: `"http://localhost:11434"`)
- **`temperature`**: Model temperature for generation (default: `null` for model default)
- **`supported_entities`**: PII/PHI entity types to detect
- **`entity_mappings`**: Map LangExtract entity classes to Presidio entity names
- **`min_score`**: Minimum confidence score (default: `0.5`)

See the [configuration file](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/ollama_config.yaml) for all options.
## Troubleshooting

**ConnectionError: "Ollama server not reachable"**
- Ensure Ollama is running: `docker ps` or check `http://localhost:11434`
- Verify the `model_url` in your configuration matches your Ollama server address

**RuntimeError: "Model 'gemma2:2b' not found"**
- Pull the model: `docker exec -it presidio-ollama-1 ollama pull gemma2:2b`
- Or for manual setup: `ollama pull gemma2:2b`
- Verify the model name matches the `model_id` in your configuration


---

## Using Azure OpenAI (Cloud Models)

Azure OpenAI provides cloud-based access to OpenAI models (GPT-4o, GPT-4, GPT-3.5-turbo) with enterprise security and compliance features.

### Prerequisites

1. **Install Presidio with LangExtract support**:
   ```sh
   pip install presidio-analyzer[langextract]
   ```
   
   This installs `langextract[openai]` which includes the OpenAI Python SDK and Azure Identity libraries.

2. **Azure Subscription**: Create one at [azure.microsoft.com](https://azure.microsoft.com)

3. **Azure OpenAI Resource**:
   - Create an Azure OpenAI resource in [Azure Portal](https://portal.azure.com)
   - Request access if needed (some regions require approval)
   - Deploy a model (e.g., "gpt-4o", "gpt-4", "gpt-35-turbo")

### Authentication Options

Azure OpenAI supports two authentication methods:

#### Option 1: API Key (Quick Start)

Simple authentication for development and testing:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import AzureOpenAILangExtractRecognizer

# Initialize with API key
azure_openai = AzureOpenAILangExtractRecognizer(
    model_id="gpt-4o",
    endpoint="https://your-resource.openai.azure.com/",
    api_key="your-api-key-here"
)

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(azure_openai)

results = analyzer.analyze(
    text="My email is john.doe@example.com and my phone is 555-123-4567",
    language="en"
)
```

#### Option 2: Managed Identity (Production Recommended)

**More secure** - No API keys in code, uses Azure RBAC:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import AzureOpenAILangExtractRecognizer

# Initialize with Managed Identity (no api_key parameter)
azure_openai = AzureOpenAILangExtractRecognizer(
    model_id="gpt-4o",
    endpoint="https://your-resource.openai.azure.com/"
    # No api_key - automatically uses managed identity
)

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(azure_openai)

results = analyzer.analyze(
    text="Patient John Smith has SSN 123-45-6789",
    language="en"
)
```

**Managed Identity Authentication Flow** (Production):

When `api_key` is not provided, the provider automatically uses `ChainedTokenCredential` which tries credentials in order:

1. **EnvironmentCredential** - Service principal from environment variables
2. **WorkloadIdentityCredential** - Azure Kubernetes Service workload identity
3. **ManagedIdentityCredential** - Azure VM/App Service managed identity

For local development, set `ENV=development` to use `DefaultAzureCredential` instead:

```python
import os
os.environ["ENV"] = "development"

# Now uses DefaultAzureCredential (includes Azure CLI, VS Code, etc.)
# No api_key needed
azure_openai = AzureOpenAILangExtractRecognizer(
    model_id="gpt-4o",
    endpoint="https://your-resource.openai.azure.com/"
)
```

**Setup Managed Identity**:

1. Enable managed identity on your Azure resource (VM, App Service, Container Instance, etc.)
2. Grant the managed identity **"Cognitive Services OpenAI User"** role on your Azure OpenAI resource
3. No API keys needed - authentication is automatic

See [Azure Managed Identity documentation](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview) for details.

### Using Configuration File

Create `azure_openai_config.yaml`:

```yaml
langextract:
  prompts:
    - "Extract and label ALL PII/PHI entities"
  examples:
    - text: "Contact John at john@example.com"
      entities:
        - value: "John"
          label: "PERSON"
        - value: "john@example.com"
          label: "EMAIL_ADDRESS"
  entity_mappings:
    person: PERSON
    email: EMAIL_ADDRESS
    phone_number: PHONE_NUMBER
    # Add more mappings as needed

azure_openai:
  model_id: "gpt-4o"  # or gpt-4, gpt-35-turbo
  endpoint: "https://your-resource.openai.azure.com/"
  
  # Authentication: Choose one option
  # Option 1: API Key (for development/quick start)
  api_key: "${AZURE_OPENAI_API_KEY}"  # Use environment variable
  
  # Option 2: Managed Identity (for production - leave api_key as null)
  # api_key: null  # When null/unset, automatically uses ChainedTokenCredential
  
  # Optional parameters
  api_version: "2024-02-15-preview"
  temperature: 0.0
  max_tokens: 2000
```

Load configuration:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.predefined_recognizers.third_party.azure_openai_langextract_recognizer import AzureOpenAILangExtractRecognizer

# Load from configuration file
azure_openai = AzureOpenAILangExtractRecognizer(
    config_file_path="azure_openai_config.yaml"
)

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(azure_openai)
```

See the [default configuration file](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/azure_openai_config.yaml) for all options.

### Configuration Options

Customize the recognizer in the `azure_openai_config.yaml` file:

- `model_id`: Azure OpenAI deployment name (e.g., "gpt-4o", "gpt-4", "gpt-35-turbo")
- `endpoint`: Azure OpenAI resource endpoint URL
- `api_key`: API key for authentication (use environment variable: `${AZURE_OPENAI_API_KEY}`). If not provided (null), automatically uses managed identity.
- `api_version`: Azure OpenAI API version (default: "2024-02-15-preview")
- `temperature`: Model temperature for response generation (0.0 = deterministic)
- `max_tokens`: Maximum tokens in response
- `supported_entities`: PII/PHI entity types to detect
- `entity_mappings`: Map LangExtract entities to Presidio entity names
- `min_score`: Minimum confidence score

---

## Choosing Between Ollama and Azure OpenAI

| Feature | Ollama | Azure OpenAI |
|---------|--------|--------------|
| **Deployment** | Local (on-premises) | Cloud (Azure) |
| **Cost** | Free (hardware required) | Pay-per-use (tokens) |
| **Models** | Open-source (Gemma, Llama, etc.) | GPT-4o, GPT-4, GPT-3.5-turbo |
| **Privacy** | Complete data control | Microsoft Azure compliance |
| **Setup** | Docker/local installation | Azure Portal + API key/Managed Identity |
| **Authentication** | None (local) | API Key or Managed Identity (RBAC) |
| **Best For** | Development, on-premises requirements | Production, enterprise compliance |

**Recommendations**:
- **Use Ollama** for local development, testing, or when data must stay on-premises
- **Use Azure OpenAI** for production workloads requiring enterprise security, compliance (HIPAA, SOC 2, etc.), and managed infrastructure