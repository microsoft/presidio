# Microsoft Presidio Development Instructions

Microsoft Presidio is a Python-based data protection and de-identification SDK with multiple components for detecting and anonymizing PII (Personally Identifiable Information) in text and images.

## Code Review Philosophy

* Only comment when you have HIGH CONFIDENCE (>80%) that an issue exists
* Be concise: one sentence per comment when possible
* Focus on actionable feedback, not observations

## Review Priorities

Focus on issues in this order of importance:

### 🔴 CRITICAL (Always Flag)

#### 1. Security & Privacy Vulnerabilities

**General Security:**
- Hardcoded secrets, API keys, credentials (especially for NLP model endpoints, cloud services)
- Command injection (especially in CLI component)
- Unsafe deserialization (pickle files, untrusted NLP models)
- Missing input validation on API endpoints (analyzer, anonymizer, image-redactor)
- Path traversal in file operations
- Insecure random number generation for fake data
- PII leakage in logs, error messages, or debug output - Never log detected PII values, only entity types and positions

#### 2. Correctness & Logic Errors

**PII Detection Accuracy:**
- **False positives** - E.g. overly broad regex patterns matching non-PII with high confidence scores
- **False negatives** - E.g. limited regex coverage missing valid PII formats, not handling common variations (e.g., "SSN: 123-45-6789" vs "123456789")
- **Incorrect entity boundaries** - E.g. off-by-one errors in start/end positions causing malformed anonymization
- **Context handling errors** - E.g. not respecting sentence/document boundaries, locale-specific formats
- **Confidence score miscalculation** - E.g. scores outside [0.0, 1.0], incorrect aggregation of multiple detection methods

**General Logic:**
- Race conditions in multi-threaded analysis
- Resource leaks (NLP models not released, file handles, network connections)
- Null/None handling in entity detection chains
- Incorrect error handling that silently fails to detect PII
- Adding state where unnecessary (Presidio is designed to be stateless for scalability)

#### 3. Performance Issues

**PII Detection Specific:**
- **Inefficient regex patterns** - Catastrophic backtracking (e.g., `(a+)+b` on "aaaa...a")
- **Redundant passes** - Running the same logic multiple times on same text
- **Unbounded batch processing** - Loading entire datasets into memory
- **Missing regex compilation caching** - Recompiling patterns on every call
- **Unnecessary model loads** - Loading the same model multiple times instead of reusing instances

**General Performance:**
- O(n²) or worse algorithms when O(n) exists
- Blocking I/O on critical API paths
- Missing database indexes for entity result storage
- Inefficient image processing (loading full image when bounding box would suffice)

### 🟡 IMPORTANT (Flag if Significant)

#### 4. Cross-Component Alignment & Integration

**Respect the Natural Data Flow:**
- Presidio follows a unidirectional flow: Analyzer → Anonymizer → Output. Within the analyzer, there's a natural flow from nlp_engine → recognizers → context.
- Downstream components (CLI, structured, image-redactor) consume analyzer/anonymizer, never the reverse
- Breaking this flow creates circular dependencies and tight coupling
- Changes should propagate forward through the data pipeline, not backward

**Module Reuse Guidelines:**
- Reuse code by importing from shared modules, not by copying code across components
- Shared data models (RecognizerResult, OperatorConfig) should be treated as contracts - changes require coordinated updates across all consumers
- When adding functionality, check if it belongs in an existing shared module rather than duplicating logic
- If multiple components need the same feature, extract it to a common location rather than implementing it multiple times
- Backward compatibility is critical when modifying shared modules - ensure existing consumers continue to work without changes

**Avoid Cross-Component Side Effects:**
- Changes to internal implementation should not affect other components' behavior
- Modifying shared configuration files requires understanding impact on all components that consume them
- Registry and provider patterns exist to decouple components - bypassing them creates hidden dependencies
- Component boundaries must be respected: anonymizer should never import from analyzer internals, only public interfaces
- Providing a solution specific to one component in a shared module instead of providing a general solution that can be used by multiple components creates tight coupling and maintenance challenges

**When Making Changes Across Components:**
- Identify all components that consume the interface you're modifying
- Update dependent components in the same changeset to maintain system consistency
- Ensure configuration files, API schemas, and documentation stay synchronized
- Test the complete integration path, not just individual components in isolation in unit tests, integration tests, and the e2e test suite
- Communicate changes clearly in the PR description, especially if they affect multiple components or require coordinated

#### 5. Architecture & Design

**Presidio Patterns:**
- **Recognizer design violations** - Not inheriting from `EntityRecognizer`, missing `load()` or `analyze()`
- **Operator design violations** - Not implementing `OperatorType` interface correctly
- **Registry pattern misuse** - Bypassing `RecognizerRegistry`, hardcoding recognizer lists
- **Provider pattern violations** - Not following `NlpEngineProvider` or `RecognizerRegistryProvider` patterns
- **Tight coupling** - Recognizers depending on specific NLP engine implementation details

**General Design:**
- Circular dependencies between modules
- Missing abstraction for third-party service integrations
- Breaking existing public APIs without deprecation warnings
- Inconsistent error handling strategies (mixing exceptions and error codes)

#### 6. Data Integrity & Validation

**Input Validation:**
- Missing validation of user-provided entity types
- Accepting arbitrary regex patterns without safety checks
- No length limits on input text (DoS via memory exhaustion)
- Missing validation of parameters
- Unchecked file uploads

**Output Validation:**
- Confidence scores outside valid range
- Overlapping entity spans not handled correctly
- Missing entity type in anonymization results

#### 7. Testing Requirements

**Presidio-Specific Testing:**
- **Missing tests for new recognizers** - Must include: true positives, true negatives, edge cases, false positive scenarios, entity within larger context
- **No validation of entity boundaries** - Tests only check entity type, not exact start/end positions
- **Missing multilingual tests** - Recognizers claiming multi-language support without language-specific tests

**General Testing:**
- Missing tests for critical business logic (PII detection, anonymization)
- Flaky tests due to non-deterministic NLP/ML models (use fixed random seeds)
- Tests that don't validate behavior (checking implementation details instead)
- Missing regex pattern edge cases (empty strings, special characters, unicode)

#### 8. Documentation Requirements

**Code-Documentation Consistency:**
- Code changes must be reflected in documentation - outdated docs are misleading and dangerous
- Implementation must not contradict existing documentation - if conflict exists, either update docs or reconsider implementation
- API documentation is auto-generated from docstrings - formatting errors break the build

**Docstring Quality:**
- All public classes, methods, and functions must have docstrings
- Docstrings must follow consistent format (Args, Returns, Raises, Examples)
- No formatting issues that break API doc generation (malformed RST/Markdown, incorrect indentation)
- Include type information in docstrings when not obvious from type hints

**Documentation for New Features:**
- New recognizers must document pattern sources - link to official standards, government specifications, or authoritative references
- Complex additions require usage examples in `docs/samples/` - show common use cases, not just API reference
- New entity types must be added to `docs/supported_entities.md` with description and example
- API changes require updates to `docs/api-docs/api-docs.yml` (OpenAPI schema)

**Pattern Recognizer Documentation:**
- Explain the logic source: "Based on ISO standard X", "Follows format defined by Y government agency"
- Document regex pattern rationale - why specific character classes, lookaheads, or groups are needed
- Include references to validation algorithms (e.g., "Luhn checksum validation per ISO/IEC 7812")
- Note any limitations or known edge cases in the pattern

### 💡 OPTIONAL (Low Priority)

#### 9. Code Quality (only if impacts maintainability)

- Overly complex recognizer logic (>50 lines in `analyze()` method, >3 nesting levels)
- Misleading variable names (e.g., `pattern` for compiled regex, should be `compiled_pattern`)
- Missing docstrings on public recognizer/operator classes
- Incomplete type hints on public APIs (especially `analyze()`, `anonymize()` signatures)

## What NOT to Flag

**DO NOT comment on these (handled by automated tools):**

- ❌ Code formatting, line length, indentation (handled by `ruff format`)
- ❌ Import ordering (handled by `ruff check --select I`)
- ❌ Trailing commas, whitespace (handled by `ruff`)
- ❌ Type hint style preferences (`List[str]` vs `list[str]` - both valid for Python 3.9-3.12 support)

**DO NOT comment on style preferences that don't affect correctness:**

- Personal preferences for syntax variations
- Subjective naming when current name is clear in PII context
- Minor refactoring suggestions that don't fix bugs or improve accuracy
- Unnecessary abstractions "for future flexibility" in recognizers

## Presidio-Specific Review Guidelines

### When Reviewing Recognizers (PII Detectors)

**Location Validation:**
```
✅ GOOD: Country-specific in presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/
✅ GOOD: Generic patterns in .../predefined_recognizers/generic/
❌ BAD: US SSN recognizer in generic/ (should be country_specific/us/)
```

**Pattern Specificity:**
```python
# 🔴 CRITICAL: Too broad - matches "May", "April" as person names
pattern = r"\b[A-Z][a-z]+\b"

# ✅ GOOD: Specific pattern with context validation
pattern = r"\b(?:Mr\.|Mrs\.|Dr\.)\s+[A-Z][a-z]+\b"  # Title + name
# Validate with NLP context in analyze() method
```

**Configuration Completeness:**
```yaml
# When adding recognizer, must update conf/default_recognizers.yaml:
- name: "AuMedicareRecognizer"
  supported_languages: ["en"]
  enabled: false  # Country-specific must default to false
```

**Test Coverage Requirements:**
```python
# Every recognizer MUST have tests for:
def test_valid_au_medicare_number_returns_match()  # True positive
def test_invalid_checksum_returns_no_match()  # True negative  
def test_boundary_detection_exact_positions()  # Exact spans
def test_common_false_positive_cases()  # e.g., phone numbers mistaken for medicare
```

### When Reviewing Anonymizers (PII Operators)

**Reversibility Checks:**
```python
# 🔴 CRITICAL: Deterministic mapping allows de-anonymization
def anonymize(text, entity):
    return hashlib.md5(text.encode()).hexdigest()  # Rainbow table attack

# ✅ GOOD: Non-reversible with entropy
def anonymize(text, entity):
    return f"<{entity.entity_type}_{uuid.uuid4().hex[:8]}>"
```

**Consistency Validation:**
```python
# 🟡 Important: Verify anonymized text maintains valid structure
original = "Email: john@example.com, Phone: 555-1234"
anonymized = "Email: <EMAIL_ADDRESS>, Phone: <PHONE_NUMBER>"  # Structure preserved
```

### When Reviewing API Changes

**Backward Compatibility:**
```python
# 🔴 CRITICAL: Breaking change to public API
# OLD: def analyze(text: str, language: str) -> List[RecognizerResult]
# NEW: def analyze(text: str, language: str, entities: List[str]) -> List[RecognizerResult]

# ✅ GOOD: Backward compatible with default
def analyze(text: str, language: str, entities: Optional[List[str]] = None) -> List[RecognizerResult]
```

**Schema Versioning:**
```python
# 🟡 Important: REST API schema changes need version bump
# Update api-docs/api-docs.yml with new fields
# Mark old fields as deprecated, don't remove immediately
```

## Repository-Specific Context

### Technology Stack
- **Python 3.9-3.12** - Must support all versions (use `list[str]` or `List[str]`, both valid)
- **Poetry** - Package manager, not pip
- **Ruff** - Linting and formatting (replaces flake8, black, isort)
- **spaCy** - Default NLP engine (en_core_web_lg for production)
- **Docker** - Deployment via mcr.microsoft.com registry

### Component Architecture
```
presidio-analyzer     → PII detection engine (spaCy, regex, NLP)
presidio-anonymizer   → PII transformation engine (operators, deanonymizers)
presidio-cli          → Command-line interface (depends on analyzer)
presidio-image-redactor → Image PII redaction (OCR + analyzer + image ops)
presidio-structured   → Tabular data PII handling (pandas integration)
```

### Critical Files for Cross-Component Changes
- `RecognizerResult` - Shared analyzer output format
- `OperatorConfig` - Anonymizer operator configuration
- `conf/default_recognizers.yaml` - System-wide recognizer registry
- `docs/supported_entities.md` - Public entity type documentation
- API schemas in `docs/api-docs/`

## Review Tone & Approach

**Be specific and actionable:**
```
✅ GOOD: "🔴 CRITICAL: Line 45 logs detected PII value. Change logger.info(f'Found: {entity.text}') 
to logger.info(f'Found entity type: {entity.entity_type}')"

❌ BAD: "Don't log PII"
```

**Provide context:**
```
✅ GOOD: "🟡 Important: This regex has catastrophic backtracking on input 'aaaaaa...b' (O(2^n) time). 
Use atomic grouping: (?>a+)b or possessive quantifier a++b"

❌ BAD: "This regex is slow"
```

**Differentiate severity:**
- **🔴 CRITICAL** - Security, data leakage, correctness bugs affecting PII detection accuracy
- **🟡 Important** - Performance issues, cross-component breaks, missing tests for new recognizers  
- **💡 Suggestion** - Code quality improvements, better error messages, optimization opportunities

**Acknowledge good practices:**
- Well-tested recognizers with comprehensive edge case coverage
- Proper use of the `validate` and `invalidate` methods and good context words
- Good error handling with informative messages
- Performance optimizations (regex caching, batch processing)

## Code Generation Guidelines

When generating code for Presidio:

### New Recognizers
1. **Start with template**: Inherit from `LocalRecognizer`, `RemoteRecognizer` or `PatternRecognizer`
2. **Use specific patterns**: Avoid overly broad regex that causes false positives
3. **Document pattern sources**: Link to official standards (ISO, government docs)
4. **Comprehensive tests**: Include all four categories (TP, TN, boundaries, false positives)
5. **Update configuration**: Add to the respective `__init__.py` files, `default_recognizers.yaml` and `supported_entities.md`

### New Operators
1. **Implement interface**: All operators need `operate()` and `validate()` methods
2. **Handle edge cases**: Empty strings, unicode, special characters
3. **Non-reversible by default**: Unless explicitly building deanonymization support
4. **Validate params**: Check operator config in `validate()` before `operate()`
5. **Test anonymization quality**: Verify output doesn't leak original PII

### API Endpoints
1. **Maintain backward compatibility**: Use optional parameters, not required
2. **Validate inputs**: Check text length, entity types, language codes
3. **Update OpenAPI schema**: Modify `docs/api-docs/api-docs.yml`
4. **Add E2E tests**: New endpoints need tests in `e2e-tests/`
5. **Document in samples**: Add usage example to `docs/samples/`

### Performance Optimization
1. **Cache compiled regexes**: Use `@lru_cache` for pattern compilation
2. **Batch NLP processing**: Process multiple texts in one spaCy pipe
3. **Lazy load models**: Don't load transformers unless explicitly requested
4. **Profile before optimizing**: Use `pytest-benchmark` for recognizer performance tests

## Testing Strategy

### Required for All PRs
```bash
# Lint check (must pass)
ruff check .

# Component tests (based on changes)
cd presidio-analyzer && poetry run pytest -xvv  # If analyzer changed
cd presidio-anonymizer && poetry run pytest -xvv  # If anonymizer changed

# E2E tests (for cross-component changes)
# First start services: docker-compose up -d
cd e2e-tests && pytest -v
```

### Test Naming Convention
```python
# ✅ GOOD: Descriptive, follows convention
def test_when_valid_ssn_then_detect_with_correct_boundaries()
def test_when_invalid_checksum_then_no_match()
def test_when_overlapping_entities_then_merge_by_score()

# ❌ BAD: Non-descriptive
def test_ssn()
def test_case1()
```

## Quick Reference Commands

### Local Development
```bash
# Setup
cd presidio-analyzer  # or presidio-anonymizer, presidio-cli, etc.
poetry install --all-extras
poetry run python -m spacy download en_core_web_lg  # For analyzer/CLI only

# Run tests
poetry run pytest -xvv  # Stop on first failure with verbose output
poetry run pytest tests/test_us_ssn_recognizer.py -k "test_valid"  # Specific test

# Lint
ruff check .  # From repo root
ruff format .  # Auto-format
```

### Docker Testing
```bash
# Quick test with pre-built images
docker pull mcr.microsoft.com/presidio-analyzer:latest
docker run -d -p 5002:3000 --name analyzer mcr.microsoft.com/presidio-analyzer:latest
curl http://localhost:5002/health

# Full build from source (takes 15+ minutes)
docker compose up --build -d
```

### E2E Testing
```bash
docker-compose up -d  # Start all services
cd e2e-tests
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest -v  # Run all E2E tests
```

## Common Issues to Watch For

### Build/Test Issues
- **Poetry version conflicts** - Use `poetry lock --no-update` to preserve versions
- **Missing spaCy models** - Download en_core_web_lg before running tests
- **AHDS test skips** - Expected when AHDS_ENDPOINT not set
- **Transformers test failures** - Expected without HuggingFace access in restricted environments

### Code Issues
- **Logging PII values** - Never log `entity.text`, only `entity.entity_type`
- **Hardcoded language assumptions** - Use `context.language` parameter
- **Missing None checks** - NLP engines return None for empty/invalid text
- **Unbounded regex backtracking** - Test patterns with long strings
- **Confidence score > 1.0** - Validate score normalization logic

## Documentation Requirements Checklist

**See section 8 in Review Priorities above for comprehensive documentation guidelines.**

When adding features, update:
- **CHANGELOG.md** - Under "Unreleased" section
- **docs/supported_entities.md** - For new entity types
- **docs/api-docs/api-docs.yml** - For API changes
- **README.md** - For major features
- **Docstrings** - All public classes and methods (ensure proper formatting for API doc generation)
- **docs/samples/** - Add usage examples for complex new features

## Reference Documentation

**Consult these for detailed guidance:**
- **CONTRIBUTING.md** - PR process, CLA, code of conduct
- **docs/development.md** - Build process, testing, CI/CD
- **docs/analyzer/developing_recognizers.md** - Recognizer best practices
- **docs/analyzer/adding_recognizers.md** - Step-by-step recognizer guide
- **docs/anonymizer/adding_operators.md** - Operator development guide

---

**Summary for Code Review**: Prioritize security (PII leakage), correctness (detection accuracy), and performance (regex efficiency). Ensure comprehensive testing for all recognizers. Let automated tools handle formatting. Focus on actionable, specific feedback with concrete fixes.