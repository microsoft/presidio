# Microsoft Presidio Development Instructions

Microsoft Presidio is a Python-based data protection and de-identification SDK with multiple components for detecting and anonymizing PII (Personally Identifiable Information) in text and images.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Initial Setup and Dependencies
- Install Poetry (Python package manager): `pip install poetry`
- Ensure Python 3.9-3.12 is available
- Install Docker for containerized deployment
- Install ruff for linting: `pip install ruff`

### Build Process (Poetry-based Development)
**CRITICAL: Set timeouts appropriately and NEVER CANCEL long-running operations.**

#### Presidio Analyzer (PII Detection)
```bash
cd presidio-analyzer
poetry install --all-extras  # Takes ~5 minutes. NEVER CANCEL. Set timeout to 10+ minutes.
poetry run python -m spacy download en_core_web_lg  # Takes ~30 seconds. NEVER CANCEL.
poetry run python -m spacy download en_core_web_sm  # Takes ~30 seconds. NEVER CANCEL.
poetry run pytest -vv  # Takes ~2 minutes. NEVER CANCEL. Set timeout to 5+ minutes.
```

#### Presidio Anonymizer (PII Anonymization)
```bash
cd presidio-anonymizer
poetry install --all-extras  # Takes ~10 seconds
poetry run pytest -vv  # Takes ~5 seconds, all tests should pass
```

#### Presidio CLI (Command-line Interface)
```bash
cd presidio-cli
poetry install  # Takes ~15 seconds
poetry run python -m spacy download en_core_web_lg  # Required for CLI functionality
poetry run pytest -vv  # Takes ~40 seconds. NEVER CANCEL.
```

### Docker Deployment (Recommended for Production Testing)
**NEVER CANCEL: Docker operations can take 10-15 minutes depending on network**

#### Using Pre-built Images (Recommended)
```bash
# Pull official images - Takes ~3 minutes. NEVER CANCEL. Set timeout to 10+ minutes.
docker pull mcr.microsoft.com/presidio-analyzer:latest
docker pull mcr.microsoft.com/presidio-anonymizer:latest

# Run containers
docker run -d -p 5002:3000 --name presidio-analyzer mcr.microsoft.com/presidio-analyzer:latest
docker run -d -p 5001:3000 --name presidio-anonymizer mcr.microsoft.com/presidio-anonymizer:latest

# Wait for services to start (~20 seconds)
sleep 20

# Test health endpoints
curl http://localhost:5002/health  # Should return "Presidio Analyzer service is up"
curl http://localhost:5001/health  # Should return "Presidio Anonymizer service is up"
```

#### Building from Source (May fail in restricted environments)
```bash
# This may fail due to SSL/network issues in sandboxed environments
docker compose up --build -d  # Takes 10-15 minutes if successful. NEVER CANCEL.
```

### Linting and Code Quality
```bash
# Run from repository root
ruff check .  # Takes <5 seconds, should pass with "All checks passed!"
```

## Validation Scenarios

**CRITICAL: Always test actual functionality after making changes. Build success alone is insufficient.**

### 1. CLI Functionality Test
```bash
cd presidio-cli
echo "My name is John Doe and my phone number is 555-123-4567" > /tmp/test.txt
poetry run presidio /tmp/test.txt
# Expected: Detects PERSON and PHONE_NUMBER entities
```

### 2. REST API Functionality Test (Requires running containers)
```bash
# Test PII Analysis
curl -X POST http://localhost:5002/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "My name is John Doe and my email is john@example.com", "language": "en"}'
# Expected: Returns JSON array with detected entities (PERSON, EMAIL_ADDRESS)

# Test PII Anonymization
curl -X POST http://localhost:5001/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My name is John Doe",
    "analyzer_results": [{"entity_type": "PERSON", "start": 11, "end": 19, "score": 0.85}]
  }'
# Expected: Returns anonymized text with "<PERSON>" replacement
```

### 3. End-to-End Integration Test
Always test the complete analyze -> anonymize pipeline:
1. Use analyzer API to detect PII entities
2. Use anonymizer API with detected entities to anonymize text
3. Verify anonymization quality and entity coverage

## Common Issues and Solutions

### Network/SSL Issues
- Docker builds may fail in restricted environments due to SSL certificate verification
- Use pre-built images: `mcr.microsoft.com/presidio-analyzer:latest` and `mcr.microsoft.com/presidio-anonymizer:latest`
- Transformers tests may fail due to HuggingFace connectivity - this is expected in restricted networks

### Build Failures
- If Poetry install fails, ensure Python 3.9-3.12 is available
- If spaCy model downloads fail, check internet connectivity
- Use `poetry run` prefix for all commands within Poetry environments

### Test Failures
- AHDS tests skip when `AHDS_ENDPOINT` environment variable not set - this is expected
- Some transformers tests fail without HuggingFace access - this is expected
- Core analyzer tests should have 900+ passing tests
- All anonymizer tests (266) should pass
- All CLI tests (23) should pass

## Repository Structure

### Core Components
- `presidio-analyzer/` - PII detection engine (most complex, requires spaCy models)
- `presidio-anonymizer/` - PII anonymization engine (lightweight, fast)
- `presidio-cli/` - Command-line interface for PII detection
- `presidio-image-redactor/` - Image PII redaction capabilities
- `presidio-structured/` - Structured data PII handling

### Configuration and Documentation
- `.github/` - GitHub workflows and configuration
- `docs/` - Comprehensive documentation
- `e2e-tests/` - End-to-end integration tests
- `pyproject.toml` - Root configuration for ruff linting
- `docker-compose.yml` - Multi-service container orchestration

## Expected Build Times and Timeouts

**CRITICAL: Always set appropriate timeouts and include "NEVER CANCEL" warnings**

| Operation | Expected Time | Minimum Timeout | Command |
|-----------|---------------|-----------------|---------|
| Analyzer Poetry Install | 5 minutes | 10 minutes | `poetry install --all-extras` |
| SpaCy Model Downloads | 1 minute | 3 minutes | `python -m spacy download en_core_web_lg` |
| Analyzer Tests | 2 minutes | 5 minutes | `poetry run pytest -vv` |
| Docker Image Pulls | 3 minutes | 10 minutes | `docker pull mcr.microsoft.com/presidio-*` |
| Docker Builds | 15 minutes | 30 minutes | `docker compose up --build` |
| Service Startup | 20 seconds | 60 seconds | Container readiness |

## CI/CD Integration Notes
- Repository uses Azure Pipelines for CI/CD
- Linting with ruff is required and enforced
- Multi-Python version testing (3.9, 3.10, 3.11, 3.12)
- Tests include unit tests, integration tests, and security analysis
- Docker builds and e2e tests run in parallel

## Key Development Commands Reference

```bash
# Quick health check of all components
cd presidio-analyzer && poetry run pytest tests/test_analyzer_engine.py::test_simple
cd ../presidio-anonymizer && poetry run pytest tests/integration/test_anonymize_engine.py::test_given_name_and_phone_number_then_we_anonymize_correctly
cd ../presidio-cli && poetry run presidio --help

# Full validation pipeline
ruff check .  # Lint all code
cd presidio-analyzer && poetry install --all-extras && poetry run pytest
cd ../presidio-anonymizer && poetry install && poetry run pytest
cd ../presidio-cli && poetry install && poetry run pytest

# Container validation
docker pull mcr.microsoft.com/presidio-analyzer:latest && docker pull mcr.microsoft.com/presidio-anonymizer:latest
docker run -d -p 5002:3000 mcr.microsoft.com/presidio-analyzer:latest
docker run -d -p 5001:3000 mcr.microsoft.com/presidio-anonymizer:latest
sleep 20 && curl http://localhost:5002/health && curl http://localhost:5001/health
```

Always run these validation steps after making changes to ensure functionality is preserved.