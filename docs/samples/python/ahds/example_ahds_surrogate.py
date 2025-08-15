"""Example usage of AHDS Surrogate operator using surrogate_ahds operation."""

import os

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, RecognizerResult


def main():
    """Use AHDS Surrogate operator with surrogate_ahds operation."""

    # Check if AHDS endpoint is available
    if not os.getenv("AHDS_ENDPOINT"):
        print("AHDS_ENDPOINT environment variable is not set.")
        print("Please set it to your Azure Health Data Services endpoint.")
        return

    try:
        # Initialize the anonymizer engine
        engine = AnonymizerEngine()

        # Example text with PII
        text = "Patient John Doe was seen by Dr. Smith on 2024-01-15"

        # Example analyzer results (normally these would come from the analyzer)
        analyzer_results = [
            RecognizerResult(entity_type="PATIENT", start=8, end=16, score=0.9),
            RecognizerResult(entity_type="DOCTOR", start=29, end=38, score=0.9),
            RecognizerResult(entity_type="DATE", start=42, end=52, score=0.9),
        ]

        # Use AHDS Surrogate operator
        result = engine.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={
                "DEFAULT": OperatorConfig(
                    "surrogate_ahds",
                    {
                        "entities": analyzer_results,
                        "input_locale": "en-US",
                        "surrogate_locale": "en-US"
                    }
                )
            },
        )

        print(f"Original text: {text}")
        print(f"Anonymized text: {result.text}")
        print(
            "Note: Uses Azure Health Data Services "
            "De-identification service surrogate_ahds operation "
            "for realistic surrogate generation"
        )

    except ImportError:
        print("AHDS dependencies are not available.")
        print("Please install with: pip install presidio-anonymizer[ahds]")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
