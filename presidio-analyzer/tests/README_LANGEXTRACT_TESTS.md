# LangExtract Recognizer Tests

## Overview

The LangExtract recognizer tests have been refactored to use **real Ollama integration** instead of misleading mocks. This ensures that tests actually validate the functionality rather than just passing without real validation.

## Key Changes

### Before (Problematic)
- ❌ Most tests used extensive mocks
- ❌ Tests passed even when Ollama wasn't working
- ❌ Developers were misled into thinking everything worked
- ❌ Only a few integration tests at the bottom actually tested real functionality

### After (Fixed)
- ✅ All tests now use real Ollama
- ✅ Tests are skipped if Ollama is not available (clear feedback)
- ✅ Automatic Ollama setup via `install_ollama_model.py`
- ✅ Tests validate actual PII detection, not mocked responses
- ✅ Only specific error cases use mocks (e.g., testing connection failures)

## How It Works

### 1. Test Fixture Setup (`conftest.py`)

The `conftest.py` file contains an `ollama_available` fixture that:

1. **Checks if Ollama is running** at `http://localhost:11434`
2. **Auto-installs and starts Ollama** if not found by running `install_ollama_model.py`
3. **Returns True/False** to indicate if Ollama is ready

```python
@pytest.fixture(scope="session")
def ollama_available() -> bool:
    # Check if already running
    # If not, run install_ollama_model.py
    # Return availability status
```

### 2. Test Marker

All tests use the `@pytest.mark.skip_engine("langextract")` marker which:
- Checks the `ollama_available` fixture
- **Skips tests** if Ollama setup failed
- Provides clear feedback about why tests were skipped

### 3. Auto-Installation

The `install_ollama_model.py` script:
- Detects the operating system
- Installs Ollama if needed (Linux/macOS)
- Starts the Ollama service
- Verifies it's responding
- Is called automatically by the test fixture

### 4. Model Auto-Download

The `LangExtractRecognizer` class itself:
- Checks if the required model exists
- **Automatically downloads** the model if missing (via `ollama pull`)
- Only downloads once (subsequent runs just verify it exists)
- Logs clear progress messages

## Running the Tests

### Prerequisites
- Python 3.8+
- Docker (optional, for containerized Ollama)
- OR let the tests auto-install Ollama locally

### Run LangExtract Tests

```bash
# Run all LangExtract tests
cd presidio-analyzer
pytest tests/test_langextract_recognizer.py -v

# Run specific test
pytest tests/test_langextract_recognizer.py::TestLangExtractRecognizerAnalyze::test_analyze_with_person_entity -v

# Run with output
pytest tests/test_langextract_recognizer.py -v -s
```

### What Happens on First Run

1. **Ollama Check**: Tests check if Ollama is running
2. **Auto-Install**: If not found, `install_ollama_model.py` runs:
   - Downloads and installs Ollama
   - Starts the service
   - Takes ~5-10 minutes on first run
3. **Model Download**: When recognizer initializes:
   - Checks if model (e.g., `llama3.2:1b`) exists
   - Downloads if missing (~1-2 GB, takes 5-10 minutes)
   - This happens once, model is cached
4. **Tests Run**: All tests now use real Ollama/LangExtract

### What Happens on Subsequent Runs

1. **Quick Check**: Verifies Ollama is running (~1 second)
2. **Model Check**: Verifies model exists (~1 second)
3. **Tests Run**: Tests execute normally (each test ~5-30 seconds)

## Test Categories

### 1. Initialization Tests
- Test config loading
- Test Ollama connection validation
- Test error handling for invalid configs

### 2. Ollama Validation Tests
- Test server reachability
- Test model availability
- Test auto-download functionality

### 3. Analysis Tests (Integration)
- Test PERSON entity detection
- Test EMAIL_ADDRESS entity detection
- Test PHONE_NUMBER entity detection
- Test multiple entity detection
- Test entity filtering
- **All use real Ollama model**

### 4. Error Handling Tests
- Test connection errors (mocked invalid URL)
- Test graceful degradation

## CI/CD Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Setup Ollama for Tests
  run: |
    python presidio-analyzer/install_ollama_model.py

- name: Run LangExtract Tests
  run: |
    cd presidio-analyzer
    pytest tests/test_langextract_recognizer.py -v
```

Or use Docker Compose:

```bash
docker-compose up -d ollama
pytest tests/test_langextract_recognizer.py -v
```

## Benefits of New Approach

### For Developers
- ✅ **Clear feedback**: Tests clearly indicate if setup fails
- ✅ **Real validation**: Tests actually verify PII detection works
- ✅ **Auto-setup**: No manual Ollama installation needed
- ✅ **Fast iteration**: After first run, tests are quick

### For CI/CD
- ✅ **Reproducible**: Same setup process everywhere
- ✅ **Containerizable**: Can use Docker Compose
- ✅ **Clear failures**: Test failures indicate real issues

### For Users
- ✅ **Confidence**: If tests pass, the feature actually works
- ✅ **Documentation**: Tests serve as usage examples
- ✅ **No surprises**: Production behavior matches test behavior

## Troubleshooting

### Tests are Skipped

```
SKIPPED [1] conftest.py:123: skipped - Ollama not available for langextract
```

**Solution**: Check logs from `install_ollama_model.py`. Common issues:
- Docker not running (if using Docker)
- Network issues preventing download
- Insufficient disk space for model

### Tests are Slow

**First Run**: Expected (10-20 minutes for setup)
**Subsequent Runs**: Should be fast (~1-2 min for all tests)

If always slow:
- Model might be re-downloading (check Ollama logs)
- Network latency to Ollama server
- LLM inference is compute-intensive (normal)

### Connection Errors

```
ConnectionError: Ollama server not reachable
```

**Solutions**:
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check firewall settings
3. Restart Ollama: `pkill ollama && ollama serve &`

## Migration from Old Tests

The old test file had extensive mocks. Key changes:

### Removed
- `mock_langextract` fixture (no longer needed)
- `test_config_path`, `test_prompt_file`, `test_examples_file` fixtures
- Most `patch()` decorators
- Fake extraction results

### Added
- Real Ollama integration
- `langextract_recognizer_class` fixture (from conftest)
- Integration test parameters
- Clear skip markers

### Kept
- Error handling tests (but with real invalid configs)
- Config validation tests
- Test structure and organization

## Future Improvements

Potential enhancements:
- [ ] Add performance benchmarks
- [ ] Test with multiple models
- [ ] Test with different languages
- [ ] Add stress tests
- [ ] Cache model downloads in CI

## Questions?

See:
- `conftest.py` - Test fixtures and Ollama setup
- `install_ollama_model.py` - Ollama installation script
- `langextract_recognizer.py` - Auto-download implementation
