"""Tests for LangExtract recognizer."""
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml

from presidio_analyzer import RecognizerResult
from presidio_analyzer.predefined_recognizers import LangExtractRecognizer


# Skip all tests if langextract is not installed
pytestmark = pytest.mark.skipif(
    not hasattr(LangExtractRecognizer, '__module__'),
    reason="langextract not installed"
)


@pytest.fixture
def mock_langextract():
    """Mock langextract module for testing without actual API calls."""
    with patch('presidio_analyzer.predefined_recognizers.third_party.langextract_recognizer.lx') as mock_lx:
        # Mock data classes
        mock_lx.data.Extraction = MagicMock
        mock_lx.data.ExampleData = MagicMock
        mock_lx.data.CharInterval = MagicMock
        mock_lx.data.AlignmentStatus = Mock()
        
        # Mock extract function
        mock_lx.extract = MagicMock()
        
        yield mock_lx


@pytest.fixture
def test_config_path(tmp_path):
    """Create a temporary test configuration file."""
    config = {
        "langextract": {
            "enabled": True,
            "model_id": "gemini-2.5-flash",
            "api_key_env_var": "TEST_LANGEXTRACT_API_KEY",
            "max_char_buffer": 1000,
            "batch_length": 10,
            "extraction_passes": 1,
            "max_workers": 5,
            "show_progress": False,
            "fetch_urls": True,
            "use_schema_constraints": True,
            "min_score": 0.5,
            "debug": False,
            "resolver_params": {
                "enable_fuzzy_alignment": True,
                "fuzzy_alignment_threshold": 0.75,
            },
            "language_model_params": {},
            "prompt_file": "langextract_prompts/default_pii_prompt.txt",
            "examples_file": "langextract_prompts/default_pii_examples.yaml",
            "prompt_validation_level": "WARNING",
            "prompt_validation_strict": False,
            "entity_mappings": {
                "person": "PERSON",
                "email": "EMAIL_ADDRESS",
                "phone": "PHONE_NUMBER",
                "ssn": "US_SSN",
            },
            "supported_entities": [
                "PERSON",
                "EMAIL_ADDRESS",
                "PHONE_NUMBER",
                "US_SSN",
            ]
        }
    }
    
    config_file = tmp_path / "test_langextract_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f)
    
    return str(config_file)


@pytest.fixture
def test_prompt_file(tmp_path):
    """Create a temporary prompt file."""
    prompt_dir = tmp_path / "langextract_prompts"
    prompt_dir.mkdir()
    
    prompt_file = prompt_dir / "default_pii_prompt.txt"
    prompt_file.write_text("Extract PII entities from the text.")
    
    return tmp_path


@pytest.fixture
def test_examples_file(tmp_path):
    """Create a temporary examples file."""
    prompt_dir = tmp_path / "langextract_prompts"
    if not prompt_dir.exists():
        prompt_dir.mkdir()
    
    examples = {
        "examples": [
            {
                "text": "John Doe's email is john@example.com",
                "extractions": [
                    {
                        "extraction_class": "person",
                        "extraction_text": "John Doe",
                        "attributes": {"type": "full_name"}
                    },
                    {
                        "extraction_class": "email",
                        "extraction_text": "john@example.com",
                        "attributes": {"type": "email_address"}
                    }
                ]
            }
        ]
    }
    
    examples_file = prompt_dir / "default_pii_examples.yaml"
    with open(examples_file, 'w') as f:
        yaml.dump(examples, f)
    
    return tmp_path


class TestLangExtractRecognizerInitialization:
    """Test recognizer initialization and configuration loading."""
    
    def test_import_error_when_langextract_not_installed(self):
        """Test that ImportError is raised when langextract is not installed."""
        with patch('presidio_analyzer.predefined_recognizers.third_party.langextract_recognizer.LANGEXTRACT_AVAILABLE', False):
            with pytest.raises(ImportError, match="LangExtract is not installed"):
                LangExtractRecognizer()
    
    def test_initialization_with_default_config(self, mock_langextract, monkeypatch):
        """Test recognizer initialization with default configuration."""
        # Mock the config file paths
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "model_id": "gemini-2.5-flash",
                "supported_entities": ["PERSON", "EMAIL_ADDRESS"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            recognizer = LangExtractRecognizer()
            
            assert recognizer.enabled is True
            assert recognizer.model_id == "gemini-2.5-flash"
            assert "PERSON" in recognizer.supported_entities
    
    def test_disabled_recognizer(self, mock_langextract):
        """Test that disabled recognizer still initializes but marks as disabled."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": False,
                "model_id": "gemini-2.5-flash",
                "supported_entities": [],
                "entity_mappings": {},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            recognizer = LangExtractRecognizer()
            
            assert recognizer.enabled is False
    
    # Removed: API key tests - LangExtract now uses Ollama only, no API keys


class TestLangExtractRecognizerAnalyze:
    """Test the analyze method with various scenarios."""
    
    def test_analyze_disabled_recognizer_returns_empty(self, mock_langextract):
        """Test that disabled recognizer returns empty results."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": False,
                "model_id": "gemini-2.5-flash",
                "supported_entities": [],
                "entity_mappings": {},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            recognizer = LangExtractRecognizer()
            results = recognizer.analyze("Test text")
            
            assert results == []
    
    def test_analyze_empty_text_returns_empty(self, mock_langextract):
        """Test that empty text returns empty results."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "model_id": "gemini-2.5-flash",
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            recognizer = LangExtractRecognizer()
            results = recognizer.analyze("")
            
            assert results == []
    
    def test_analyze_with_person_entity(self, mock_langextract):
        """Test analysis detecting a person entity."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "model_id": "gemini-2.5-flash",
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
                "min_score": 0.5,
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            # Mock LangExtract result
            mock_extraction = Mock()
            mock_extraction.extraction_class = "person"
            mock_extraction.extraction_text = "John Doe"
            mock_extraction.char_interval = Mock(start_pos=0, end_pos=8)
            mock_extraction.alignment_status = "MATCH_EXACT"
            mock_extraction.attributes = {"type": "full_name"}
            
            mock_result = Mock()
            mock_result.extractions = [mock_extraction]
            
            mock_langextract.extract.return_value = mock_result
            
            recognizer = LangExtractRecognizer()
            results = recognizer.analyze("John Doe is a person")
            
            assert len(results) == 1
            assert results[0].entity_type == "PERSON"
            assert results[0].start == 0
            assert results[0].end == 8
            assert results[0].score >= 0.5
    
    def test_analyze_with_multiple_entities(self, mock_langextract):
        """Test analysis detecting multiple entity types."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "model_id": "gemini-2.5-flash",
                "supported_entities": ["PERSON", "EMAIL_ADDRESS"],
                "entity_mappings": {
                    "person": "PERSON",
                    "email": "EMAIL_ADDRESS"
                },
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
                "min_score": 0.5,
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            # Mock LangExtract results
            mock_person = Mock()
            mock_person.extraction_class = "person"
            mock_person.extraction_text = "John Doe"
            mock_person.char_interval = Mock(start_pos=0, end_pos=8)
            mock_person.alignment_status = "MATCH_EXACT"
            mock_person.attributes = {}
            
            mock_email = Mock()
            mock_email.extraction_class = "email"
            mock_email.extraction_text = "john@example.com"
            mock_email.char_interval = Mock(start_pos=20, end_pos=36)
            mock_email.alignment_status = "MATCH_EXACT"
            mock_email.attributes = {}
            
            mock_result = Mock()
            mock_result.extractions = [mock_person, mock_email]
            
            mock_langextract.extract.return_value = mock_result
            
            recognizer = LangExtractRecognizer()
            text = "John Doe's email is john@example.com"
            results = recognizer.analyze(text)
            
            assert len(results) == 2
            entity_types = {r.entity_type for r in results}
            assert "PERSON" in entity_types
            assert "EMAIL_ADDRESS" in entity_types
    
    def test_analyze_filters_by_requested_entities(self, mock_langextract):
        """Test that only requested entities are returned."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "model_id": "gemini-2.5-flash",
                "supported_entities": ["PERSON", "EMAIL_ADDRESS"],
                "entity_mappings": {
                    "person": "PERSON",
                    "email": "EMAIL_ADDRESS"
                },
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
                "min_score": 0.5,
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            # Mock LangExtract results
            mock_person = Mock()
            mock_person.extraction_class = "person"
            mock_person.extraction_text = "John Doe"
            mock_person.char_interval = Mock(start_pos=0, end_pos=8)
            mock_person.alignment_status = "MATCH_EXACT"
            mock_person.attributes = {}
            
            mock_result = Mock()
            mock_result.extractions = [mock_person]
            
            mock_langextract.extract.return_value = mock_result
            
            recognizer = LangExtractRecognizer()
            # Only request EMAIL_ADDRESS
            results = recognizer.analyze("John Doe", entities=["EMAIL_ADDRESS"])
            
            # Should return empty since only EMAIL_ADDRESS was requested
            # but PERSON was detected
            assert len(results) == 0
    
    def test_analyze_applies_minimum_score_threshold(self, mock_langextract):
        """Test that extractions below minimum score are filtered out."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "model_id": "gemini-2.5-flash",
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
                "min_score": 0.8,  # High threshold
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            # Mock LangExtract result with fuzzy match (lower score)
            mock_extraction = Mock()
            mock_extraction.extraction_class = "person"
            mock_extraction.extraction_text = "John"
            mock_extraction.char_interval = Mock(start_pos=0, end_pos=4)
            mock_extraction.alignment_status = "MATCH_LESSER"  # Lower confidence
            mock_extraction.attributes = {}
            
            mock_result = Mock()
            mock_result.extractions = [mock_extraction]
            
            mock_langextract.extract.return_value = mock_result
            
            recognizer = LangExtractRecognizer()
            results = recognizer.analyze("John")
            
            # Should be filtered out due to low score
            assert len(results) == 0
    
    def test_analyze_handles_exception_gracefully(self, mock_langextract):
        """Test that exceptions during extraction are handled gracefully."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "model_id": "gemini-2.5-flash",
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            # Mock extraction to raise an exception
            mock_langextract.extract.side_effect = Exception("API Error")
            
            recognizer = LangExtractRecognizer()
            results = recognizer.analyze("Test text")
            
            # Should return empty list instead of crashing
            assert results == []


class TestLangExtractRecognizerScoreCalculation:
    """Test score calculation based on alignment status."""
    
    def test_score_for_exact_match(self, mock_langextract):
        """Test high score for exact matches."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
                "min_score": 0.5,
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            recognizer = LangExtractRecognizer()
            
            # Create mock extraction with exact match
            mock_extraction = Mock()
            mock_extraction.alignment_status = "MATCH_EXACT"
            
            score = recognizer._calculate_score(mock_extraction)
            assert score == 0.95


class TestLangExtractRecognizerEntityMapping:
    """Test entity mapping functionality."""
    
    def test_unmapped_entity_class_skipped(self, mock_langextract):
        """Test that extractions with unmapped classes are skipped."""
        with patch.object(LangExtractRecognizer, '_load_config') as mock_load_config, \
             patch.object(LangExtractRecognizer, '_load_prompt_file') as mock_load_prompt, \
             patch.object(LangExtractRecognizer, '_load_examples_file') as mock_load_examples:
            
            mock_load_config.return_value = {
                "enabled": True,
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},  # Only person mapped
                "prompt_file": "test.txt",
                "examples_file": "test.yaml",
                "min_score": 0.5,
            }
            mock_load_prompt.return_value = "Test prompt"
            mock_load_examples.return_value = []
            
            # Mock extraction with unmapped class
            mock_extraction = Mock()
            mock_extraction.extraction_class = "unknown_type"
            mock_extraction.extraction_text = "Something"
            mock_extraction.char_interval = Mock(start_pos=0, end_pos=9)
            mock_extraction.alignment_status = "MATCH_EXACT"
            mock_extraction.attributes = {}
            
            mock_result = Mock()
            mock_result.extractions = [mock_extraction]
            
            mock_langextract.extract.return_value = mock_result
            
            recognizer = LangExtractRecognizer()
            results = recognizer.analyze("Something")
            
            # Should be skipped
            assert len(results) == 0


# Integration tests with real Ollama (skip if not available)
@pytest.mark.skip_engine("langextract")
@pytest.fixture(scope="module")
def langextract_recognizer(langextract_recognizer_class):
    """Create LangExtractRecognizer instance for testing."""
    if not langextract_recognizer_class:
        return None
    
    recognizer = langextract_recognizer_class()
    recognizer.enabled = True  # Enable for testing
    return recognizer


@pytest.mark.skip_engine("langextract")
@pytest.mark.parametrize(
    "text, expected_entity_types",
    [
        # Test PERSON entity
        ("My name is John Doe", ["PERSON"]),
        ("Contact Jane Smith for details", ["PERSON"]),
        # Test EMAIL_ADDRESS entity
        ("Email me at john.doe@example.com", ["EMAIL_ADDRESS"]),
        # Test PHONE_NUMBER entity
        ("Call me at 555-123-4567", ["PHONE_NUMBER"]),
        # Test multiple entities
        ("John Doe's email is john@example.com and phone is 555-1234", 
         ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]),
    ],
)
def test_langextract_with_real_ollama(
    text,
    expected_entity_types,
    langextract_recognizer,
):
    """Test LangExtract recognizer with real Ollama model."""
    results = langextract_recognizer.analyze(text, entities=expected_entity_types)
    
    # Should detect at least some entities
    assert len(results) > 0
    
    # Check that detected entities match expected types
    detected_types = {r.entity_type for r in results}
    assert detected_types.intersection(set(expected_entity_types))
    
    # Check score range
    for result in results:
        assert 0.0 <= result.score <= 1.0
        assert result.start >= 0
        assert result.end <= len(text)
        assert result.start < result.end
