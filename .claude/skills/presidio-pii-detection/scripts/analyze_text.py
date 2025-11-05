#!/usr/bin/env python3
"""
Analyze text for PII entities using Presidio Analyzer.

Usage:
    python analyze_text.py "Text to analyze"
    python analyze_text.py --file input.txt
    python analyze_text.py --entities PHONE_NUMBER EMAIL_ADDRESS "My phone is 555-1234"
"""

import argparse
import json
import sys
from typing import List, Optional


def analyze_text(
    text: str,
    entities: Optional[List[str]] = None,
    language: str = "en",
    score_threshold: float = 0.5
):
    """Analyze text for PII entities."""
    try:
        from presidio_analyzer import AnalyzerEngine

        analyzer = AnalyzerEngine()
        results = analyzer.analyze(
            text=text,
            entities=entities,
            language=language,
            score_threshold=score_threshold
        )

        # Format results as JSON
        results_json = [
            {
                "entity_type": r.entity_type,
                "start": r.start,
                "end": r.end,
                "score": r.score,
                "text": text[r.start:r.end]
            }
            for r in results
        ]

        return {
            "text": text,
            "language": language,
            "entities_found": len(results_json),
            "results": results_json
        }

    except ImportError:
        return {
            "error": "presidio-analyzer not installed. Run: pip install presidio-analyzer"
        }
    except Exception as e:
        return {
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Analyze text for PII entities")
    parser.add_argument("text", nargs="?", help="Text to analyze")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--entities", "-e", nargs="+", help="Specific entities to detect")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--threshold", "-t", type=float, default=0.5, help="Score threshold (default: 0.5)")
    parser.add_argument("--output", "-o", help="Output file for results")

    args = parser.parse_args()

    # Get text from argument or file
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

    # Analyze
    results = analyze_text(
        text=text,
        entities=args.entities,
        language=args.language,
        score_threshold=args.threshold
    )

    # Output
    output_json = json.dumps(results, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Results written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
