from importlib import metadata
from pathlib import Path

import pytest
from packaging.requirements import Requirement


def test_spacy_3_8_14_excluded_for_python_3_14_plus():
    """Ensure spacy 3.8.14 exclusion applies only to Python 3.14+."""
    pyproject = (
        Path(__file__).resolve().parents[1] / "pyproject.toml"
    ).read_text(encoding="utf-8")

    assert "spacy (>=3.4.4,!=3.7.0,<4.0.0); python_version < '3.14'" in pyproject
    assert (
        "spacy (>=3.4.4,!=3.7.0,!=3.8.14,<4.0.0); python_version >= '3.14'"
        in pyproject
    )


def test_distribution_preserves_python_version_markers():
    """Ensure built metadata preserves Python-version-specific spacy constraints."""
    try:
        requires = metadata.distribution("presidio_analyzer").requires or []
    except metadata.PackageNotFoundError:
        pytest.skip("presidio_analyzer distribution metadata is unavailable")

    spacy_requirements = []
    for requirement_text in requires:
        requirement = Requirement(requirement_text)
        if requirement.name.lower() == "spacy":
            spacy_requirements.append(requirement)

    requires_for_312 = [
        requirement
        for requirement in spacy_requirements
        if requirement.marker is None
        or requirement.marker.evaluate({"python_version": "3.12"})
    ]
    requires_for_314 = [
        requirement
        for requirement in spacy_requirements
        if requirement.marker is None
        or requirement.marker.evaluate({"python_version": "3.14"})
    ]

    assert requires_for_312
    assert requires_for_314
    assert all(
        str(requirement.specifier) == "!=3.7.0,<4.0.0,>=3.4.4"
        for requirement in requires_for_312
    )
    assert all(
        str(requirement.specifier) == "!=3.7.0,!=3.8.14,<4.0.0,>=3.4.4"
        for requirement in requires_for_314
    )
