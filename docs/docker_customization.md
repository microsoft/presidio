# Customizing Presidio Docker Images

## Overview

This guide provides detailed instructions on how to build and customize Presidio Docker images to support additional languages and custom configurations. The official Presidio Docker images support English by default, but you can create custom images to work with other languages.

## Prerequisites

- Docker installed ([Download Docker](https://docs.docker.com/get-docker/))
- Basic knowledge of Docker and YAML
- Familiarity with spaCy language models

## Understanding Presidio's Docker Architecture

Presidio consists of three main Docker images:
- `presidio-analyzer`: Detects PII entities in text
- `presidio-anonymizer`: Anonymizes detected PII
- `presidio-image-redactor`: Redacts PII from images

For multi-language support, you'll primarily need to customize the `presidio-analyzer` image.

## Step 1: Clone the Presidio Repository

First, clone the Presidio repository:

```bash
git clone https://github.com/microsoft/presidio.git
cd presidio
```

## Step 2: Locate Configuration Files

The key files for customization are:

- `presidio-analyzer/Dockerfile`: Defines the analyzer Docker image
- `presidio-analyzer/presidio_analyzer/conf/default_recognizers.yaml`: Configures recognizers

## Step 3: Modify the Dockerfile for Additional Languages

Navigate to `presidio-analyzer/Dockerfile` and add your desired spaCy language models.

### Example: Adding Spanish Support

In the Dockerfile, locate the section where spaCy models are downloaded and add:

```dockerfile
RUN python -m spacy download es_core_news_md
```

### Example: Adding Multiple Languages

```dockerfile
# Install language models
RUN python -m spacy download en_core_web_lg
RUN python -m spacy download es_core_news_md  # Spanish
RUN python -m spacy download fr_core_news_md  # French
RUN python -m spacy download de_core_news_md  # German
```

## Step 4: Configure Language Support

### Update Configuration File

Modify the recognizers configuration to support your languages. Edit `presidio-analyzer/presidio_analyzer/conf/default_recognizers.yaml`:

```yaml
# Add supported languages
supported_languages:
  - en
  - es
  - fr
  - de
```

## Step 5: Build the Custom Docker Image

Build your customized Docker image:

```bash
cd presidio-analyzer
docker build . -t presidio-analyzer-custom:latest
```

## Step 6: Run Your Custom Image

Run the custom image:

```bash
docker run -d -p 5002:3000 presidio-analyzer-custom:latest
```

## Common Pitfalls and Best Practices

### 1. Memory Issues with Multiple Languages

**Problem**: Adding 10+ languages at once can cause the Docker image to run out of memory during build or runtime.

**Solutions**:
- Use smaller spaCy models (e.g., `es_core_news_sm` instead of `es_core_news_lg`)
- Increase Docker memory allocation:
  ```bash
  docker run -d -p 5002:3000 --memory="4g" presidio-analyzer-custom:latest
  ```
- Build images with only the languages you actually need
- Consider using transformers models which can be more memory-efficient

### 2. Warning: NLP Recognizer Not in List

If you see warnings like:
```
UserWarning: NLP recognizer (e.g. SpacyRecognizer, StanzaRecognizer) is not in the list of recognizers for language en.
```

**Solution**: Ensure your language configuration matches your installed models:

1. Check `default_recognizers.yaml` includes your language
2. Verify the spaCy model is properly downloaded in the Dockerfile
3. Ensure the language code matches (e.g., 'en' for English, 'es' for Spanish)

### 3. Model Size vs. Accuracy Trade-off

spaCy offers different model sizes:
- `sm` (small): ~15MB, faster but less accurate
- `md` (medium): ~40MB, balanced
- `lg` (large): ~500MB+, most accurate but resource-intensive

**Recommendation**: Start with `md` models for a good balance.

## Complete Example: Building a Multi-Language Analyzer

Here's a complete example for Spanish and French support:

### Modified Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /usr/bin/presidio-analyzer

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install spaCy language models
RUN python -m spacy download en_core_web_lg
RUN python -m spacy download es_core_news_md
RUN python -m spacy download fr_core_news_md

# Copy application code
COPY . .

EXPOSE 3000

CMD ["python", "app.py"]
```

### Test Your Custom Image

```bash
# Build the image
docker build -t my-presidio-analyzer .

# Run the container
docker run -d -p 5002:3000 my-presidio-analyzer

# Test with curl
curl -X POST http://localhost:5002/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Mi nombre es David y mi email es david@example.com", "language": "es"}'
```

## Using Docker Compose

For complex setups, use docker-compose.yml:

```yaml
version: '3.8'
services:
  presidio-analyzer:
    build:
      context: ./presidio-analyzer
    ports:
      - "5002:3000"
    environment:
      - LOG_LEVEL=INFO
    deploy:
      resources:
        limits:
          memory: 4G
  
  presidio-anonymizer:
    image: mcr.microsoft.com/presidio-anonymizer:latest
    ports:
      - "5001:3000"
```

Run with:
```bash
docker-compose up --build
```

## Additional Resources

- [Presidio Analyzer Documentation](https://microsoft.github.io/presidio/analyzer/)
- [spaCy Language Models](https://spacy.io/models)
- [Presidio Custom Recognizers](https://microsoft.github.io/presidio/analyzer/adding_recognizers/)
- [Analyzer Engine Provider](https://microsoft.github.io/presidio/analyzer/analyzer_engine_provider/)

## Troubleshooting

### Issue: Build fails with "No space left on device"
**Solution**: Clean up Docker resources:
```bash
docker system prune -a
```

### Issue: Container crashes on startup
**Solution**: Check logs and increase memory:
```bash
docker logs <container-id>
docker run --memory="6g" ...
```

## Contributing

For questions or contributions, please refer to the [Presidio Contributing Guide](https://github.com/microsoft/presidio/blob/main/CONTRIBUTING.md).

## Related Documentation

- [Installation Guide](./installation.md)
- [Getting Started with Presidio](./getting_started/getting_started_text.md)
- [Supported Languages](https://microsoft.github.io/presidio/analyzer/languages/)

This guide addresses [Issue #1663](https://github.com/microsoft/presidio/issues/1663) - More elaborate description for building custom Docker images for Presidio.
