"""Prompt loading and rendering utilities for LLM recognizers."""
import logging
from pathlib import Path

logger = logging.getLogger("presidio-analyzer")


def load_prompt_file(prompt_file: str, conf_subdir: str = "conf") -> str:
    """Load prompt template file from configuration directory.

    :param prompt_file: Relative path to prompt file within conf directory.
    :param conf_subdir: Subdirectory name (default: "conf").
    :return: Contents of the prompt file.
    :raises FileNotFoundError: If prompt file doesn't exist.
    """
    prompt_path = Path(__file__).parent.parent / conf_subdir / prompt_file
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, "r") as f:
        return f.read()


def render_jinja_template(template_str: str, **kwargs) -> str:
    """Render Jinja2 template with provided variables.

    :param template_str: Jinja2 template string.
    :param kwargs: Variables to render in the template.
    :return: Rendered template string.
    :raises ImportError: If Jinja2 is not installed.
    """
    try:
        from jinja2 import Template
    except ImportError:
        raise ImportError(
            "Jinja2 is not installed. Install it with: pip install jinja2"
        )

    template = Template(template_str)
    return template.render(**kwargs)
