"""Prompt loading and rendering utilities for LLM recognizers."""
import logging
from pathlib import Path

logger = logging.getLogger("presidio-analyzer")

__all__ = [
    "load_file_from_conf",
    "load_prompt_file",
    "render_jinja_template",
]


def load_file_from_conf(filename: str, conf_subdir: str = "conf") -> str:
    """Load text file from configuration directory.

    :param filename: Name of file to load.
    :param conf_subdir: Configuration subdirectory (default: "conf").
    :return: File contents as string.
    :raises FileNotFoundError: If file doesn't exist.
    """
    file_path = Path(__file__).parent.parent / conf_subdir / filename
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r") as f:
        return f.read()


def load_prompt_file(prompt_file: str, conf_subdir: str = "conf") -> str:
    """Load prompt template file from configuration directory.

    :param prompt_file: Name of prompt template file.
    :param conf_subdir: Configuration subdirectory (default: "conf").
    :return: Prompt template contents as string.
    :raises FileNotFoundError: If file doesn't exist.
    """
    return load_file_from_conf(prompt_file, conf_subdir)


def render_jinja_template(template_str: str, **kwargs) -> str:
    """Render Jinja2 template with provided variables.

    :param template_str: Jinja2 template string.
    :param kwargs: Variables to pass to template rendering.
    :return: Rendered template as string.
    :raises ImportError: If Jinja2 is not installed.
    """
    try:
        from jinja2 import Template
    except ImportError:
        raise ImportError(
            "Jinja2 is not installed. "
            "Install it with: poetry install --extras langextract"
        )

    template = Template(template_str)
    return template.render(**kwargs)
