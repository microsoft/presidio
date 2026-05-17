import pytest
from presidio_analyzer.analyzer_engine_provider import AnalyzerEngineProvider


def test_partial_analyzer_config_warning_uses_migration_guidance(tmp_path):
    """Test partial analyzer configs warn with explicit migration guidance."""
    config_file = tmp_path / "partial_analyzer.yaml"
    config_file.write_text(
        "supported_languages:\n"
        "  - en\n"
        "default_score_threshold: 0.1\n",
        encoding="utf-8",
    )

    with pytest.warns(DeprecationWarning) as warnings:
        AnalyzerEngineProvider(analyzer_engine_conf_file=config_file)

    warning_message = str(warnings[0].message)
    assert "deprecated YAML config format" in warning_message
    assert "separate file for each module" in warning_message
    assert "Migrate to the unified analyzer configuration file format" in (
        warning_message
    )
