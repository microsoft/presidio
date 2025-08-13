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

### 4. E2E Tests (Comprehensive Integration Testing)
**CRITICAL: Run comprehensive e2e tests for significant changes. Takes ~2 minutes. NEVER CANCEL.**

E2E tests validate REST API functionality and cross-service integration:

```bash
# First, ensure all services are running via docker-compose
docker-compose up --build -d  # Takes 10-15 minutes. NEVER CANCEL.
docker-compose ps  # Verify all services are up

# Set up e2e test environment (Takes ~30 seconds)
cd e2e-tests
python -m venv presidio-e2e  # Create virtualenv
source presidio-e2e/bin/activate  # On Windows: presidio-e2e\Scripts\activate
pip install -r requirements.txt  # Install test dependencies

# Run all e2e tests (Takes ~2 minutes. NEVER CANCEL. Set timeout to 5+ minutes.)
pytest -v

# Run specific test categories
pytest -m api -v          # API-only tests
pytest -m integration -v  # Cross-service integration tests

# Cleanup
deactivate
```

**E2E Test Categories:**
- `@pytest.mark.api` - Single service API tests
- `@pytest.mark.integration` - Multi-service integration flows
- Tests include: analyzer API, anonymizer API, image redactor API, end-to-end analyze→anonymize flows

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

### Samples and Examples
- `docs/samples/` - **Reference examples only, not official production code**
  - Python notebooks for various use cases (basic usage, customization, batch processing)
  - Deployment samples (Kubernetes, Spark, Azure services)
  - Integration examples (external services, transformers, custom recognizers)
  - **Use these for inspiration but validate approaches for production use**

### External Resources
- **presidio-research repository** - Additional samples, research datasets, and experimental features
  - Contains advanced examples and research-oriented implementations
  - May include experimental features not yet in main Presidio
  - Use as reference for advanced scenarios and research contexts

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
| E2E Test Suite | 2 minutes | 5 minutes | `pytest -v` from e2e-tests/ |

## Development Guidelines and Contribution Process

**CRITICAL: Follow these guidelines when contributing to Presidio. All changes require proper testing and documentation.**

### Before Making Changes
1. **Open a GitHub issue** suggesting the change before creating a PR
2. **Read CONTRIBUTING.md** for detailed contribution guidelines
3. **Follow the development process** documented in docs/development.md

### Code Quality Requirements  
- **All code must be tested** - Unit tests, integration tests, and e2e tests as appropriate
- **All code must be linted** - Use `ruff check .` from repository root
- **All code must be documented** - Include docstrings and update documentation
- **Use test naming convention** - `test_when_[condition]_then_[expected_behavior]`

### Pull Request Requirements
- **PR must be small** - Solve one issue at a time
- **Tests must pass** - CI pipeline (unit tests, e2e tests, linting) must succeed  
- **Two maintainer approvals** required for merge
- **Update CHANGELOG.md** under "Unreleased" section
- **Clear commit messages** explaining the changes made

### Adding New Recognizers (PII Detectors)
Follow best practices in docs/analyzer/developing_recognizers.md:

1. **Choose correct folder** in `presidio-analyzer/presidio_analyzer/predefined_recognizers/`:
   - `country_specific/<country>/` for region-specific recognizers
   - `generic/` for globally applicable recognizers  
   - `nlp_engine_recognizers/` for NLP-based recognizers
   - `ner/` for standalone NER models
   - `third_party/` for external service integrations

2. **Make regex patterns specific** to minimize false positives
3. **Document pattern sources** with comments linking to standards/references
4. **Add to configuration** in `conf/default_recognizers.yaml` (set `enabled: false` for country-specific)
5. **Update imports** in `predefined_recognizers/__init__.py`
6. **Add comprehensive tests** including edge cases
7. **Update supported entities documentation** if adding new entity types

### Local Development Setup
```bash
# Install Poetry and dependencies  
pip install poetry
pip install ruff

# Set up pre-commit hooks (recommended)
pip install pre-commit
pre-commit install  # Enables automatic formatting on commit

# Choose a component to work on
cd presidio-analyzer  # or presidio-anonymizer, presidio-cli
poetry install --all-extras  # NEVER CANCEL. Set timeout to 10+ minutes.
poetry run python -m spacy download en_core_web_lg  # For analyzer/CLI
```

### Testing Strategy
1. **Unit tests** - Test individual functions/classes with mocks
2. **Integration tests** - Test component integration, external packages
3. **E2E tests** - Test REST APIs and cross-service flows
4. **Manual validation** - Always test actual functionality beyond automated tests

### Linting and Formatting
```bash
# Check code style (required before PR)
ruff check .  # From repository root

# Auto-format code (if using pre-commit hooks)
git commit  # Will automatically format and re-commit if needed
```

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

# E2E testing workflow
docker-compose up --build -d  # Start all services
cd e2e-tests && python -m venv presidio-e2e && source presidio-e2e/bin/activate
pip install -r requirements.txt && pytest -v  # Run all e2e tests
```

## Reference Documentation Links

**Always consult these official documents for detailed guidance:**

- **CONTRIBUTING.md** - Complete contribution guidelines, PR process, CLA requirements
- **docs/development.md** - Comprehensive development setup, testing conventions, local build process
- **docs/analyzer/developing_recognizers.md** - Best practices for creating new PII recognizers
- **docs/analyzer/adding_recognizers.md** - Step-by-step guide for adding recognizers to Presidio
- **docs/supported_entities.md** - Current list of supported PII entity types
- **docs/samples/index.md** - Index of all available examples and use cases

Always run these validation steps after making changes to ensure functionality is preserved.