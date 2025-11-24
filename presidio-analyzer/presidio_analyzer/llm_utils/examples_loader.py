"""Examples loading utilities for LLM recognizers."""
import logging
from typing import Dict, List

from .config_loader import get_conf_path, load_yaml_file, validate_config_fields
from .langextract_helper import check_langextract_available, lx

logger = logging.getLogger("presidio-analyzer")


def load_yaml_examples(
    examples_file: str, conf_subdir: str = "conf"
) -> List[Dict]:
    """Load examples from YAML file."""
    filepath = get_conf_path(examples_file, conf_subdir)
    data = load_yaml_file(filepath)
    validate_config_fields(data, ["examples"], "Examples file")
    return data["examples"]


def convert_to_langextract_format(examples_data: List[Dict]) -> List:
    """Convert examples to LangExtract format."""
    check_langextract_available()

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
