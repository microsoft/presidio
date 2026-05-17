from install_nlp_models import (
    DEFAULT_ANALYZER_CONF_FILE,
    DEFAULT_NLP_CONF_FILE,
    _resolve_config_files,
)


def test_resolve_config_files_defaults_to_unified_analyzer_config():
    """Test no explicit config defaults to unified analyzer config."""
    nlp_conf_file, analyzer_conf_file = _resolve_config_files(
        nlp_conf_file=None, analyzer_conf_file=None
    )

    assert nlp_conf_file == DEFAULT_NLP_CONF_FILE
    assert analyzer_conf_file == DEFAULT_ANALYZER_CONF_FILE


def test_resolve_config_files_preserves_explicit_nlp_config_without_analyzer_default():
    """Test explicit NLP config is not overridden by default analyzer config."""
    nlp_conf_file, analyzer_conf_file = _resolve_config_files(
        nlp_conf_file="custom-nlp.yaml", analyzer_conf_file=None
    )

    assert nlp_conf_file == "custom-nlp.yaml"
    assert analyzer_conf_file is None


def test_resolve_config_files_adds_legacy_nlp_fallback_for_analyzer_config():
    """Test analyzer configs keep the legacy NLP fallback config."""
    nlp_conf_file, analyzer_conf_file = _resolve_config_files(
        nlp_conf_file=None, analyzer_conf_file="custom-analyzer.yaml"
    )

    assert nlp_conf_file == DEFAULT_NLP_CONF_FILE
    assert analyzer_conf_file == "custom-analyzer.yaml"
