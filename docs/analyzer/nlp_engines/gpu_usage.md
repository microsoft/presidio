# GPU Acceleration

Presidio supports GPU acceleration for transformer-based NLP models, which can significantly improve performance when processing large volumes of text.

!!! note "How GPU Support Works"
    GPU acceleration is handled by the underlying NLP frameworks (spaCy, PyTorch/Transformers). Presidio automatically detects available GPU hardware and configures these frameworks to use it. No additional code changes are required.

## Prerequisites

### Hardware Requirements

Presidio supports the following hardware acceleration:

- **NVIDIA GPU**: CUDA Toolkit 11.x or 12.x
- **Apple Silicon**: MPS (Metal Performance Shaders) on M1/M2/M3
- **CPU**: Automatic fallback when GPU is unavailable

### Software Dependencies

=== "NVIDIA GPU"

    ```bash
    # Install presidio with GPU support
    pip install "presidio-analyzer[gpu]"
    
    # Alternatively, install dependencies separately
    pip install cupy-cuda12x  # For CUDA 12.x (or cupy-cuda11x for CUDA 11.x)
    pip install torch --index-url https://download.pytorch.org/whl/cu121  # PyTorch with CUDA
    
    # Download spaCy transformer model
    python -m spacy download en_core_web_trf
    ```

=== "Apple Silicon"

    ```bash
    # No additional dependencies required
    pip install presidio-analyzer
    
    # Download spaCy transformer model
    python -m spacy download en_core_web_trf
    ```

=== "Transformers"

    ```bash
    # For Hugging Face transformers
    pip install "presidio-analyzer[transformers]"
    
    # Download a small spaCy model for tokenization
    python -m spacy download en_core_web_sm
    ```

!!! tip "Tip"
    Use `pip install "presidio-analyzer[gpu]"` to install commonly used GPU dependencies. Ensure the CUDA version matches your system installation.

## Automatic GPU Detection

Presidio automatically detects and uses available GPU hardware through the `DeviceDetector` module. The detection hierarchy is:

1. CUDA (NVIDIA GPU)
2. MPS (Apple Silicon)
3. CPU (fallback)

No configuration is required. When initializing an NLP engine, Presidio:

- Detects available GPU hardware
- Configures the model to use GPU if available
- Falls back to CPU if no GPU is detected

Code examples work identically across GPU and CPU environments.

## Usage

### spaCy Transformer Models

For spaCy's transformer models like `en_core_web_trf`, GPU is automatically used when available:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Configure spaCy transformer model
configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_trf"}],
}

provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

# GPU will be used automatically if available
results = analyzer.analyze(
    text="My name is John Doe and my email is john@example.com",
    language="en"
)

print(results)
```

!!! tip "Tip"
    The `en_core_web_trf` model uses a transformer architecture (RoBERTa) and benefits significantly from GPU acceleration. For best results, ensure CUDA and cupy are installed.

### Hugging Face Transformers

For Hugging Face models, use `TransformersNlpEngine`:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import TransformersNlpEngine

# Configure transformer model
model_config = [{
    "lang_code": "en",
    "model_name": {
        "spacy": "en_core_web_sm",  # for tokenization and lemmatization
        "transformers": "StanfordAIMI/stanford-deidentifier-base"  # for NER
    }
}]

# Create engine - GPU will be used automatically
nlp_engine = TransformersNlpEngine(models=model_config)
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

# Process text on GPU
results = analyzer.analyze(
    text="Patient John Doe was admitted on 01/15/2024",
    language="en"
)

print(results)
```

**Popular Hugging Face models:**

- `dslim/bert-base-NER` - General NER
- `obi/deid_roberta_i2b2` - Medical de-identification  
- `StanfordAIMI/stanford-deidentifier-base` - Medical PII

See [Hugging Face models](https://huggingface.co/models?pipeline_tag=token-classification) for more options.

### Checking if GPU is being used

The easiest way to verify GPU usage is to check PyTorch:

```python
import torch

if torch.cuda.is_available():
    print("GPU available: CUDA")
    print(f"Device: {torch.cuda.get_device_name(0)}")
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    print("GPU available: MPS (Apple Silicon)")
else:
    print("Using CPU")
```

You can also monitor GPU usage in your terminal:

```bash
# For NVIDIA GPUs
watch -n 1 nvidia-smi

# For Apple Silicon
sudo powermetrics --samplers gpu_power
```

### Processing multiple texts

When processing batches of text, GPU acceleration provides significant performance improvements:

```python
texts = [
    "My name is Sarah",
    "Contact me at bob@company.com",
    "My phone is 555-1234",
    # ... more texts
]

for text in texts:
    results = analyzer.analyze(text=text, language="en")
    # Process results...
```

## GPU-Enabled NLP Engines

The following NLP engines support GPU acceleration:

| Engine | GPU Support | Performance Gain |
|--------|-------------|------------------|
| **Transformers** | ✅ Full | 4-10x faster |
| **GLiNER** | ✅ Full | 5-7x faster |
| **Stanza** | ✅ Full | 1.3-4x faster |
| **spaCy (transformer models)** | ✅ Full | Significant improvement |
| **spaCy (standard models)** | ⚠️ Limited | Minimal to negative impact |

!!! warning "Warning"
    Standard spaCy models (e.g., `en_core_web_lg`) may perform worse on GPU due to overhead. Use GPU primarily for transformer-based models.

## When to Use GPU

GPU acceleration is recommended for:

- Transformer-based models (`TransformersNlpEngine`, `en_core_web_trf`)
- Large-scale batch processing (100+ documents)
- Long documents (1000+ tokens)
- Production workloads with high throughput requirements

CPU is sufficient for:

- Standard spaCy models
- Small batches (< 50 documents)
- Short texts (< 200 tokens)
- Development and testing environments

## Performance Considerations

Transformer models require substantial GPU memory:

- `en_core_web_trf` uses around 500MB
- Start with smaller batches if you hit memory limits
- Keep an eye on `nvidia-smi` to see memory usage

!!! warning "Memory"
    If you get "CUDA out of memory" errors, try processing fewer documents at a time.

## Troubleshooting

### GPU not being detected

If Presidio is not using your GPU:

1. Check CUDA is installed:
   ```bash
   nvidia-smi
   nvcc --version
   ```

2. Verify cupy can see your GPU:
   ```python
   import cupy as cp
   print(cp.cuda.runtime.getDeviceCount())  # Should be > 0
   ```

3. Make sure cupy version matches CUDA version:
   ```bash
   pip uninstall cupy cupy-cuda11x cupy-cuda12x
   pip install cupy-cuda12x  # or cupy-cuda11x
   ```

### Out of memory errors

If you see `RuntimeError: CUDA out of memory`:

- Process fewer texts at once
- Try a smaller model (`en_core_web_sm` instead of `en_core_web_trf`)
- Clear GPU cache:
  ```python
  import torch
  torch.cuda.empty_cache()
  ```

### GPU is slow

For small batches, GPU overhead may result in slower performance than CPU. If experiencing slow performance:

- Increase batch size
- Make sure you're processing enough text to benefit from GPU
- Check if data transfer is the bottleneck

### CPU fallback

Presidio will automatically use CPU if:

- No GPU is detected
- CUDA or cupy are not installed
- GPU initialization fails

This ensures code portability across different environments.

## Additional Resources

For more information on GPU usage and transformer models:

- [spaCy: GPU Usage](https://spacy.io/usage/embeddings-transformers#gpu)
- [NVIDIA CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
- [cupy Documentation](https://docs.cupy.dev/en/stable/install.html)

Related Presidio documentation:

- [Transformer Models in Presidio](transformers.md)
- [spaCy and Stanza Models](spacy_stanza.md)
- [Customizing NLP Models](../customizing_nlp_models.md)
