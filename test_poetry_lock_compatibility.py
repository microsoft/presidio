#!/usr/bin/env python3
"""
Test script to validate that presidio-analyzer and presidio-anonymizer
can be installed successfully with their poetry.lock files across all
supported Python versions (3.10, 3.11, 3.12, 3.13)

This is a Python-based alternative to the bash script.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Configuration
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]
PROJECTS = ["presidio-analyzer", "presidio-anonymizer"]
WORKSPACE_ROOT = Path("/workspaces/presidio")

# Test results tracking
class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.failed_details: List[str] = []
    
    def record_pass(self):
        self.total += 1
        self.passed += 1
    
    def record_fail(self, detail: str):
        self.total += 1
        self.failed += 1
        self.failed_details.append(detail)
    
    def record_skip(self):
        self.total += 1
        self.skipped += 1


def check_python_version(version: str) -> bool:
    """Check if a specific Python version is available."""
    python_cmd = f"python{version}"
    try:
        result = subprocess.run(
            [python_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓{Colors.NC} Python {version} is available: {result.stdout.strip()}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠{Colors.NC} Python {version} is NOT available")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"{Colors.YELLOW}⚠{Colors.NC} Python {version} is NOT available")
        return False


def test_installation(project: str, python_version: str, results: TestResults) -> bool:
    """Test installation for a project with a specific Python version."""
    print(f"\n{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
    print(f"{Colors.BLUE}Testing: {project} with Python {python_version}{Colors.NC}")
    print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
    
    python_cmd = f"python{python_version}"
    
    # Check if Python version is available
    if not shutil.which(python_cmd):
        print(f"{Colors.YELLOW}⚠ SKIPPED: Python {python_version} not available{Colors.NC}")
        results.record_skip()
        return True
    
    # Create temporary virtual environment
    venv_dir = Path(f"/tmp/presidio_test_{project}_py{python_version}")
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    
    try:
        # Create virtual environment
        print(f"Creating virtual environment with {python_cmd}...")
        result = subprocess.run(
            [python_cmd, "-m", "venv", str(venv_dir)],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            print(f"{Colors.RED}✗ FAILED: Could not create virtual environment{Colors.NC}")
            print(result.stderr)
            results.record_fail(f"{project} | Python {python_version} | Failed to create venv")
            return False
        
        # Determine pip and python executables in venv
        if sys.platform == "win32":
            venv_python = venv_dir / "Scripts" / "python.exe"
            venv_pip = venv_dir / "Scripts" / "pip.exe"
        else:
            venv_python = venv_dir / "bin" / "python"
            venv_pip = venv_dir / "bin" / "pip"
        
        # Upgrade pip and install poetry
        print("Setting up Poetry in virtual environment...")
        result = subprocess.run(
            [str(venv_pip), "install", "--quiet", "--upgrade", "pip", "poetry"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            print(f"{Colors.RED}✗ FAILED: Could not install pip/poetry{Colors.NC}")
            print(result.stderr)
            results.record_fail(f"{project} | Python {python_version} | Failed to install pip/poetry")
            return False
        
        # Navigate to project directory
        project_dir = WORKSPACE_ROOT / project
        
        # Verify poetry.lock exists
        lock_file = project_dir / "poetry.lock"
        if not lock_file.exists():
            print(f"{Colors.RED}✗ FAILED: poetry.lock not found in {project}{Colors.NC}")
            results.record_fail(f"{project} | Python {python_version} | poetry.lock not found")
            return False
        
        # Determine poetry executable in venv
        if sys.platform == "win32":
            venv_poetry = venv_dir / "Scripts" / "poetry.exe"
        else:
            venv_poetry = venv_dir / "bin" / "poetry"
        
        # Check if lock file is compatible
        print("Checking poetry.lock compatibility...")
        result = subprocess.run(
            [str(venv_poetry), "check"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"{Colors.RED}✗ FAILED: poetry check failed{Colors.NC}")
            print(result.stderr)
            results.record_fail(f"{project} | Python {python_version} | poetry check failed")
            return False
        
        # Install dependencies and the package itself
        print("Installing dependencies from poetry.lock...")
        result = subprocess.run(
            [str(venv_poetry), "install", "--no-interaction", "--no-ansi", "--without", "dev"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout for installation
        )
        if result.returncode != 0:
            print(f"{Colors.RED}✗ FAILED: poetry install failed{Colors.NC}")
            print("Last lines of output:")
            print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
            print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
            results.record_fail(f"{project} | Python {python_version} | poetry install failed")
            return False
        
        # Verify package can be imported using poetry run
        print("Verifying package import...")
        package_name = project.replace("-", "_")
        result = subprocess.run(
            [
                str(venv_poetry), "run", "python", "-c",
                f"import {package_name}; print(f'Successfully imported {package_name}')"
            ],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"{Colors.RED}✗ FAILED: Could not import {package_name}{Colors.NC}")
            print(result.stderr)
            results.record_fail(f"{project} | Python {python_version} | Import failed")
            return False
        
        print(result.stdout.strip())
        print(f"{Colors.GREEN}✓ PASSED: {project} successfully installed and imported with Python {python_version}{Colors.NC}")
        results.record_pass()
        return True
        
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}✗ FAILED: Operation timed out{Colors.NC}")
        results.record_fail(f"{project} | Python {python_version} | Timeout")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ FAILED: Unexpected error: {e}{Colors.NC}")
        results.record_fail(f"{project} | Python {python_version} | Exception: {str(e)}")
        return False
    finally:
        # Cleanup
        if venv_dir.exists():
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Could not cleanup {venv_dir}: {e}{Colors.NC}")


def main():
    """Main test execution."""
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print(f"{Colors.BLUE}Poetry Lock Compatibility Test{Colors.NC}")
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print()
    print(f"Testing Python versions: {', '.join(PYTHON_VERSIONS)}")
    print(f"Testing projects: {', '.join(PROJECTS)}")
    print()
    
    # Check available Python versions
    print(f"\n{Colors.BLUE}Checking available Python versions:{Colors.NC}")
    for version in PYTHON_VERSIONS:
        check_python_version(version)
    
    print(f"\n{Colors.BLUE}========================================{Colors.NC}")
    print(f"{Colors.BLUE}Running Installation Tests{Colors.NC}")
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    
    # Run tests
    results = TestResults()
    for project in PROJECTS:
        for version in PYTHON_VERSIONS:
            test_installation(project, version, results)
    
    # Print summary
    print(f"\n{Colors.BLUE}========================================{Colors.NC}")
    print(f"{Colors.BLUE}Test Summary{Colors.NC}")
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print(f"Total Tests:   {results.total}")
    print(f"{Colors.GREEN}Passed:        {results.passed}{Colors.NC}")
    print(f"{Colors.RED}Failed:        {results.failed}{Colors.NC}")
    print(f"{Colors.YELLOW}Skipped:       {results.skipped}{Colors.NC}")
    
    # Print failed test details
    if results.failed > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.NC}")
        for detail in results.failed_details:
            print(f"{Colors.RED}  ✗ {detail}{Colors.NC}")
    
    print(f"\n{Colors.BLUE}========================================{Colors.NC}")
    
    # Exit with appropriate code
    if results.failed > 0:
        print(f"{Colors.RED}Some tests failed!{Colors.NC}")
        sys.exit(1)
    else:
        print(f"{Colors.GREEN}All tests passed!{Colors.NC}")
        sys.exit(0)


if __name__ == "__main__":
    main()
