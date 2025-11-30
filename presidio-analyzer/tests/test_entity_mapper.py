"""Tests for llm_utils.entity_mapper module."""
import pytest
from presidio_analyzer import RecognizerResult, AnalysisExplanation
from presidio_analyzer.llm_utils.entity_mapper import (
    GENERIC_PII_ENTITY,
    filter_results_by_labels,
    filter_results_by_score,
    filter_results_by_entities,
    validate_result_positions,
    consolidate_generic_entities,
    skip_unmapped_entities,
    ensure_generic_entity_support,
)


def create_test_result(
    entity_type="PERSON",
    start=0,
    end=10,
    score=0.9,
    recognition_metadata=None
):
    """Helper to create RecognizerResult for testing."""
    return RecognizerResult(
        entity_type=entity_type,
        start=start,
        end=end,
        score=score,
        analysis_explanation=AnalysisExplanation(
            recognizer="TestRecognizer",
            original_score=score,
            textual_explanation="Test"
        ),
        recognition_metadata=recognition_metadata
    )


class TestFilterResultsByLabels:
    """Tests for filter_results_by_labels function."""

    def test_when_no_ignored_labels_then_returns_all_results(self):
        """Test that all results are returned when no labels are ignored."""
        results = [
            create_test_result("PERSON"),
            create_test_result("EMAIL_ADDRESS"),
        ]

        filtered = filter_results_by_labels(results, [])

        assert len(filtered) == 2

    def test_when_result_matches_ignored_label_then_filters_out(self):
        """Test that results with ignored labels are filtered out."""
        results = [
            create_test_result("PERSON"),
            create_test_result("SYSTEM"),
            create_test_result("EMAIL_ADDRESS"),
        ]

        filtered = filter_results_by_labels(results, ["system"])

        assert len(filtered) == 2
        assert all(r.entity_type != "SYSTEM" for r in filtered)

    def test_when_multiple_ignored_labels_then_filters_all(self):
        """Test filtering multiple ignored labels."""
        results = [
            create_test_result("PERSON"),
            create_test_result("SYSTEM"),
            create_test_result("METADATA"),
            create_test_result("EMAIL_ADDRESS"),
        ]

        filtered = filter_results_by_labels(results, ["system", "metadata"])

        assert len(filtered) == 2
        entity_types = [r.entity_type for r in filtered]
        assert "PERSON" in entity_types
        assert "EMAIL_ADDRESS" in entity_types

    def test_when_label_matching_is_case_insensitive(self):
        """Test that label matching is case-insensitive."""
        results = [
            create_test_result("PERSON"),
            create_test_result("System"),
        ]

        filtered = filter_results_by_labels(results, ["SYSTEM"])

        assert len(filtered) == 1
        assert filtered[0].entity_type == "PERSON"

    def test_when_result_has_no_entity_type_then_skips_with_warning(self):
        """Test that results without entity_type are skipped."""
        result_without_type = RecognizerResult(
            entity_type=None,
            start=0,
            end=10,
            score=0.9
        )
        results = [
            result_without_type,
            create_test_result("PERSON"),
        ]

        filtered = filter_results_by_labels(results, [])

        assert len(filtered) == 1
        assert filtered[0].entity_type == "PERSON"


class TestFilterResultsByScore:
    """Tests for filter_results_by_score function."""

    def test_when_all_results_above_threshold_then_returns_all(self):
        """Test that all results above threshold are returned."""
        results = [
            create_test_result("PERSON", score=0.9),
            create_test_result("EMAIL_ADDRESS", score=0.8),
        ]

        filtered = filter_results_by_score(results, min_score=0.5)

        assert len(filtered) == 2

    def test_when_result_below_threshold_then_filters_out(self):
        """Test that results below threshold are filtered out."""
        results = [
            create_test_result("PERSON", score=0.9),
            create_test_result("EMAIL_ADDRESS", score=0.4),
            create_test_result("PHONE_NUMBER", score=0.7),
        ]

        filtered = filter_results_by_score(results, min_score=0.5)

        assert len(filtered) == 2
        scores = [r.score for r in filtered]
        assert all(s >= 0.5 for s in scores)

    def test_when_result_equals_threshold_then_includes(self):
        """Test that results exactly at threshold are included."""
        results = [
            create_test_result("PERSON", score=0.5),
        ]

        filtered = filter_results_by_score(results, min_score=0.5)

        assert len(filtered) == 1

    def test_when_min_score_is_zero_then_returns_all(self):
        """Test that min_score=0 includes all results."""
        results = [
            create_test_result("PERSON", score=0.1),
            create_test_result("EMAIL_ADDRESS", score=0.9),
        ]

        filtered = filter_results_by_score(results, min_score=0.0)

        assert len(filtered) == 2

    def test_when_min_score_is_one_then_only_perfect_scores(self):
        """Test that min_score=1.0 only includes perfect scores."""
        results = [
            create_test_result("PERSON", score=1.0),
            create_test_result("EMAIL_ADDRESS", score=0.99),
        ]

        filtered = filter_results_by_score(results, min_score=1.0)

        assert len(filtered) == 1
        assert filtered[0].entity_type == "PERSON"


class TestFilterResultsByEntities:
    """Tests for filter_results_by_entities function."""

    def test_when_no_requested_entities_then_returns_all(self):
        """Test that all results are returned when requested_entities is empty."""
        results = [
            create_test_result("PERSON"),
            create_test_result("EMAIL_ADDRESS"),
        ]

        filtered = filter_results_by_entities(results, [])

        assert len(filtered) == 2

    def test_when_result_matches_requested_entity_then_includes(self):
        """Test that only requested entities are included."""
        results = [
            create_test_result("PERSON"),
            create_test_result("EMAIL_ADDRESS"),
            create_test_result("PHONE_NUMBER"),
        ]

        filtered = filter_results_by_entities(results, ["PERSON", "PHONE_NUMBER"])

        assert len(filtered) == 2
        entity_types = [r.entity_type for r in filtered]
        assert "PERSON" in entity_types
        assert "PHONE_NUMBER" in entity_types
        assert "EMAIL_ADDRESS" not in entity_types

    def test_when_result_not_in_requested_entities_then_filters_out(self):
        """Test that non-requested entities are filtered out."""
        results = [
            create_test_result("PERSON"),
            create_test_result("UNKNOWN_TYPE"),
        ]

        filtered = filter_results_by_entities(results, ["PERSON"])

        assert len(filtered) == 1
        assert filtered[0].entity_type == "PERSON"


class TestValidateResultPositions:
    """Tests for validate_result_positions function."""

    def test_when_all_results_have_positions_then_returns_all(self):
        """Test that results with valid positions are returned."""
        results = [
            create_test_result("PERSON", start=0, end=10),
            create_test_result("EMAIL_ADDRESS", start=20, end=40),
        ]

        filtered = validate_result_positions(results)

        assert len(filtered) == 2

    def test_when_result_missing_start_then_filters_out(self):
        """Test that results with missing start are filtered out."""
        valid_result = create_test_result("PERSON", start=0, end=10)
        invalid_result = RecognizerResult(
            entity_type="EMAIL_ADDRESS",
            start=None,
            end=40,
            score=0.9
        )

        filtered = validate_result_positions([valid_result, invalid_result])

        assert len(filtered) == 1
        assert filtered[0].entity_type == "PERSON"

    def test_when_result_missing_end_then_filters_out(self):
        """Test that results with missing end are filtered out."""
        valid_result = create_test_result("PERSON", start=0, end=10)
        invalid_result = RecognizerResult(
            entity_type="EMAIL_ADDRESS",
            start=20,
            end=None,
            score=0.9
        )

        filtered = validate_result_positions([valid_result, invalid_result])

        assert len(filtered) == 1
        assert filtered[0].entity_type == "PERSON"

    def test_when_result_missing_both_positions_then_filters_out(self):
        """Test that results with both positions missing are filtered out."""
        valid_result = create_test_result("PERSON", start=0, end=10)
        invalid_result = RecognizerResult(
            entity_type="EMAIL_ADDRESS",
            start=None,
            end=None,
            score=0.9
        )

        filtered = validate_result_positions([valid_result, invalid_result])

        assert len(filtered) == 1


class TestConsolidateGenericEntities:
    """Tests for consolidate_generic_entities function."""

    def test_when_entity_supported_then_keeps_original(self):
        """Test that supported entities are not modified."""
        results = [
            create_test_result("PERSON"),
        ]
        supported_entities = ["PERSON", "EMAIL_ADDRESS"]
        logged_entities = set()

        processed = consolidate_generic_entities(results, supported_entities, logged_entities)

        assert len(processed) == 1
        assert processed[0].entity_type == "PERSON"

    def test_when_entity_unsupported_then_consolidates_to_generic(self):
        """Test that unsupported entities are consolidated to GENERIC_PII_ENTITY."""
        results = [
            create_test_result("UNKNOWN_TYPE"),
        ]
        supported_entities = ["PERSON"]
        logged_entities = set()

        processed = consolidate_generic_entities(results, supported_entities, logged_entities)

        assert len(processed) == 1
        assert processed[0].entity_type == GENERIC_PII_ENTITY

    def test_when_entity_consolidated_then_stores_original_in_metadata(self):
        """Test that original entity type is stored in metadata."""
        results = [
            create_test_result("UNKNOWN_TYPE"),
        ]
        supported_entities = ["PERSON"]
        logged_entities = set()

        processed = consolidate_generic_entities(results, supported_entities, logged_entities)

        assert processed[0].recognition_metadata is not None
        assert processed[0].recognition_metadata["original_entity_type"] == "UNKNOWN_TYPE"

    def test_when_entity_already_has_metadata_then_adds_original_type(self):
        """Test that original_entity_type is added to existing metadata."""
        results = [
            create_test_result("UNKNOWN_TYPE", recognition_metadata={"key": "value"}),
        ]
        supported_entities = ["PERSON"]
        logged_entities = set()

        processed = consolidate_generic_entities(results, supported_entities, logged_entities)

        assert processed[0].recognition_metadata["key"] == "value"
        assert processed[0].recognition_metadata["original_entity_type"] == "UNKNOWN_TYPE"

    def test_when_unknown_entity_first_seen_then_logs_to_set(self):
        """Test that first occurrence of unknown entity is added to logged set."""
        results = [
            create_test_result("UNKNOWN_TYPE"),
        ]
        supported_entities = ["PERSON"]
        logged_entities = set()

        consolidate_generic_entities(results, supported_entities, logged_entities)

        assert "UNKNOWN_TYPE" in logged_entities

    def test_when_unknown_entity_seen_again_then_not_logged_twice(self):
        """Test that same unknown entity is only logged once."""
        results = [
            create_test_result("UNKNOWN_TYPE"),
            create_test_result("UNKNOWN_TYPE"),
        ]
        supported_entities = ["PERSON"]
        logged_entities = set()

        consolidate_generic_entities(results, supported_entities, logged_entities)

        assert len([e for e in logged_entities if e == "UNKNOWN_TYPE"]) == 1


class TestSkipUnmappedEntities:
    """Tests for skip_unmapped_entities function."""

    def test_when_entity_supported_then_includes(self):
        """Test that supported entities are included."""
        results = [
            create_test_result("PERSON"),
            create_test_result("EMAIL_ADDRESS"),
        ]
        supported_entities = ["PERSON", "EMAIL_ADDRESS"]

        filtered = skip_unmapped_entities(results, supported_entities)

        assert len(filtered) == 2

    def test_when_entity_unsupported_then_skips(self):
        """Test that unsupported entities are skipped."""
        results = [
            create_test_result("PERSON"),
            create_test_result("UNKNOWN_TYPE"),
        ]
        supported_entities = ["PERSON"]

        filtered = skip_unmapped_entities(results, supported_entities)

        assert len(filtered) == 1
        assert filtered[0].entity_type == "PERSON"

    def test_when_multiple_unsupported_then_skips_all(self):
        """Test that multiple unsupported entities are all skipped."""
        results = [
            create_test_result("PERSON"),
            create_test_result("UNKNOWN1"),
            create_test_result("UNKNOWN2"),
        ]
        supported_entities = ["PERSON"]

        filtered = skip_unmapped_entities(results, supported_entities)

        assert len(filtered) == 1


class TestEnsureGenericEntitySupport:
    """Tests for ensure_generic_entity_support function."""

    def test_when_consolidation_enabled_and_generic_missing_then_adds_generic(self):
        """Test that GENERIC_PII_ENTITY is added when consolidation is enabled."""
        supported_entities = ["PERSON", "EMAIL_ADDRESS"]

        result = ensure_generic_entity_support(supported_entities, enable_generic_consolidation=True)

        assert GENERIC_PII_ENTITY in result
        assert "PERSON" in result
        assert "EMAIL_ADDRESS" in result

    def test_when_consolidation_disabled_then_does_not_add_generic(self):
        """Test that GENERIC_PII_ENTITY is not added when consolidation is disabled."""
        supported_entities = ["PERSON", "EMAIL_ADDRESS"]

        result = ensure_generic_entity_support(supported_entities, enable_generic_consolidation=False)

        assert GENERIC_PII_ENTITY not in result
        assert len(result) == 2

    def test_when_generic_already_present_and_consolidation_enabled_then_no_duplicate(self):
        """Test that GENERIC_PII_ENTITY is not duplicated."""
        supported_entities = ["PERSON", GENERIC_PII_ENTITY]

        result = ensure_generic_entity_support(supported_entities, enable_generic_consolidation=True)

        # Count occurrences of GENERIC_PII_ENTITY
        generic_count = result.count(GENERIC_PII_ENTITY)
        assert generic_count == 1

    def test_when_original_list_not_modified(self):
        """Test that original list is not modified (returns a copy)."""
        original = ["PERSON", "EMAIL_ADDRESS"]
        
        result = ensure_generic_entity_support(original, enable_generic_consolidation=True)

        assert GENERIC_PII_ENTITY not in original  # Original unchanged
        assert GENERIC_PII_ENTITY in result  # Result has it

    def test_when_empty_list_and_consolidation_enabled_then_adds_generic(self):
        """Test that GENERIC_PII_ENTITY is added to empty list."""
        result = ensure_generic_entity_support([], enable_generic_consolidation=True)

        assert len(result) == 1
        assert result[0] == GENERIC_PII_ENTITY


class TestGenericPiiEntityConstant:
    """Tests for GENERIC_PII_ENTITY constant."""

    def test_generic_pii_entity_is_string(self):
        """Test that GENERIC_PII_ENTITY is a string."""
        assert isinstance(GENERIC_PII_ENTITY, str)

    def test_generic_pii_entity_value(self):
        """Test the expected value of GENERIC_PII_ENTITY."""
        assert GENERIC_PII_ENTITY == "GENERIC_PII_ENTITY"
