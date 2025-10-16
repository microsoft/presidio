#!/bin/bash
# Test script to validate that presidio-analyzer and presidio-anonymizer
# can be installed successfully with their poetry.lock files across all
# supported Python versions (3.10, 3.11, 3.12, 3.13)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Supported Python versions
PYTHON_VERSIONS=("3.10" "3.11" "3.12" "3.13")

# Projects to test
PROJECTS=("presidio-analyzer" "presidio-anonymizer")

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Store failed test details
declare -a FAILED_TEST_DETAILS

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Poetry Lock Compatibility Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Testing Python versions: ${PYTHON_VERSIONS[*]}"
echo "Testing projects: ${PROJECTS[*]}"
echo ""

# Function to check if a Python version is available
check_python_version() {
    local version=$1
    if command -v python${version} &> /dev/null; then
        echo -e "${GREEN}✓${NC} Python ${version} is available"
        python${version} --version
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Python ${version} is NOT available"
        return 1
    fi
}

# Function to test installation for a project with a specific Python version
test_installation() {
    local project=$1
    local python_version=$2
    local python_cmd="python${python_version}"
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Testing: ${project} with Python ${python_version}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Check if Python version is available
    if ! command -v ${python_cmd} &> /dev/null; then
        echo -e "${YELLOW}⚠ SKIPPED: Python ${python_version} not available${NC}"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
        return 0
    fi
    
    # Create a temporary virtual environment
    local venv_dir="/tmp/presidio_test_${project}_py${python_version}"
    rm -rf ${venv_dir}
    
    echo "Creating virtual environment with ${python_cmd}..."
    if ! ${python_cmd} -m venv ${venv_dir}; then
        echo -e "${RED}✗ FAILED: Could not create virtual environment${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_DETAILS+=("${project} | Python ${python_version} | Failed to create venv")
        return 1
    fi
    
    # Activate virtual environment
    source ${venv_dir}/bin/activate
    
    # Upgrade pip and install poetry in the venv
    echo "Setting up Poetry in virtual environment..."
    if ! python -m pip install --quiet --upgrade pip poetry; then
        echo -e "${RED}✗ FAILED: Could not install pip/poetry${NC}"
        deactivate
        rm -rf ${venv_dir}
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_DETAILS+=("${project} | Python ${python_version} | Failed to install pip/poetry")
        return 1
    fi
    
    # Navigate to project directory
    cd /workspaces/presidio/${project}
    
    # Verify poetry.lock exists
    if [ ! -f "poetry.lock" ]; then
        echo -e "${RED}✗ FAILED: poetry.lock not found in ${project}${NC}"
        deactivate
        rm -rf ${venv_dir}
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_DETAILS+=("${project} | Python ${python_version} | poetry.lock not found")
        return 1
    fi
    
    # Check if lock file is compatible
    echo "Checking poetry.lock compatibility..."
    if ! poetry check; then
        echo -e "${RED}✗ FAILED: poetry check failed${NC}"
        deactivate
        rm -rf ${venv_dir}
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_DETAILS+=("${project} | Python ${python_version} | poetry check failed")
        return 1
    fi
    
    # Install dependencies and the package (--without dev to skip dev dependencies and speed up)
    echo "Installing dependencies from poetry.lock..."
    if ! poetry install --no-interaction --no-ansi --without dev 2>&1 | tee /tmp/install_log_${project}_${python_version}.txt; then
        echo -e "${RED}✗ FAILED: poetry install failed${NC}"
        echo "Last 20 lines of install log:"
        tail -20 /tmp/install_log_${project}_${python_version}.txt
        deactivate
        rm -rf ${venv_dir}
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_DETAILS+=("${project} | Python ${python_version} | poetry install failed")
        return 1
    fi
    
    # Verify the package can be imported using poetry run
    echo "Verifying package import..."
    local package_name="${project//-/_}"  # Convert presidio-analyzer to presidio_analyzer
    if ! poetry run python -c "import ${package_name}; print(f'Successfully imported ${package_name}')"; then
        echo -e "${RED}✗ FAILED: Could not import ${package_name}${NC}"
        deactivate
        rm -rf ${venv_dir}
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_DETAILS+=("${project} | Python ${python_version} | Import failed")
        return 1
    fi
    
    # Test passed!
    echo -e "${GREEN}✓ PASSED: ${project} successfully installed and imported with Python ${python_version}${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    
    # Cleanup
    deactivate
    rm -rf ${venv_dir}
    rm -f /tmp/install_log_${project}_${python_version}.txt
    
    return 0
}

# Main test execution
echo -e "\n${BLUE}Checking available Python versions:${NC}"
for version in "${PYTHON_VERSIONS[@]}"; do
    check_python_version ${version} || true
done

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Running Installation Tests${NC}"
echo -e "${BLUE}========================================${NC}"

# Run tests for each combination
for project in "${PROJECTS[@]}"; do
    for version in "${PYTHON_VERSIONS[@]}"; do
        test_installation ${project} ${version}
    done
done

# Print summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Tests:   ${TOTAL_TESTS}"
echo -e "${GREEN}Passed:        ${PASSED_TESTS}${NC}"
echo -e "${RED}Failed:        ${FAILED_TESTS}${NC}"
echo -e "${YELLOW}Skipped:       ${SKIPPED_TESTS}${NC}"

# Print failed test details if any
if [ ${FAILED_TESTS} -gt 0 ]; then
    echo -e "\n${RED}Failed Tests:${NC}"
    for detail in "${FAILED_TEST_DETAILS[@]}"; do
        echo -e "${RED}  ✗ ${detail}${NC}"
    done
fi

echo -e "\n${BLUE}========================================${NC}"

# Exit with error if any tests failed
if [ ${FAILED_TESTS} -gt 0 ]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
fi
