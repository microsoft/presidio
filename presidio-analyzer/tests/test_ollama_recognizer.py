"""Tests for LangExtract recognizer hierarchy using mocks."""
import pytest
import urllib.error
from unittest.mock import Mock, patch, MagicMock


def create_test_config(
    supported_entities=None,
    entity_mappings=None,
    model_id="gemma2:2b",
    model_url="http://localhost:11434",
    temperature=0.0,
    min_score=0.5,
    labels_to_ignore=None,
    enable_generic_consolidation=True
):
    """Create test config."""
    if supported_entities is None:
        supported_entities = ["PERSON", "EMAIL_ADDRESS"]
    if entity_mappings is None:
        entity_mappings = {"person": "PERSON", "email": "EMAIL_ADDRESS"}
    if labels_to_ignore is None:
        labels_to_ignore = []
    
    return {
        "lm_recognizer": {
            "supported_entities": supported_entities,
            "labels_to_ignore": labels_to_ignore,
            "enable_generic_consolidation": enable_generic_consolidation,
            "min_score": min_score,
        },
        "langextract": {
            "prompt_file": "langextract_prompts/default_pii_phi_prompt.j2",
            "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
            "model": {
                "model_id": model_id,
                "model_url": model_url,
                "temperature": temperature,
            },
            "entity_mappings": entity_mappings,
        }
    }


class TestOllamaLangExtractRecognizerInitialization:
    """Test OllamaLangExtractRecognizer initialization and configuration loading."""

    def test_when_langextract_not_installed_then_raises_import_error(self):
        """Test that ImportError is raised when langextract is not installed."""
        with patch(
            'presidio_analyzer.predefined_recognizers.third_party.'
            'langextract_recognizer.LANGEXTRACT_AVAILABLE',
            False
        ):
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ImportError, match="LangExtract is not installed"):
                OllamaLangExtractRecognizer()

    def test_when_initialized_with_mocked_ollama_then_succeeds(self, tmp_path):
        """Test OllamaLangExtractRecognizer initialization with mocked Ollama server."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON", "EMAIL_ADDRESS"],
            entity_mappings={"person": "PERSON", "email": "EMAIL_ADDRESS"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0,
            min_score=0.5
        )

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
            assert recognizer.name == "Ollama LangExtract PII"
            assert recognizer.model_id == "gemma2:2b"
            assert recognizer.model_url == "http://localhost:11434"
            assert len(recognizer.supported_entities) == 3  # PERSON, EMAIL_ADDRESS, GENERIC_PII_ENTITY
            assert "PERSON" in recognizer.supported_entities
            assert "EMAIL_ADDRESS" in recognizer.supported_entities
            assert "GENERIC_PII_ENTITY" in recognizer.supported_entities
            
            # Verify inheritance hierarchy
            from presidio_analyzer.lm_recognizer import LMRecognizer
            from presidio_analyzer.predefined_recognizers.third_party.langextract_recognizer import LangExtractRecognizer
            assert isinstance(recognizer, OllamaLangExtractRecognizer)
            assert isinstance(recognizer, LangExtractRecognizer)
            assert isinstance(recognizer, LMRecognizer)

    def test_when_ollama_server_unreachable_then_raises_connection_error(self, tmp_path):
        """Test that initializing with unreachable Ollama server raises ConnectionError."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

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

    def test_when_ollama_model_unavailable_then_raises_runtime_error(self, tmp_path):
        """Test that initializing with unavailable model raises RuntimeError."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

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

    def test_when_config_file_missing_then_raises_file_not_found_error(self):
        """Test FileNotFoundError when config file doesn't exist."""
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True):
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(FileNotFoundError, match="Configuration file not found"):
                OllamaLangExtractRecognizer(config_path="/nonexistent/path.yaml")

    def test_when_model_section_missing_then_raises_value_error(self, tmp_path):
        """Test ValueError when config missing 'langextract.model' section."""
        import yaml
        
        config = {
            "lm_recognizer": {
                "supported_entities": ["PERSON"],
                "labels_to_ignore": [],
                "enable_generic_consolidation": True,
                "min_score": 0.5,
            },
            "langextract": {
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.j2",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "entity_mappings": {"person": "PERSON"},
                # Missing 'model' section
            }
        }
        
        config_file = tmp_path / "bad_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True):
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ValueError, match="must contain 'langextract.model' section"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_model_id_missing_then_raises_value_error(self, tmp_path):
        """Test ValueError when model_id is missing."""
        import yaml
        
        config = {
            "lm_recognizer": {
                "supported_entities": ["PERSON"],
                "labels_to_ignore": [],
                "enable_generic_consolidation": True,
                "min_score": 0.5,
            },
            "langextract": {
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.j2",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "entity_mappings": {"person": "PERSON"},
                "model": {
                    "model_url": "http://localhost:11434"
                    # Missing model_id
                }
            }
        }
        
        config_file = tmp_path / "bad_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True):
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ValueError, match="must contain 'model_id'"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_model_url_missing_then_raises_value_error(self, tmp_path):
        """Test ValueError when model_url is missing."""
        import yaml
        
        config = {
            "lm_recognizer": {
                "supported_entities": ["PERSON"],
                "labels_to_ignore": [],
                "enable_generic_consolidation": True,
                "min_score": 0.5,
            },
            "langextract": {
                "prompt_file": "langextract_prompts/default_pii_phi_prompt.j2",
                "examples_file": "langextract_prompts/default_pii_phi_examples.yaml",
                "entity_mappings": {"person": "PERSON"},
                "model": {
                    "model_id": "gemma2:2b"
                    # Missing model_url
                }
            }
        }
        
        config_file = tmp_path / "bad_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True):
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ValueError, match="must contain 'model_url'"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_server_returns_http_error_then_init_raises_connection_error(self, tmp_path):
        """Test that HTTP errors from Ollama server cause ConnectionError during init."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # Mock urlopen to raise HTTPError - this tests _check_ollama_server internally
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('urllib.request.urlopen', 
                   side_effect=urllib.error.HTTPError(None, 500, "Server Error", None, None)):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ConnectionError, match="Ollama server not reachable"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_server_times_out_then_init_raises_connection_error(self, tmp_path):
        """Test that timeout from Ollama server causes ConnectionError during init."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # Mock urlopen to raise TimeoutError - this tests _check_ollama_server internally
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('urllib.request.urlopen', side_effect=TimeoutError("Connection timeout")):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ConnectionError, match="Ollama server not reachable"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_server_returns_url_error_then_init_raises_connection_error(self, tmp_path):
        """Test that URLError from Ollama server causes ConnectionError during init."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # Mock urlopen to raise URLError - this tests _check_ollama_server internally
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('urllib.request.urlopen', side_effect=urllib.error.URLError("Connection refused")):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(ConnectionError, match="Ollama server not reachable"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_model_list_returns_invalid_json_then_init_raises_runtime_error(self, tmp_path):
        """Test that invalid JSON from model list API causes RuntimeError during init."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # Mock response with invalid JSON - this tests _check_model_available internally
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value.decode.return_value = "invalid json"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('urllib.request.urlopen', return_value=mock_response):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(RuntimeError, match="Model .* not found"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_model_list_is_empty_then_init_raises_runtime_error(self, tmp_path):
        """Test that empty model list from API causes RuntimeError during init."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # Mock response with empty models list - this tests _check_model_available internally
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value.decode.return_value = '{"models": []}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('urllib.request.urlopen', return_value=mock_response):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(RuntimeError, match="Model .* not found"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_model_exists_but_name_does_not_match_then_init_raises_runtime_error(self, tmp_path):
        """Test that non-matching model name causes RuntimeError during init."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # Mock response with different model - this tests _check_model_available internally
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value.decode.return_value = '{"models": [{"name": "llama2:latest"}]}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('urllib.request.urlopen', return_value=mock_response):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(RuntimeError, match="Model .* not found"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_model_check_raises_exception_then_init_raises_runtime_error(self, tmp_path):
        """Test that exceptions during model check cause RuntimeError during init."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON"],
            entity_mappings={"person": "PERSON"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0
        )

        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        # First call succeeds (server check), second call fails (model check)
        # This tests _check_model_available exception handling internally
        responses = [
            MagicMock(status=200, __enter__=Mock(side_effect=lambda: responses[0]), __exit__=Mock(return_value=False)),
            Exception("Network error")
        ]
        
        with patch('presidio_analyzer.predefined_recognizers.third_party.'
                   'langextract_recognizer.LANGEXTRACT_AVAILABLE', True), \
             patch('urllib.request.urlopen', side_effect=responses):
            
            from presidio_analyzer.predefined_recognizers.third_party.ollama_langextract_recognizer import OllamaLangExtractRecognizer
            with pytest.raises(RuntimeError, match="Model .* not found"):
                OllamaLangExtractRecognizer(config_path=str(config_file))

    def test_when_initialized_then_prompt_template_loads_correctly(self, tmp_path):
        """Test that _load_prompt_file loads the Jinja2 template."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON", "EMAIL_ADDRESS"],
            entity_mappings={"person": "PERSON", "email": "EMAIL_ADDRESS"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434"
        )

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

            # Verify prompt_template is loaded (raw Jinja2 template)
            assert recognizer.prompt_template is not None
            assert len(recognizer.prompt_template) > 0
            assert "{% for entity in supported_entities %}" in recognizer.prompt_template
            assert "ENTITY TYPES TO EXTRACT:" in recognizer.prompt_template

    def test_when_initialized_then_examples_load_correctly(self, tmp_path):
        """Test that _load_examples_file loads and converts examples to LangExtract format."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON", "EMAIL_ADDRESS"],
            entity_mappings={"person": "PERSON", "email": "EMAIL_ADDRESS"},
            model_id="gemma2:2b",
            model_url="http://localhost:11434"
        )

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

            # Verify examples are loaded
            assert recognizer.examples is not None
            assert len(recognizer.examples) > 0
            
            # Verify examples are LangExtract ExampleData objects
            import langextract as lx
            assert all(isinstance(ex, lx.data.ExampleData) for ex in recognizer.examples)
            
            # Verify each example has text and extractions
            for example in recognizer.examples:
                assert hasattr(example, 'text')
                assert hasattr(example, 'extractions')
                assert example.text is not None
                assert isinstance(example.extractions, list)

    def test_when_initialized_then_prompt_renders_with_entities_from_config(self, tmp_path):
        """Test that _render_prompt creates final prompt with entities from config."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
            entity_mappings={"person": "PERSON", "email": "EMAIL_ADDRESS", "phone": "PHONE_NUMBER"},
            labels_to_ignore=["metadata", "annotation"],
            enable_generic_consolidation=True,
            model_id="gemma2:2b",
            model_url="http://localhost:11434"
        )

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

            # Verify prompt_description is the rendered result
            assert recognizer.prompt_description is not None
            assert len(recognizer.prompt_description) > 0
            
            # Should NOT contain Jinja2 syntax (means it was rendered)
            assert "{% for" not in recognizer.prompt_description
            assert "{%- endfor %}" not in recognizer.prompt_description
            
            # Check that supported entities appear in the rendered prompt
            assert "PERSON" in recognizer.prompt_description
            assert "EMAIL_ADDRESS" in recognizer.prompt_description
            assert "PHONE_NUMBER" in recognizer.prompt_description
            assert "GENERIC_PII_ENTITY" in recognizer.prompt_description  # Added by default
            
            # Check that labels_to_ignore appear in the DO NOT EXTRACT section
            assert "metadata" in recognizer.prompt_description
            assert "annotation" in recognizer.prompt_description
            assert "DO NOT EXTRACT" in recognizer.prompt_description
            
            # Verify the prompt mentions generic consolidation
            assert "UNKNOWN ENTITIES" in recognizer.prompt_description


class TestOllamaLangExtractRecognizerAnalyze:
    """Test the analyze method with mocked LangExtract."""

    @pytest.fixture
    def mock_recognizer(self, tmp_path):
        """Fixture to create a mocked OllamaLangExtractRecognizer."""
        import yaml
        
        config = create_test_config(
            supported_entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
            entity_mappings={
                "person": "PERSON",
                "email": "EMAIL_ADDRESS",
                "phone": "PHONE_NUMBER"
            },
            model_id="gemma2:2b",
            model_url="http://localhost:11434",
            temperature=0.0,
            min_score=0.5
        )

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

    def test_when_text_contains_person_then_detects_entity(self, mock_recognizer):
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

    def test_when_text_contains_multiple_entities_then_detects_all(self, mock_recognizer):
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

    def test_when_text_is_empty_then_returns_no_results(self, mock_recognizer):
        """Test analysis with empty text returns no results."""
        results = mock_recognizer.analyze("")
        assert len(results) == 0

        results = mock_recognizer.analyze("   ")
        assert len(results) == 0

    def test_when_no_entities_match_then_returns_empty_list(self, mock_recognizer):
        """Test analysis when requested entities don't match supported entities."""
        text = "Some text here"
        
        # Request unsupported entity type
        results = mock_recognizer.analyze(text, entities=["CREDIT_CARD"])
        assert len(results) == 0

    def test_when_entities_requested_then_filters_results(self, mock_recognizer):
        """Test that analyze filters results based on requested entities."""
        from presidio_analyzer import RecognizerResult
        
        text = "Contact John Doe at john@example.com"

        # Create RecognizerResult objects (what _call_llm returns)
        person_result = RecognizerResult(
            entity_type="PERSON",
            start=8,
            end=16,
            score=0.95
        )
        
        email_result = RecognizerResult(
            entity_type="EMAIL_ADDRESS",
            start=20,
            end=36,
            score=0.95
        )

        with patch.object(mock_recognizer, '_call_llm', return_value=[person_result, email_result]):
            # Request only PERSON entities - EMAIL_ADDRESS should be filtered out by analyze()
            results = mock_recognizer.analyze(text, entities=["PERSON"])

        # Should only return PERSON, EMAIL_ADDRESS filtered by analyze() method
        assert len(results) == 1
        assert results[0].entity_type == "PERSON"
        assert results[0].start == 8
        assert results[0].end == 16

    def test_when_min_score_set_then_filters_low_confidence_results(self, mock_recognizer):
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

    def test_when_langextract_raises_exception_then_returns_empty_list(self, mock_recognizer):
        """Test that exceptions from LangExtract are handled gracefully."""
        text = "Some text"

        with patch('langextract.extract', side_effect=Exception("LangExtract error")):
            results = mock_recognizer.analyze(text)

        # Should return empty list on exception
        assert len(results) == 0

    def test_when_entity_has_no_mapping_and_consolidation_enabled_then_creates_generic(
        self, mock_recognizer
    ):
        """Test that extractions with unknown entity classes become GENERIC_PII_ENTITY."""
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

        # Unknown entity type should be consolidated to GENERIC_PII_ENTITY
        assert len(results) == 1
        assert results[0].entity_type == "GENERIC_PII_ENTITY"
        assert results[0].recognition_metadata["original_entity_type"] == "UNKNOWN_TYPE"
        assert results[0].start == 0
        assert results[0].end == 9

    def test_when_entity_has_no_mapping_and_consolidation_disabled_then_skips(self, tmp_path):
        """Test that unknown entities are skipped when consolidation is disabled."""
        import yaml
        
        # Create config with consolidation disabled
        config = create_test_config(
            supported_entities=["PERSON", "EMAIL_ADDRESS"],
            entity_mappings={"person": "PERSON", "email": "EMAIL_ADDRESS"},
            enable_generic_consolidation=False
        )

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
            results = recognizer.analyze(text)

        # Unknown entity type should be skipped when consolidation is disabled
        assert len(results) == 0
