from importlib import metadata
from pathlib import Path

import pytest
from packaging.requirements import Requirement

SPACY_SPECIFIERS_PRE_314 = {">=3.4.4", "!=3.7.0", "<4.0.0"}
SPACY_SPECIFIERS_314_PLUS = {">=3.4.4", "!=3.7.0", "!=3.8.14", "<4.0.0"}


def test_spacy_3_8_14_excluded_for_python_3_14_plus():
    """Ensure spacy 3.8.14 exclusion applies only to Python 3.14+."""
    pyproject_lines = (
        Path(__file__).resolve().parents[1] / "pyproject.toml"
    ).read_text(encoding="utf-8").splitlines()

    spacy_lines = [line.strip() for line in pyproject_lines if "spacy (" in line]
    lower_python_line = next(
        (line for line in spacy_lines if "python_version < '3.14'" in line),
        None,
    )
    higher_python_line = next(
        (line for line in spacy_lines if "python_version >= '3.14'" in line),
        None,
    )

    assert lower_python_line is not None
    assert higher_python_line is not None
    assert "!=3.8.14" not in lower_python_line
    assert "!=3.8.14" in higher_python_line


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

    assert spacy_requirements
    requires_for_312 = [
        requirement
        for requirement in spacy_requirements
        if requirement.marker
        and requirement.marker.evaluate({"python_version": "3.12"})
    ]
    requires_for_314 = [
        requirement
        for requirement in spacy_requirements
        if requirement.marker
        and requirement.marker.evaluate({"python_version": "3.14"})
    ]

    assert len(requires_for_312) == 1
    assert len(requires_for_314) == 1
    assert all(
        {str(specifier) for specifier in requirement.specifier}
        == SPACY_SPECIFIERS_PRE_314
        for requirement in requires_for_312
    )
    assert all(
        {str(specifier) for specifier in requirement.specifier}
        == SPACY_SPECIFIERS_314_PLUS
        for requirement in requires_for_314
    )
