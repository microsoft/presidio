# Poetry Lock Compatibility Test Scripts

This directory contains test scripts to validate that `presidio-analyzer` and `presidio-anonymizer` can be installed successfully using their `poetry.lock` files across all supported Python versions.

## Supported Python Versions
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

## Test Scripts

### 1. Bash Script: `test_poetry_lock_compatibility.sh`

A comprehensive bash script that tests installation compatibility.

**Usage:**
```bash
./test_poetry_lock_compatibility.sh
```

**Features:**
- Tests both presidio-analyzer and presidio-anonymizer
- Creates isolated virtual environments for each test
- Validates poetry.lock files
- Tests package imports after installation
- Provides colored output with detailed results
- Automatically cleans up temporary files

**Requirements:**
- Bash shell
- Poetry installed
- Desired Python versions installed on the system

### 2. Python Script: `test_poetry_lock_compatibility.py`

A Python-based alternative that performs the same tests.

**Usage:**
```bash
python3 test_poetry_lock_compatibility.py
# or
./test_poetry_lock_compatibility.py
```

**Features:**
- Same functionality as the bash script
- Cross-platform compatible (Linux, macOS, Windows)
- More robust error handling
- Better timeout management

**Requirements:**
- Python 3.6+ (for running the test script itself)
- Poetry installed
- Desired Python versions installed on the system

## What the Tests Do

For each project (presidio-analyzer, presidio-anonymizer) and each Python version (3.10-3.13):

1. **Check Python Availability**: Verifies if the Python version is installed
2. **Create Virtual Environment**: Creates an isolated venv using the target Python version
3. **Install Poetry**: Installs Poetry in the virtual environment
4. **Validate Lock File**: Runs `poetry check` to verify the lock file is valid
5. **Install Dependencies**: Runs `poetry install` using the lock file
6. **Import Test**: Verifies the installed package can be imported
7. **Cleanup**: Removes the virtual environment after testing

## Test Results

The scripts provide:
- **Passed**: Installation and import successful
- **Failed**: Installation or import failed (with error details)
- **Skipped**: Python version not available on the system

### Exit Codes
- `0`: All tests passed (or were skipped due to missing Python versions)
- `1`: One or more tests failed

## Example Output

```
========================================
Poetry Lock Compatibility Test
========================================

Testing Python versions: 3.10 3.11 3.12 3.13
Testing projects: presidio-analyzer presidio-anonymizer

Checking available Python versions:
✓ Python 3.10 is available
✓ Python 3.11 is available
✓ Python 3.12 is available
⚠ Python 3.13 is NOT available

========================================
Running Installation Tests
========================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Testing: presidio-analyzer with Python 3.10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Creating virtual environment with python3.10...
Setting up Poetry in virtual environment...
Checking poetry.lock compatibility...
Installing dependencies from poetry.lock...
Verifying package import...
Successfully imported presidio_analyzer
✓ PASSED: presidio-analyzer successfully installed and imported with Python 3.10

[... more tests ...]

========================================
Test Summary
========================================
Total Tests:   8
Passed:        6
Failed:        0
Skipped:       2

========================================
All tests passed!
```

## CI/CD Integration

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Test Poetry Lock Compatibility
  run: |
    ./test_poetry_lock_compatibility.sh
```

```yaml
# Example with Python script
- name: Test Poetry Lock Compatibility
  run: |
    python3 test_poetry_lock_compatibility.py
```

## Troubleshooting

### Script fails with "Python X.XX not available"
This is expected if that Python version is not installed. Install the missing version or the test will be skipped.

### Script times out during installation
Increase the timeout values in the script. Default is 10 minutes for `poetry install`.

### Permission denied
Make sure the scripts are executable:
```bash
chmod +x test_poetry_lock_compatibility.sh
chmod +x test_poetry_lock_compatibility.py
```

### Import test fails
This may indicate:
- The poetry.lock file has incompatible dependencies for that Python version
- Missing system dependencies
- The package structure has issues

Check the detailed error output for more information.

## Development Notes

- Both scripts create temporary virtual environments in `/tmp/presidio_test_*`
- Virtual environments are automatically cleaned up after each test
- The scripts do NOT install optional extras by default (to speed up tests)
- To test with extras, modify the `poetry install` command in the scripts

## Maintenance

When adding support for new Python versions:
1. Update the `PYTHON_VERSIONS` array in both scripts
2. Update this README
3. Ensure the new version is added to `pyproject.toml` classifiers
4. Regenerate poetry.lock files with `poetry lock`
