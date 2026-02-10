
import functools

from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
    RecognizerListLoader,
)


class NoKwargsPlural:
    """Mock class that accepts only supported_entities (plural)."""

    def __init__(self, supported_entities=None):
        pass


class NoKwargsSingular:
    """Mock class that accepts only supported_entity (singular)."""

    def __init__(self, supported_entity=None):
        pass


class VarKwargsOnly:
    """Mock class that accepts only **kwargs."""

    def __init__(self, **kwargs):
        pass


class NoKwargsNone:
    """Mock class that accepts neither supported_entity nor supported_entities."""

    def __init__(self):
        pass


class Uninspectable:
    """Mock class where signature inspection fails."""

    __init__ = 123


class StrictParent:
    """Parent class that accepts only supported_entities (no **kwargs)."""

    def __init__(self, supported_entities=None):
        pass


class ChildForwardsKwargs(StrictParent):
    """Child class that accepts **kwargs and forwards to parent."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Helper: partial to avoid passing empty lang_conf every time
prepare = functools.partial(
    RecognizerListLoader._prepare_recognizer_kwargs, language_conf={}
)


def test_cleanup_none_removes_entity_keys():
    """Test that explicit None values for entity keys are removed."""
    kwargs = prepare(
        recognizer_conf={"supported_entity": None, "supported_entities": None},
        recognizer_cls=NoKwargsNone,
    )
    assert "supported_entity" not in kwargs
    assert "supported_entities" not in kwargs


def test_plural_only_signature_keeps_plural_and_drops_singular():
    """Test that plural kept, singular dropped for plural-only class."""
    kwargs = prepare(
        recognizer_conf={"supported_entities": ["ENT"], "supported_entity": "X"},
        recognizer_cls=NoKwargsPlural,
    )
    assert kwargs["supported_entities"] == ["ENT"]
    assert "supported_entity" not in kwargs


def test_singular_only_signature_converts_plural_to_singular():
    """Test that plural key is converted to singular for singular-only class."""
    kwargs = prepare(
        recognizer_conf={"supported_entities": ["ENT"]}, recognizer_cls=NoKwargsSingular
    )
    assert kwargs["supported_entity"] == "ENT"
    assert "supported_entities" not in kwargs


def test_singular_only_signature_keeps_singular_if_provided():
    """Test that singular key is preserved if provided for singular-only class."""
    kwargs = prepare(
        recognizer_conf={"supported_entity": "ENT_S"}, recognizer_cls=NoKwargsSingular
    )
    assert kwargs["supported_entity"] == "ENT_S"
    assert "supported_entities" not in kwargs


def test_no_kwargs_signature_removes_both():
    """Test that both entity keys are removed if class accepts neither."""
    kwargs = prepare(
        recognizer_conf={"supported_entities": ["ENT"], "supported_entity": "X"},
        recognizer_cls=NoKwargsNone,
    )
    assert "supported_entities" not in kwargs
    assert "supported_entity" not in kwargs


def test_var_kwargs_preserves_plural_but_drops_singular_for_safety():
    """Test that plural is kept (compat) but singular is dropped (safety)."""
    kwargs = prepare(
        recognizer_conf={"supported_entities": ["ENT"], "supported_entity": "X"},
        recognizer_cls=VarKwargsOnly,
    )
    assert kwargs["supported_entities"] == ["ENT"]
    assert "supported_entity" not in kwargs


def test_uninspectable_signature_drops_entity_keys():
    """Test that entity keys are dropped if signature inspection fails."""
    kwargs = prepare(
        recognizer_conf={"supported_entities": ["ENT"], "supported_entity": "X"},
        recognizer_cls=Uninspectable,
    )
    assert "supported_entities" not in kwargs
    assert "supported_entity" not in kwargs


def test_inheritance_forwarding_does_not_crash():
    """Test that inheritance forwarding to strict parent does not crash."""
    # Verify both:
    # 1. dangerous 'supported_entity' (singular) is removed to prevent crash.
    # 2. valid 'supported_entities' (plural) is preserved for compatibility.
    input_kwargs = {"supported_entity": "BAD", "supported_entities": ["ENT"]}
    kwargs = prepare(recognizer_conf=input_kwargs, recognizer_cls=ChildForwardsKwargs)

    # This ensures it doesn't crash when instantiated
    ChildForwardsKwargs(**kwargs)

    assert "supported_entity" not in kwargs
    assert kwargs["supported_entities"] == ["ENT"]
