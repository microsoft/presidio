"""Tests for LangExtract recognizer hierarchy using mocks.

Tests the hierarchy: LMRecognizer -> LangExtractRecognizer -> OllamaLangExtractRecognizer

These tests use mocks to avoid requiring Ollama or actual LLM calls.
"""
import pytest
from unittest.mock import Mock, patch


class TestOllamaLangExtractRecognizerInitialization:
    """Test OllamaLangExtractRecognizer initialization and configuration loading."""

    def test_import_error_when_langextract_not_installed(self):
        """Test that ImportError is raised when langextract is not installed."""
        with patch(
            'presidio_analyzer.predefined_recognizers.third_party.'
            'langextract_recognizer.LANGEXTRACT_AVAILABLE',
            False
        ):
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ImportError, match="LangExtract is not installed"):
                OllamaLangExtractRecognizer()

    def test_initialization_with_mocked_ollama(self, tmp_path):
        """Test OllamaLangExtractRecognizer initialization with mocked Ollama server."""
        import yaml
        
        config = {
            "langextract": {
                "supported_entities": ["PERSON", "EMAIL_ADDRESS"],
                "entity_mappings": {"person": "PERSON", "email": "EMAIL_ADDRESS"},
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "min_score": 0.5,
            },
            "ollama": {
                "model_id": "gemma3:1b",
                "model_url": "http://localhost:11434",
                "temperature": 0.0,
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'ollama_langextract_recognizer.OllamaLangExtractRecognizer._check_ollama_server',
                   return_value=True), \
             patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'ollama_langextract_recognizer.OllamaLangExtractRecognizer._check_model_available',
                   return_value=True):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            recognizer = OllamaLangExtractRecognizer(config_path=str(config_file))
            
            # Verify initialization
            assert recognizer.model_id == "gemma3:1b"
            assert recognizer.model_url == "http://localhost:11434"
            assert len(recognizer.supported_entities) == 2
            assert "PERSON" in recognizer.supported_entities
            assert "EMAIL_ADDRESS" in recognizer.supported_entities
            
            # Verify inheritance hierarchy
            from presidio_analyzer.lm_recognizer import LMRecognizer
            from presidio_analyzer.predefined_recognizers.third_party.langextract_recognizer import LangExtractRecognizer
            assert isinstance(recognizer, OllamaLangExtractRecognizer)
            assert isinstance(recognizer, LangExtractRecognizer)
            assert isinstance(recognizer, LMRecognizer)

    def test_ollama_server_validation_failure(self, tmp_path):
        """Test that initialization fails when Ollama server is not available."""
        import yaml
        
        config = {
            "langextract": {
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "min_score": 0.5,
            },
            "ollama": {
                "model_id": "gemma3:1b",
                "model_url": "http://localhost:11434",
                "temperature": 0.0,
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'ollama_langextract_recognizer.OllamaLangExtractRecognizer._check_ollama_server',
                   return_value=False):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ConnectionError, match="Ollama server not reachable"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_ollama_model_validation_failure(self, tmp_path):
        """Test that initialization fails when Ollama model is not available."""
        import yaml
        
        config = {
            "langextract": {
                "supported_entities": ["PERSON"],
                "entity_mappings": {"person": "PERSON"},
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "min_score": 0.5,
            },
            "ollama": {
                "model_id": "gemma3:1b",
                "model_url": "http://localhost:11434",
                "temperature": 0.0,
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'ollama_langextract_recognizer.OllamaLangExtractRecognizer._check_ollama_server',
                   return_value=True), \
             patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'ollama_langextract_recognizer.OllamaLangExtractRecognizer._check_model_available',
                   return_value=False):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(RuntimeError, match="Model .* not found"):
                OllamaLangExtractRecognizer(config_path=str(config_file))


class TestOllamaLangExtractRecognizerAnalyze:
    """Test the analyze method with mocked LangExtract."""

    @pytest.fixture
    def mock_recognizer(self, tmp_path):
        """Fixture to create a mocked OllamaLangExtractRecognizer."""
        import yaml
        
        config = {
            "langextract": {
                "supported_entities": ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
                "entity_mappings": {
                    "person": "PERSON",
                    "email": "EMAIL_ADDRESS",
                    "phone": "PHONE_NUMBER"
                },
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "min_score": 0.5,
            },
            "ollama": {
                "model_id": "gemma3:1b",
                "model_url": "http://localhost:11434",
                "temperature": 0.0,
            }
        }

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'ollama_langextract_recognizer.OllamaLangExtractRecognizer._check_ollama_server',
                   return_value=True), \
             patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'ollama_langextract_recognizer.OllamaLangExtractRecognizer._check_model_available',
                   return_value=True):
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            return OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_analyze_with_person_entity(self, mock_recognizer):
        """Test analysis detecting a person entity with mocked LangExtract."""
        text = "My name is John Doe"

        # Create mock extraction
        mock_extraction = Mock()
        mock_extraction.extraction_class = "person"
        mock_extraction.extraction_text = "John Doe"
        mock_extraction.char_interval = Mock()
        mock_extraction.char_interval.start_pos = 11
        mock_extraction.char_interval.end_pos = 19
        mock_extraction.alignment_status = "MATCH_EXACT"
        mock_extraction.attributes = {"type": "full_name"}

        mock_result = Mock()
        mock_result.extractions = [mock_extraction]

        with patch('langextract.extract', return_value=mock_result):
            results = mock_recognizer.analyze(text, entities=["PERSON"])

        assert len(results) == 1
        assert results[0].entity_type == "PERSON"
        assert results[0].start == 11
        assert results[0].end == 19
        assert results[0].score == 0.95  # MATCH_EXACT score

    def test_analyze_with_multiple_entities(self, mock_recognizer):
        """Test analysis detecting multiple entity types."""
        text = "Contact John Doe at john@example.com or 555-1234"

        # Create mock extractions
        person_extraction = Mock()
        person_extraction.extraction_class = "person"
        person_extraction.extraction_text = "John Doe"
        person_extraction.char_interval = Mock(start_pos=8, end_pos=16)
        person_extraction.alignment_status = "MATCH_EXACT"
        person_extraction.attributes = {}

        email_extraction = Mock()
        email_extraction.extraction_class = "email"
        email_extraction.extraction_text = "john@example.com"
        email_extraction.char_interval = Mock(start_pos=20, end_pos=36)
        email_extraction.alignment_status = "MATCH_EXACT"
        email_extraction.attributes = {}

        phone_extraction = Mock()
        phone_extraction.extraction_class = "phone"
        phone_extraction.extraction_text = "555-1234"
        phone_extraction.char_interval = Mock(start_pos=40, end_pos=48)
        phone_extraction.alignment_status = "MATCH_FUZZY"
        phone_extraction.attributes = {}

        mock_result = Mock()
        mock_result.extractions = [person_extraction, email_extraction, phone_extraction]

        with patch('langextract.extract', return_value=mock_result):
            results = mock_recognizer.analyze(text)

        assert len(results) == 3
        assert results[0].entity_type == "PERSON"
        assert results[1].entity_type == "EMAIL_ADDRESS"
        assert results[2].entity_type == "PHONE_NUMBER"
        assert results[2].score == 0.80  # MATCH_FUZZY score

    def test_analyze_with_empty_text(self, mock_recognizer):
        """Test analysis with empty text returns no results."""
        results = mock_recognizer.analyze("")
        assert len(results) == 0

        results = mock_recognizer.analyze("   ")
        assert len(results) == 0

    def test_analyze_with_no_matching_entities(self, mock_recognizer):
        """Test analysis when requested entities don't match supported entities."""
        text = "Some text here"
        
        # Request unsupported entity type
        results = mock_recognizer.analyze(text, entities=["CREDIT_CARD"])
        assert len(results) == 0

    def test_analyze_filters_by_requested_entities(self, mock_recognizer):
        """Test that analysis only returns requested entity types."""
        text = "Contact John Doe at john@example.com"

        # Create mock extractions for both PERSON and EMAIL
        person_extraction = Mock()
        person_extraction.extraction_class = "person"
        person_extraction.extraction_text = "John Doe"
        person_extraction.char_interval = Mock(start_pos=8, end_pos=16)
        person_extraction.alignment_status = "MATCH_EXACT"
        person_extraction.attributes = {}

        email_extraction = Mock()
        email_extraction.extraction_class = "email"
        email_extraction.extraction_text = "john@example.com"
        email_extraction.char_interval = Mock(start_pos=20, end_pos=36)
        email_extraction.alignment_status = "MATCH_EXACT"
        email_extraction.attributes = {}

        mock_result = Mock()
        mock_result.extractions = [person_extraction, email_extraction]

        with patch('langextract.extract', return_value=mock_result):
            # Request only PERSON entities
            results = mock_recognizer.analyze(text, entities=["PERSON"])

        assert len(results) == 1
        assert results[0].entity_type == "PERSON"

    def test_analyze_respects_min_score(self, mock_recognizer):
        """Test that results below min_score are filtered out."""
        # Set min_score to 0.5 (default in config)
        text = "Some text"

        mock_extraction = Mock()
        mock_extraction.extraction_class = "person"
        mock_extraction.extraction_text = "Some text"
        mock_extraction.char_interval = Mock(start_pos=0, end_pos=9)
        mock_extraction.alignment_status = "NOT_ALIGNED"  # Score 0.60
        mock_extraction.attributes = {}

        mock_result = Mock()
        mock_result.extractions = [mock_extraction]

        with patch('langextract.extract', return_value=mock_result):
            results = mock_recognizer.analyze(text)

        # NOT_ALIGNED has score 0.60, which is above min_score 0.5
        assert len(results) == 1

    def test_analyze_handles_langextract_exception(self, mock_recognizer):
        """Test that exceptions from LangExtract are handled gracefully."""
        text = "Some text"

        with patch('langextract.extract', side_effect=Exception("LangExtract error")):
            results = mock_recognizer.analyze(text)

        # Should return empty list on exception
        assert len(results) == 0

    def test_analyze_skips_unknown_entity_mappings(self, mock_recognizer):
        """Test that extractions with unknown entity classes are skipped."""
        text = "Some text"

        mock_extraction = Mock()
        mock_extraction.extraction_class = "unknown_type"  # Not in entity_mappings
        mock_extraction.extraction_text = "Some text"
        mock_extraction.char_interval = Mock(start_pos=0, end_pos=9)
        mock_extraction.alignment_status = "MATCH_EXACT"
        mock_extraction.attributes = {}

        mock_result = Mock()
        mock_result.extractions = [mock_extraction]

        with patch('langextract.extract', return_value=mock_result):
            results = mock_recognizer.analyze(text)

        # Unknown entity type should be skipped
        assert len(results) == 0
