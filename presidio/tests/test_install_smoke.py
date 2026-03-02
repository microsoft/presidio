"""Smoke test: build and install the presidio meta-package in a fresh venv.

Verifies that:
1. The package can be built from source.
2. Installing ``presidio`` in a clean environment pulls in ``presidio-analyzer``.
3. Core analyzer imports (``AnalyzerEngine``) are importable after installation.
"""

import subprocess
import sys
import venv
from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).parents[1]  # presidio/


@pytest.fixture(scope="module")
def fresh_venv(tmp_path_factory):
    """Create a throw-away venv with the presidio package installed."""
    env_dir = tmp_path_factory.mktemp("presidio_venv")
    venv.create(str(env_dir), with_pip=True)

    python = env_dir / "bin" / "python"

    # Build a wheel from the local source tree so the test is hermetic.
    dist_dir = tmp_path_factory.mktemp("presidio_dist")
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir), str(PACKAGE_ROOT)],
        check=True,
        capture_output=True,
    )

    wheels = list(dist_dir.glob("presidio-*.whl"))
    assert wheels, "No wheel was produced by the build step"
    wheel = wheels[0]

    # Install the wheel (and therefore presidio-analyzer) into the fresh venv.
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet", str(wheel)],
        check=True,
        capture_output=True,
    )

    return python


def test_presidio_analyzer_is_installed(fresh_venv):
    """presidio-analyzer must be present after installing presidio."""
    result = subprocess.run(
        [str(fresh_venv), "-m", "pip", "show", "presidio-analyzer"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "presidio-analyzer is not installed after installing presidio.\n"
        + result.stdout
        + result.stderr
    )


def test_analyzer_engine_importable(fresh_venv):
    """AnalyzerEngine must be importable from presidio_analyzer."""
    result = subprocess.run(
        [
            str(fresh_venv),
            "-c",
            "from presidio_analyzer import AnalyzerEngine; print('ok')",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Failed to import AnalyzerEngine from presidio_analyzer.\n"
        + result.stdout
        + result.stderr
    )
    assert result.stdout.strip() == "ok"
