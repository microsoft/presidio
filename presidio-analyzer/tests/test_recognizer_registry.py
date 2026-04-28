from pathlib import Path

import pytest
import regex as re

from presidio_analyzer import (
    RecognizerRegistry,
    PatternRecognizer,
    EntityRecognizer,
    Pattern,
    AnalyzerEngine,
)
from presidio_analyzer.predefined_recognizers import SpacyRecognizer


def create_mock_pattern_recognizer(lang, entity, name):
    return PatternRecognizer(
        supported_entity=entity,
        supported_language=lang,
        name=name,
        patterns=[Pattern("pat", regex="REGEX", score=1.0)],
    )


def create_mock_custom_recognizer(lang, entities, name):
    return EntityRecognizer(
        supported_entities=entities, name=name, supported_language=lang
    )


@pytest.fixture(scope="function")
def mock_recognizer_registry():
    pattern_recognizer1 = create_mock_pattern_recognizer("en", "PERSON", "1")
    pattern_recognizer2 = create_mock_pattern_recognizer("de", "PERSON", "2")
    pattern_recognizer3 = create_mock_pattern_recognizer("de", "ADDRESS", "3")
    pattern_recognizer4 = create_mock_pattern_recognizer("he", "ADDRESS", "4")
    pattern_recognizer5 = create_mock_custom_recognizer(
        "he", ["PERSON", "ADDRESS"], "5"
    )
    return RecognizerRegistry(
        [
            pattern_recognizer1,
            pattern_recognizer2,
            pattern_recognizer3,
            pattern_recognizer4,
            pattern_recognizer5,
        ],
    )


def test_when_get_recognizers_then_all_recognizers_returned(mock_recognizer_registry):
    registry = mock_recognizer_registry
    registry.load_predefined_recognizers()
    recognizers = registry.get_recognizers(language="en", all_fields=True)
    
    # 1 custom recognizer in english + 28 predefined - 11 disabled
    assert len(recognizers) == 1 + 28 - 11


def test_when_get_recognizers_then_return_all_fields(mock_recognizer_registry):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="de", all_fields=True)
    assert len(recognizers) == 2


def test_when_get_recognizers_one_language_then_return_one_entity(
    mock_recognizer_registry,
):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="de", entities=["PERSON"])
    assert len(recognizers) == 1


def test_when_get_recognizers_unsupported_language_then_return(
    mock_recognizer_registry,
):
    with pytest.raises(ValueError):
        registry = mock_recognizer_registry
        registry.get_recognizers(language="brrrr", entities=["PERSON"])


def test_when_get_recognizers_specific_language_and_entity_then_return_one_result(
    mock_recognizer_registry,
):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="he", entities=["PERSON"])
    assert len(recognizers) == 1


def test_when_multiple_entities_from_same_recognizer_only_one_is_returned():
    registry = RecognizerRegistry()

    recognizer_supporting_two_ents = EntityRecognizer(
        supported_entities=["A", "B"], name="MyReco"
    )
    registry.add_recognizer(recognizer_supporting_two_ents)
    recognizers = registry.get_recognizers(
        language="en", entities=["A", "B"], all_fields=False
    )

    assert len(recognizers) == 1
    assert recognizers[0].name == "MyReco"


def test_when_add_pattern_recognizer_then_item_added():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    # Create an empty recognizer registry
    recognizer_registry = RecognizerRegistry(recognizers=[])
    assert len(recognizer_registry.recognizers) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizer_registry.add_recognizer(pattern_recognizer)

    assert len(recognizer_registry.recognizers) == 1
    assert recognizer_registry.recognizers[0].patterns[0].name == "rocket pattern"
    assert recognizer_registry.recognizers[0].name == "Rocket recognizer"


def test_when_remove_pattern_recognizer_then_item_removed():
    pattern = Pattern("spaceship pattern", r"\W*(spaceship)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "SPACESHIP", name="Spaceship recognizer", patterns=[pattern]
    )
    # Create an empty recognizer registry
    recognizer_registry = RecognizerRegistry(recognizers=[])
    assert len(recognizer_registry.recognizers) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizer_registry.add_recognizer(pattern_recognizer)

    # Expects one custom recognizer
    assert len(recognizer_registry.recognizers) == 1

    # Remove recognizer
    recognizer_registry.remove_recognizer("Spaceship recognizer")

    # Expects zero custom recognizers
    assert len(recognizer_registry.recognizers) == 0


def test_add_recognizer_from_dict():
    registry = RecognizerRegistry()
    recognizer = {
        "name": "Zip code Recognizer",
        "supported_language": "de",
        "patterns": [
            {
                "name": "zip code (weak)",
                "regex": "(\\b\\d{5}(?:\\-\\d{4})?\\b)",
                "score": 0.01,
            }
        ],
        "context": ["zip", "code"],
        "supported_entity": "ZIP",
    }
    registry.add_pattern_recognizer_from_dict(recognizer)

    assert len(registry.recognizers) == 1
    assert registry.recognizers[0].name == "Zip code Recognizer"


def test_recognizer_registry_add_from_yaml_file():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/recognizers.yaml")

    registry = RecognizerRegistry()
    registry.add_recognizers_from_yaml(test_yaml)

    assert len(registry.recognizers) == 2
    zip_recogizer: PatternRecognizer = registry.get_recognizers(
        language="de", entities=["ZIP"]
    )[0]
    assert zip_recogizer.name == "Zip code Recognizer"
    assert zip_recogizer.supported_language == "de"
    assert zip_recogizer.supported_entities == ["ZIP"]
    assert len(zip_recogizer.patterns) == 1

    titles_recogizer: PatternRecognizer = registry.get_recognizers(
        language="en", entities=["TITLE"]
    )[0]
    assert titles_recogizer.name == "Titles recognizer"
    assert titles_recogizer.supported_language == "en"
    assert titles_recogizer.supported_entities == ["TITLE"]
    assert len(titles_recogizer.patterns) == 1  # deny-list turns into a pattern
    assert len(titles_recogizer.deny_list) == 6


def test_recognizer_registry_exception_missing_yaml_file():
    test_yaml = Path("missing.yaml")
    with pytest.raises(IOError):
        registry = RecognizerRegistry()
        registry.add_recognizers_from_yaml(test_yaml)


def test_recognizer_registry_exception_erroneous_yaml():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/recognizers_error.yaml")

    with pytest.raises(TypeError):
        registry = RecognizerRegistry()
        registry.add_recognizers_from_yaml(test_yaml)


def test_predefined_pattern_recognizers_have_the_right_regex_flags():
    registry = RecognizerRegistry(global_regex_flags=re.DOTALL)
    registry.load_predefined_recognizers()
    for rec in registry.recognizers:
        if isinstance(rec, PatternRecognizer):
            assert rec.global_regex_flags == re.DOTALL


def test_recognizer_removed_and_returned_entities_are_correct():
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()
    registry.remove_recognizer("SpacyRecognizer")
    sr = SpacyRecognizer(supported_entities=["DATE_TIME", "NRP"])
    registry.add_recognizer(sr)

    supported_entities = registry.get_supported_entities(languages=["en"])

    assert "DATE_TIME" in supported_entities
    assert "PERSON" not in supported_entities

    analyzer = AnalyzerEngine(registry=registry, supported_languages=["en"])

    analyzer.analyze("My name is David", language="en")


def test_remove_recognizer_when_multiple_instances_exist():
    registry = RecognizerRegistry()

    spacy_english = SpacyRecognizer(supported_language="en")
    spacy_spanish = SpacyRecognizer(supported_language="es")
    registry.add_recognizer(spacy_english)
    registry.add_recognizer(spacy_spanish)

    registry.remove_recognizer("SpacyRecognizer", language="en")
    assert len(registry.recognizers) == 1

    assert registry.recognizers[0].supported_language == "es"
    assert len([rec for rec in registry.recognizers
                if rec.name == "SpacyRecognizer"]) == 1



# ---------------------------------------------------------------------------
# Country filter (load_predefined_recognizers(countries=...)) — fixes #1328
# ---------------------------------------------------------------------------


def _recognizer_class_names(registry):
    return {type(rec).__name__ for rec in registry.recognizers}


def test_load_predefined_recognizers_without_country_filter_loads_all():
    """Default behavior must be unchanged when `countries` is omitted."""
    baseline = RecognizerRegistry()
    baseline.load_predefined_recognizers()

    explicit_none = RecognizerRegistry()
    explicit_none.load_predefined_recognizers(countries=None)

    assert _recognizer_class_names(baseline) == _recognizer_class_names(explicit_none)


def test_load_predefined_recognizers_filters_to_requested_countries():
    """Only recognizers from the requested countries plus country-agnostic
    recognizers (generic, NER, NLP engine, third-party) should be loaded."""
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(countries=["us"])
    names = _recognizer_class_names(registry)

    # A US recognizer is present.
    assert "UsSsnRecognizer" in names
    # A non-US country recognizer is absent.
    assert "UkNinoRecognizer" not in names
    assert "NhsRecognizer" not in names
    # Country-agnostic recognizers are still present.
    assert "CreditCardRecognizer" in names
    assert "EmailRecognizer" in names


def test_load_predefined_recognizers_country_filter_is_case_insensitive():
    registry_lower = RecognizerRegistry()
    registry_lower.load_predefined_recognizers(countries=["us"])

    registry_upper = RecognizerRegistry()
    registry_upper.load_predefined_recognizers(countries=["US"])

    assert _recognizer_class_names(registry_lower) == _recognizer_class_names(
        registry_upper
    )


def test_load_predefined_recognizers_empty_countries_keeps_only_agnostic():
    """Passing an empty list drops every country-specific recognizer but keeps
    generic ones."""
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(countries=[])
    names = _recognizer_class_names(registry)

    assert "UsSsnRecognizer" not in names
    assert "UkNinoRecognizer" not in names
    assert "NhsRecognizer" not in names
    # Country-agnostic recognizers remain.
    assert "CreditCardRecognizer" in names
    assert "EmailRecognizer" in names


def test_load_predefined_recognizers_multiple_countries():
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(countries=["us", "uk"])
    names = _recognizer_class_names(registry)

    assert "UsSsnRecognizer" in names
    assert "NhsRecognizer" in names  # UK National Health Service
    # Germany should be excluded.
    assert not any(n.startswith("De") for n in names if n != "DateRecognizer")


# ---------------------------------------------------------------------------
# COUNTRY_CODE class attribute on EntityRecognizer + filter integration — #1328
# ---------------------------------------------------------------------------


def test_entity_recognizer_country_code_default_is_none():
    """A recognizer class with no ``COUNTRY_CODE`` declared is locale-agnostic
    via the inherited default on ``EntityRecognizer``."""
    rec = create_mock_pattern_recognizer("en", "FOO", "rec")
    assert rec.country_code() is None
    assert rec.is_country_specific() is False


def test_country_code_classmethod_lowercases_class_attribute():
    """``country_code()`` normalizes the class-level ``COUNTRY_CODE`` to
    lowercase so the filter's case-insensitive contract holds at the
    source of truth."""

    class _UpperCased(PatternRecognizer):
        COUNTRY_CODE = "DE"

        def __init__(self):
            super().__init__(
                supported_entity="X",
                patterns=[Pattern("p", "REGEX", 1.0)],
            )

    rec = _UpperCased()
    assert rec.country_code() == "de"
    assert rec.is_country_specific() is True


def test_predefined_country_specific_recognizer_carries_class_country_code():
    """Predefined country-specific recognizers expose ``country_code()`` via
    their class-level ``COUNTRY_CODE`` attribute."""
    from presidio_analyzer.predefined_recognizers import UsSsnRecognizer

    # Classmethod is callable on the class without instantiation.
    assert UsSsnRecognizer.country_code() == "us"
    assert UsSsnRecognizer.is_country_specific() is True

    # And on an instance.
    rec = UsSsnRecognizer()
    assert rec.country_code() == "us"


def test_country_code_is_a_class_level_fact_not_instance():
    """``COUNTRY_CODE`` is a fact about the recognizer *class*; setting it
    on an instance does not influence what the classmethod returns. This
    keeps country tagging discoverable at the type level for review and
    introspection."""
    from presidio_analyzer.predefined_recognizers import UsSsnRecognizer

    rec = UsSsnRecognizer()
    # Attempting to override at the instance level is intentionally a no-op
    # for the classmethod-based API.
    rec.COUNTRY_CODE = "ca"  # noqa: B010 — exercising the contract
    assert rec.country_code() == "us"


def test_country_filter_keeps_untagged_custom_recognizer():
    """An untagged custom recognizer (no ``COUNTRY_CODE`` declared) is the
    "I haven't opted in" case and must always be kept regardless of the
    requested countries — this is what makes the migration backwards
    compatible."""
    custom = create_mock_pattern_recognizer("en", "MY_THING", "Custom")
    assert custom.country_code() is None

    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(countries=["us"])
    registry.add_recognizer(custom)

    assert custom in registry.recognizers


def test_country_filter_includes_tagged_custom_recognizer():
    """A custom recognizer that opts in via class-level ``COUNTRY_CODE`` is
    included when the filter is loaded with the matching country."""
    from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
        RecognizerListLoader,
    )

    class _BrCpfRecognizer(PatternRecognizer):
        COUNTRY_CODE = "br"

        def __init__(self):
            super().__init__(
                supported_entity="BR_CPF",
                name="BR CPF Recognizer",
                patterns=[Pattern("p", regex="REGEX", score=1.0)],
            )

    class _XUsRecognizer(PatternRecognizer):
        COUNTRY_CODE = "us"

        def __init__(self):
            super().__init__(
                supported_entity="X_US_THING",
                name="X US Recognizer",
                patterns=[Pattern("p", regex="REGEX", score=1.0)],
            )

    br_recognizer = _BrCpfRecognizer()
    us_recognizer = _XUsRecognizer()
    agnostic = create_mock_pattern_recognizer("en", "AGNOSTIC", "Agnostic")

    filtered = RecognizerListLoader.filter_by_countries(
        [br_recognizer, us_recognizer, agnostic], ["br"]
    )

    assert br_recognizer in filtered
    assert us_recognizer not in filtered
    # Locale-agnostic recognizers always survive the filter.
    assert agnostic in filtered


def test_country_filter_warns_on_unknown_country(caplog):
    """When a requested country has no matching recognizer in the input
    list, a WARNING is logged so silent zero-result filters are easier to
    debug."""
    from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
        RecognizerListLoader,
    )

    class _XUsRecognizer(PatternRecognizer):
        COUNTRY_CODE = "us"

        def __init__(self):
            super().__init__(
                supported_entity="X_US_THING",
                patterns=[Pattern("p", regex="REGEX", score=1.0)],
            )

    us_recognizer = _XUsRecognizer()

    with caplog.at_level("WARNING", logger="presidio-analyzer"):
        RecognizerListLoader.filter_by_countries([us_recognizer], ["br"])

    warning_messages = [r.getMessage() for r in caplog.records if r.levelname == "WARNING"]
    assert any("'br'" in m and "country_code" in m for m in warning_messages), (
        f"expected a country-filter WARNING mentioning 'br' and country_code, "
        f"got {warning_messages!r}"
    )


def test_supported_countries_via_loader_kwarg():
    """``RecognizerListLoader.get(supported_countries=...)`` applies the
    country filter inline alongside the language filter, mirroring how
    ``supported_languages`` is threaded through. This is what allows the
    same filter to be driven from a top-level YAML field with no extra
    plumbing in ``RecognizerRegistry``."""
    from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
        RecognizerConfigurationLoader,
        RecognizerListLoader,
    )

    configuration = RecognizerConfigurationLoader.get(
        registry_configuration={"global_regex_flags": 0}
    )
    recognizers = list(
        RecognizerListLoader.get(**configuration, supported_countries=["us"])
    )
    names = {type(rec).__name__ for rec in recognizers}

    assert "UsSsnRecognizer" in names
    assert "UkNinoRecognizer" not in names
    # Locale-agnostic recognizers survive the filter.
    assert "CreditCardRecognizer" in names


def test_get_country_codes_returns_loaded_countries():
    """``RecognizerRegistry.get_country_codes()`` aggregates the
    class-level ``COUNTRY_CODE`` across all loaded recognizers.

    The default registry is English-only and many predefined country
    recognizers are either disabled by default or scoped to non-English
    languages, so we assert the subset that actually loads: US and UK
    recognizers are enabled-by-default and English-language.
    """
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()

    codes = registry.get_country_codes()
    assert isinstance(codes, list)
    assert codes == sorted(codes), "country codes should be returned sorted"
    assert "us" in codes
    assert "uk" in codes
    # Every code returned is non-empty and lowercased (the contract).
    assert all(isinstance(c, str) and c == c.lower() and c for c in codes)


def test_get_country_codes_after_country_filter():
    """``get_country_codes()`` reflects the country filter applied at load."""
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(countries=["us"])

    assert registry.get_country_codes() == ["us"]


def test_get_country_codes_excludes_locale_agnostic_recognizers():
    """Filter out locale-agnostic recognizers from the country code report.

    Recognizers without a ``COUNTRY_CODE`` are never reported by
    ``get_country_codes`` even though they are present in the registry.
    """
    agnostic = create_mock_pattern_recognizer("en", "FOO", "Agnostic")
    assert agnostic.country_code() is None

    registry = RecognizerRegistry()
    registry.add_recognizer(agnostic)

    assert registry.get_country_codes() == []


def test_to_dict_does_not_carry_country_code():
    """Country tag is a class-level fact, not part of the to_dict payload.

    Serialized recognizers can be re-instantiated by class name; the
    country tag travels with the class definition rather than the
    instance dict.
    """
    rec = create_mock_pattern_recognizer("en", "FOO", "rec")
    assert "country_code" not in rec.to_dict()
