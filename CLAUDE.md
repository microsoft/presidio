# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo Layout

Presidio is a monorepo of independent Python packages, each in its own directory with its own `pyproject.toml` and `tests/` folder:

- `presidio-analyzer/` — detects PII entities in text (core package)
- `presidio-anonymizer/` — replaces detected PII with redacted/encrypted/masked values
- `presidio-image-redactor/` — redacts PII from images (standard + DICOM)
- `presidio-structured/` — PII de-identification in structured data (DataFrames, JSON)
- `presidio-cli/` — CLI wrapper
- `e2e-tests/` — end-to-end tests requiring a running cluster (docker-compose)

Each package is independent: install and test them separately from within their directory.

## Development Commands

All commands run from the individual package directory (e.g., `presidio-analyzer/`).

```sh
# Install all dependencies including dev extras
poetry install --all-extras

# Download the default spaCy model (required for analyzer)
poetry run python install_nlp_models.py

# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_analyzer_engine.py

# Run a single test by name
poetry run pytest tests/test_analyzer_engine.py::test_when_analyze_called_then_all_pii_entities_found

# Lint
poetry run ruff check

# Format
poetry run ruff format
```

Pre-commit hooks (optional but enforced in CI): `pre-commit install` from the repo root.

PRs require ≥ 90% coverage on changed lines (`diff-cover` is used).

## Analyzer Architecture

`AnalyzerEngine` (`presidio_analyzer/analyzer_engine.py`) is the entry point. It orchestrates:

1. **NLP Engine** (`nlp_engine/`) — runs spaCy (default), Stanza, or Transformers to produce `NlpArtifacts` (tokens, entities, lemmas). Configured via YAML files in `presidio_analyzer/conf/` (e.g., `default.yaml`, `spacy.yaml`, `transformers.yaml`). `NlpEngineProvider` loads the correct engine from config.

2. **RecognizerRegistry** (`recognizer_registry/`) — holds all active recognizers. `RecognizerRegistryProvider` loads them from `conf/default_recognizers.yaml` or a custom YAML.

3. **Recognizers** (`predefined_recognizers/`) — each detects one or more PII entity types:
   - `generic/` — entity-agnostic (credit cards, email, phone, URL, IP, etc.)
   - `country_specific/<country>/` — country-scoped IDs, licenses, SSNs, etc. (disabled by default in YAML config)
   - `nlp_engine_recognizers/` — `SpacyRecognizer`, `StanzaRecognizer`, `TransformersRecognizer` wrap NLP model output
   - `ner/` — standalone NER models: `HuggingFaceNerRecognizer`, `GlinerRecognizer`, `MedicalNerRecognizer`
   - `third_party/` — `LangExtractRecognizer`, `AzureOpenAILangExtractRecognizer`, `AzureAILanguage`, `AhdsRecognizer`

4. **ContextAwareEnhancer** — boosts/lowers confidence scores based on surrounding words (`LemmaContextAwareEnhancer` is the default).

### Class Hierarchy for Recognizers

```
EntityRecognizer (abstract)
  └─ LocalRecognizer
       └─ PatternRecognizer   ← regex + deny-list, the base for most predefined recognizers
  └─ RemoteRecognizer         ← calls an external HTTP service
```

`PatternRecognizer` accepts `Pattern` objects (regex + score) and/or `deny_list`.

## Adding a New Recognizer

1. Place the file under the correct subfolder of `predefined_recognizers/`.
2. Register it in `presidio_analyzer/conf/default_recognizers.yaml` (set `enabled: false` for country-specific by default).
3. Export it from `predefined_recognizers/__init__.py` and add to `__all__`.
4. Add a test file `tests/test_<recognizer_name>.py` following the pattern `test_when_<condition>_then_<expected>`.
5. For regex-based recognizers: document the source/reference for the pattern in a comment.

## Anonymizer Architecture

`AnonymizerEngine` (`presidio_anonymizer/anonymizer_engine.py`) takes `RecognizerResult` objects from the analyzer and applies operators to the matched spans:

- **Operators** (`operators/`): `Replace`, `Redact`, `Mask`, `Hash`, `Encrypt`/`Decrypt` (AES-CBC), `Keep`, `Custom`. `OperatorsFactory` resolves the right operator by name.
- `DeanonymizeEngine` reverses encryption-based anonymization.
- `BatchAnonymizerEngine` handles dict/list inputs.

## YAML Configuration

The NLP engine and recognizer registry are both fully YAML-configurable:

- `presidio_analyzer/conf/default.yaml` — NLP engine (spaCy by default)
- `presidio_analyzer/conf/default_recognizers.yaml` — which recognizers to load and their per-language context words
- Other configs: `transformers.yaml`, `stanza.yaml`, `slim.yaml`, `spacy_multilingual.yaml`

Pass a config file path to `AnalyzerEngineProvider` or `RecognizerRegistryProvider` to use a custom setup without code changes.

## Test Conventions

- Test names: `test_when_<condition>_then_<expected_behavior>`
- Mocks live in `tests/mocks/` (e.g., `NlpEngineMock`, `RecognizerRegistryMock`)
- Integration tests use `@pytest.mark.integration`; API-layer tests use `@pytest.mark.api`
- e2e tests require the full docker-compose cluster to be running

## Linting / Style

- `ruff` enforces PEP 8, pep8-naming, and NumPy-style docstrings (`D` rules)
- Line length: 88 (Black-compatible)
- Tests directory is excluded from ruff checks
- `ruff format` is the auto-formatter (Black-compatible double quotes, spaces)
