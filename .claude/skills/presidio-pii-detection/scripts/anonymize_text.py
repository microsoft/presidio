#!/usr/bin/env python3
"""
Anonymize PII in text using Presidio.

Usage:
    python anonymize_text.py "My SSN is 123-45-6789"
    python anonymize_text.py --file input.txt --output output.txt
    python anonymize_text.py --operator redact "John's email is john@example.com"
"""

import argparse
import json
import sys
from typing import Optional


def anonymize_text(
    text: str,
    operator: str = "replace",
    entities: Optional[list] = None,
    language: str = "en",
    operator_params: Optional[dict] = None
):
    """Anonymize PII in text."""
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        from presidio_anonymizer.entities import OperatorConfig

        # Analyze
        analyzer = AnalyzerEngine()
        results = analyzer.analyze(
            text=text,
            entities=entities,
            language=language
        )

        if not results:
            return {
                "original_text": text,
                "anonymized_text": text,
                "entities_found": 0,
                "message": "No PII detected"
            }

        # Anonymize
        anonymizer = AnonymizerEngine()

        # Build operator config
        if operator_params:
            operator_config = OperatorConfig(operator, operator_params)
        else:
            operator_config = OperatorConfig(operator, {})

        # Apply same operator to all entities
        operators = {r.entity_type: operator_config for r in results}

        anonymized = anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )

        return {
            "original_text": text,
            "anonymized_text": anonymized.text,
            "entities_found": len(results),
            "operator": operator,
            "entities": [
                {
                    "entity_type": r.entity_type,
                    "start": r.start,
                    "end": r.end,
                    "original_text": text[r.start:r.end]
                }
                for r in results
            ]
        }

    except ImportError as e:
        return {
            "error": f"Missing package: {e}. Install with: pip install presidio-analyzer presidio-anonymizer"
        }
    except Exception as e:
        return {
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Anonymize PII in text")
    parser.add_argument("text", nargs="?", help="Text to anonymize")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--output", "-o", help="Output file for anonymized text")
    parser.add_argument("--operator", default="replace",
                       choices=["replace", "redact", "hash", "mask", "encrypt"],
                       help="Anonymization operator (default: replace)")
    parser.add_argument("--entities", "-e", nargs="+", help="Specific entities to anonymize")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Get text
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        sys.exit(1)

    # Anonymize
    result = anonymize_text(
        text=text,
        operator=args.operator,
        entities=args.entities,
        language=args.language
    )

    # Check for errors
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.json:
                f.write(json.dumps(result, indent=2))
            else:
                f.write(result['anonymized_text'])
        print(f"Anonymized text written to {args.output}")
    else:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result['anonymized_text'])


if __name__ == "__main__":
    main()
