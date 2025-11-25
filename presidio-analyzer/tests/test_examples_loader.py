"""Tests for llm_utils.examples_loader module."""
import pytest
import tempfile
from pathlib import Path
from presidio_analyzer.llm_utils.examples_loader import (
    load_yaml_examples,
    convert_to_langextract_format,
)


class TestLoadYamlExamples:
    """Tests for load_yaml_examples function."""

    def test_when_examples_file_exists_then_loads_list(self):
        """Test loading examples from YAML file returns a list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
examples:
  - text: "John Doe works at Acme Corp"
    extractions:
      - extraction_class: "PERSON"
        extraction_text: "John Doe"
        attributes: {}
      
  - text: "Contact us at info@example.com"
    extractions:
      - extraction_class: "EMAIL_ADDRESS"
        extraction_text: "info@example.com"
        attributes: {}
""")
            examples_path = Path(f.name)

        try:
            # Use absolute path to load temp file
            examples = load_yaml_examples(str(examples_path))
            
            assert isinstance(examples, list)
            assert len(examples) == 2
            assert examples[0]["text"] == "John Doe works at Acme Corp"
            assert examples[1]["text"] == "Contact us at info@example.com"
        finally:
            examples_path.unlink()

    def test_when_examples_file_has_multiple_extractions_per_example_then_loads_all(self):
        """Test loading example with multiple extractions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
examples:
  - text: "John at john@example.com"
    extractions:
      - extraction_class: "PERSON"
        extraction_text: "John"
        attributes: {}
      - extraction_class: "EMAIL_ADDRESS"
        extraction_text: "john@example.com"
        attributes: {}
""")
            examples_path = Path(f.name)

        try:
            examples = load_yaml_examples(str(examples_path))
            
            assert len(examples) == 1
            assert len(examples[0]["extractions"]) == 2
        finally:
            examples_path.unlink()

    def test_when_examples_file_missing_then_raises_file_not_found_error(self):
        """Test that missing examples file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_yaml_examples("nonexistent_examples.yaml")

    def test_when_examples_missing_from_yaml_then_raises_value_error(self):
        """Test that YAML without 'examples' key raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
other_section:
  - text: "some text"
""")
            examples_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Examples file must contain 'examples'"):
                load_yaml_examples(str(examples_path))
        finally:
            examples_path.unlink()

    def test_when_loading_actual_langextract_examples_file_then_works(self):
        """Test loading the actual langextract examples file."""
        # Load the real examples file from conf directory using repo-root-relative path
        examples = load_yaml_examples(
            "presidio-analyzer/presidio_analyzer/conf/langextract_prompts/default_pii_phi_examples.yaml"
        )
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        # Each example should have text and extractions
        for example in examples:
            assert "text" in example
            assert "extractions" in example


class TestConvertToLangextractFormat:
    """Tests for convert_to_langextract_format function."""

    def test_when_examples_data_valid_then_converts_to_langextract_format(self):
        """Test converting examples to LangExtract ExampleData format."""
        examples_data = [
            {
                "text": "John Doe works here",
                "extractions": [
                    {
                        "extraction_class": "PERSON",
                        "extraction_text": "John Doe",
                        "attributes": {}
                    }
                ]
            }
        ]

        result = convert_to_langextract_format(examples_data)

        assert isinstance(result, list)
        assert len(result) == 1
        
        # Check it's a LangExtract ExampleData object
        example = result[0]
        assert hasattr(example, 'text')
        assert hasattr(example, 'extractions')
        assert example.text == "John Doe works here"
        assert len(example.extractions) == 1

    def test_when_multiple_examples_then_converts_all(self):
        """Test converting multiple examples."""
        examples_data = [
            {
                "text": "John Doe",
                "extractions": [
                    {"extraction_class": "PERSON", "extraction_text": "John Doe", "attributes": {}}
                ]
            },
            {
                "text": "info@example.com",
                "extractions": [
                    {"extraction_class": "EMAIL_ADDRESS", "extraction_text": "info@example.com", "attributes": {}}
                ]
            }
        ]

        result = convert_to_langextract_format(examples_data)

        assert len(result) == 2
        assert result[0].text == "John Doe"
        assert result[1].text == "info@example.com"

    def test_when_example_has_multiple_extractions_then_converts_all(self):
        """Test converting example with multiple extractions."""
        examples_data = [
            {
                "text": "John at john@example.com",
                "extractions": [
                    {"extraction_class": "PERSON", "extraction_text": "John", "attributes": {}},
                    {"extraction_class": "EMAIL_ADDRESS", "extraction_text": "john@example.com", "attributes": {}}
                ]
            }
        ]

        result = convert_to_langextract_format(examples_data)

        assert len(result) == 1
        assert len(result[0].extractions) == 2

    def test_when_extraction_has_all_fields_then_preserves_data(self):
        """Test that all extraction fields are preserved."""
        examples_data = [
            {
                "text": "Sample text",
                "extractions": [
                    {
                        "extraction_class": "PERSON",
                        "extraction_text": "Sample",
                        "attributes": {"type": "name"}
                    }
                ]
            }
        ]

        result = convert_to_langextract_format(examples_data)
        extraction = result[0].extractions[0]

        # Check the Extraction object has correct attributes
        assert hasattr(extraction, 'extraction_class')
        assert hasattr(extraction, 'extraction_text')
        assert hasattr(extraction, 'attributes')
        assert extraction.extraction_class == "PERSON"
        assert extraction.extraction_text == "Sample"
        assert extraction.attributes == {"type": "name"}

    def test_when_empty_examples_list_then_returns_empty_list(self):
        """Test converting empty examples list."""
        result = convert_to_langextract_format([])
        assert result == []

    def test_when_example_has_no_extractions_then_creates_empty_extractions(self):
        """Test example with empty extractions list."""
        examples_data = [
            {
                "text": "No entities here",
                "extractions": []
            }
        ]

        result = convert_to_langextract_format(examples_data)

        assert len(result) == 1
        assert result[0].text == "No entities here"
        assert len(result[0].extractions) == 0


class TestIntegration:
    """Integration tests for examples_loader functions."""

    def test_when_loading_and_converting_workflow_then_works(self):
        """Test complete workflow: load YAML → convert to LangExtract format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
examples:
  - text: "John Doe at john@example.com and Jane Smith"
    extractions:
      - extraction_class: "PERSON"
        extraction_text: "John Doe"
        attributes: {}
      - extraction_class: "EMAIL_ADDRESS"
        extraction_text: "john@example.com"
        attributes: {}
      - extraction_class: "PERSON"
        extraction_text: "Jane Smith"
        attributes: {}
""")
            examples_path = Path(f.name)

        try:
            # Step 1: Load YAML
            examples_data = load_yaml_examples(str(examples_path))
            assert len(examples_data) == 1
            assert len(examples_data[0]["extractions"]) == 3
            
            # Step 2: Convert to LangExtract format
            langextract_examples = convert_to_langextract_format(examples_data)
            assert len(langextract_examples) == 1
            assert len(langextract_examples[0].extractions) == 3
            
            # Verify entity types
            entity_types = [e.extraction_class for e in langextract_examples[0].extractions]
            assert "PERSON" in entity_types
            assert "EMAIL_ADDRESS" in entity_types
            assert entity_types.count("PERSON") == 2
            
        finally:
            examples_path.unlink()

    def test_when_using_actual_langextract_examples_then_converts_correctly(self):
        """Test loading and converting the actual langextract examples file."""
        # Load the real examples file using repo-root-relative path
        examples_data = load_yaml_examples(
            "presidio-analyzer/presidio_analyzer/conf/langextract_prompts/default_pii_phi_examples.yaml"
        )
        
        # Convert to LangExtract format
        langextract_examples = convert_to_langextract_format(examples_data)
        
        assert isinstance(langextract_examples, list)
        assert len(langextract_examples) > 0
        
        # Verify structure
        for example in langextract_examples:
            assert hasattr(example, 'text')
            assert hasattr(example, 'extractions')
            assert isinstance(example.text, str)
            assert isinstance(example.extractions, list)
