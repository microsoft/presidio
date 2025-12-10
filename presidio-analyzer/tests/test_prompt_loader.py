"""Tests for llm_utils.prompt_loader module."""
import pytest
from pathlib import Path
from presidio_analyzer.llm_utils.prompt_loader import (
    load_prompt_file,
    render_jinja_template,
)


class TestLoadPromptFile:
    """Tests for load_prompt_file function."""

    def test_when_prompt_file_exists_then_loads_content(self):
        """Test loading an existing prompt template file from conf directory."""
        # Load the actual langextract prompt file using repo-root-relative path
        result = load_prompt_file(
            "presidio-analyzer/presidio_analyzer/conf/langextract_prompts/default_pii_phi_prompt.j2"
        )

        assert result is not None
        assert len(result) > 0
        assert "ENTITY TYPES TO EXTRACT" in result
        assert "Extract personally identifiable information" in result

    def test_when_prompt_file_missing_then_raises_file_not_found_error(self):
        """Test that missing prompt file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_prompt_file("nonexistent_prompt.jinja2")


class TestRenderJinjaTemplate:
    """Tests for render_jinja_template function."""

    def test_when_template_has_variables_then_renders_correctly(self):
        """Test rendering a template with variables."""
        template = "Hello {{ name }}, your score is {{ score }}"
        result = render_jinja_template(template, name="Alice", score=95)

        assert result == "Hello Alice, your score is 95"

    def test_when_template_has_list_iteration_then_renders_correctly(self):
        """Test rendering a template with for loop."""
        template = """Entities:
{% for entity in entities %}
- {{ entity }}
{% endfor %}"""
        result = render_jinja_template(template, entities=["PERSON", "EMAIL", "PHONE"])

        assert "- PERSON" in result
        assert "- EMAIL" in result
        assert "- PHONE" in result

    def test_when_template_has_conditionals_then_renders_correctly(self):
        """Test rendering a template with if/else conditions."""
        template = """{% if enabled %}Feature is ON{% else %}Feature is OFF{% endif %}"""

        result_enabled = render_jinja_template(template, enabled=True)
        assert result_enabled.strip() == "Feature is ON"

        result_disabled = render_jinja_template(template, enabled=False)
        assert result_disabled.strip() == "Feature is OFF"

    def test_when_template_has_no_variables_then_returns_original(self):
        """Test rendering a static template without variables."""
        template = "This is a static prompt with no variables"
        result = render_jinja_template(template)

        assert result == template

    def test_when_template_has_complex_expressions_then_renders_correctly(self):
        """Test rendering with complex Jinja2 expressions."""
        template = """Total: {{ items | length }}
{% for item in items %}
{{ loop.index }}. {{ item.name }}: {{ item.value }}
{% endfor %}"""
        items = [
            {"name": "Item1", "value": 10},
            {"name": "Item2", "value": 20}
        ]
        result = render_jinja_template(template, items=items)

        assert "Total: 2" in result
        assert "1. Item1: 10" in result
        assert "2. Item2: 20" in result

    def test_when_template_has_filters_then_applies_correctly(self):
        """Test rendering with Jinja2 filters."""
        template = "{{ text | upper }} and {{ number | int }}"
        result = render_jinja_template(template, text="hello", number="42")

        assert "HELLO" in result
        assert "42" in result

    def test_when_missing_required_variable_then_renders_empty(self):
        """Test that missing variables render as empty strings (Jinja2 default)."""
        template = "Hello {{ undefined_var }}"
        result = render_jinja_template(template)

        # Jinja2 renders undefined variables as empty strings by default
        assert result == "Hello "

    def test_when_template_has_whitespace_control_then_handles_correctly(self):
        """Test Jinja2 whitespace control with {%- and -%}."""
        template = """ENTITIES:
{%- for entity in entities %}
- {{ entity }}
{%- endfor %}
END"""
        result = render_jinja_template(template, entities=["PERSON", "EMAIL"])

        assert "ENTITIES:" in result
        assert "- PERSON" in result
        assert "- EMAIL" in result
        assert "END" in result

    def test_when_rendering_actual_langextract_template_then_works(self):
        """Test rendering the actual LangExtract prompt template."""
        # Load the actual template using repo-root-relative path
        template = load_prompt_file(
            "presidio-analyzer/presidio_analyzer/conf/langextract_prompts/default_pii_phi_prompt.j2"
        )
        
        # Render with typical parameters
        result = render_jinja_template(
            template,
            supported_entities=["PERSON", "EMAIL_ADDRESS"],
            enable_generic_consolidation=True,
            labels_to_ignore=["metadata"]
        )

        assert "PERSON" in result
        assert "EMAIL_ADDRESS" in result
        # Check for consolidation entity if enabled
        assert len(result) > 0
