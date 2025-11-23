"""Examples loading utilities for LLM recognizers."""
import logging
from pathlib import Path
from typing import Dict, List

import yaml

logger = logging.getLogger("presidio-analyzer")


def load_yaml_examples(
    examples_file: str, conf_subdir: str = "conf"
) -> List[Dict]:
    """Load examples from YAML file.

    :param examples_file: Relative path to examples file within conf directory.
    :param conf_subdir: Subdirectory name (default: "conf").
    :return: List of example dictionaries.
    :raises FileNotFoundError: If examples file doesn't exist.
    :raises ValueError: If YAML parsing fails or examples format is invalid.
    """
    examples_path = Path(__file__).parent.parent / conf_subdir / examples_file
    if not examples_path.exists():
        raise FileNotFoundError(f"Examples file not found: {examples_path}")

    try:
        with open(examples_path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse examples YAML: {e}")

    examples_data = data.get("examples", [])
    if not examples_data:
        raise ValueError("Examples file must contain 'examples' list")

    return examples_data


def convert_to_langextract_format(examples_data: List[Dict]) -> List:
    """Convert YAML examples to LangExtract objects.

    :param examples_data: List of example dictionaries from YAML.
    :return: List of LangExtract ExampleData objects.
    :raises ImportError: If langextract is not installed.
    """
    try:
        import langextract as lx
    except ImportError:
        raise ImportError(
            "LangExtract is not installed. "
            "Install it with: pip install presidio-analyzer[langextract]"
        )

    langextract_examples = []
    for example in examples_data:
        extractions = [
            lx.data.Extraction(
                extraction_class=ext["extraction_class"],
                extraction_text=ext["extraction_text"],
                attributes=ext.get("attributes", {}),
            )
            for ext in example.get("extractions", [])
        ]

        langextract_examples.append(
            lx.data.ExampleData(text=example["text"], extractions=extractions)
        )

    return langextract_examples
