from pathlib import Path


def test_when_reading_pyproject_then_spacy_3814_exclusion_is_python_314_scoped():
    """Ensure spacy 3.8.14 exclusion applies only to Python 3.14+."""
    pyproject = (
        Path(__file__).resolve().parents[1] / "pyproject.toml"
    ).read_text(encoding="utf-8")

    assert (
        "spacy (>=3.4.4,!=3.7.0,<4.0.0); python_version < '3.14'" in pyproject
    )
    assert (
        "spacy (>=3.4.4,!=3.7.0,!=3.8.14,<4.0.0); python_version >= '3.14'"
        in pyproject
    )
