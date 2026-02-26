"""Example usage of the Pseudonymize operator for realistic data anonymization.

This example demonstrates how to use the Pseudonymize operator with
the Presidio Anonymizer to generate realistic fake data using the Faker library.
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Initialize engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Sample text with PII
text = """
John Doe works at ABC Corporation. His email is john.doe@example.com
and his phone number is 555-123-4567. He lives in New York.
You can also reach Jane Smith at jane.smith@example.com or call her at 555-987-6543.
"""

print("Original Text:")
print(text)
print("\n" + "="*80 + "\n")

# Analyze text for PII
analyzer_results = analyzer.analyze(text=text, language="en")
print(f"Found {len(analyzer_results)} PII entities:")
for result in analyzer_results:
    print(f"  - {result.entity_type}: '{text[result.start:result.end]}' (score: {result.score:.2f})")
print("\n" + "="*80 + "\n")

# Example 1: Basic pseudonymization
print("Example 1: Basic Pseudonymization")
print("-" * 80)

result1 = anonymizer.anonymize(
    text=text,
    analyzer_results=analyzer_results,
    operators={
        "PERSON": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "EMAIL_ADDRESS": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "PHONE_NUMBER": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "LOCATION": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "ORGANIZATION": OperatorConfig("pseudonymize", {"locale": "en_US"}),
    }
)

print(result1.text)
print("\n" + "="*80 + "\n")

# Example 2: Consistent pseudonymization (same input = same output)
print("Example 2: Consistent Pseudonymization")
print("-" * 80)
print("Notice how 'John Doe' and 'jane.smith@example.com' get the same replacement each time")

result2 = anonymizer.anonymize(
    text=text,
    analyzer_results=analyzer_results,
    operators={
        "PERSON": OperatorConfig("pseudonymize", {
            "locale": "en_US",
            "consistent": True,
            "seed": 42
        }),
        "EMAIL_ADDRESS": OperatorConfig("pseudonymize", {
            "locale": "en_US",
            "consistent": True,
            "seed": 42
        }),
        "PHONE_NUMBER": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "LOCATION": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "ORGANIZATION": OperatorConfig("pseudonymize", {"locale": "en_US"}),
    }
)

print(result2.text)
print("\n" + "="*80 + "\n")

# Example 3: Korean locale (generates Korean-style names for English text)
print("Example 3: Korean Locale Pseudonymization")
print("-" * 80)
print("Using Korean locale to generate Korean-style fake names")

# Analyze the English text
korean_style_results = analyzer.analyze(text=text, language="en")

result3 = anonymizer.anonymize(
    text=text,
    analyzer_results=korean_style_results,
    operators={
        "PERSON": OperatorConfig("pseudonymize", {"locale": "ko_KR"}),
        "EMAIL_ADDRESS": OperatorConfig("pseudonymize", {"locale": "ko_KR"}),
        "PHONE_NUMBER": OperatorConfig("pseudonymize", {"locale": "ko_KR"}),
        "LOCATION": OperatorConfig("pseudonymize", {"locale": "ko_KR"}),
        "ORGANIZATION": OperatorConfig("pseudonymize", {"locale": "ko_KR"}),
    }
)

print(f"Original text with English PII:")
print(text[:80] + "...")
print(f"\nAnonymized with Korean-style names:")
print(result3.text)
print("\n" + "="*80 + "\n")

# Example 4: Mixed operators (pseudonymize + mask)
print("Example 4: Mixed Operators (Pseudonymize + Mask)")
print("-" * 80)

result4 = anonymizer.anonymize(
    text=text,
    analyzer_results=analyzer_results,
    operators={
        "PERSON": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "EMAIL_ADDRESS": OperatorConfig("mask", {
            "masking_char": "*",
            "chars_to_mask": 10,
            "from_end": False
        }),
        "PHONE_NUMBER": OperatorConfig("pseudonymize", {"locale": "en_US"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "<CITY>"}),
        "ORGANIZATION": OperatorConfig("pseudonymize", {"locale": "en_US"}),
    }
)

print(result4.text)
print("\n" + "="*80 + "\n")

# Example 5: Reproducible results with seed
print("Example 5: Reproducible Results with Seed")
print("-" * 80)

seed_value = 12345

result5a = anonymizer.anonymize(
    text=text,
    analyzer_results=analyzer_results,
    operators={
        "DEFAULT": OperatorConfig("pseudonymize", {
            "locale": "en_US",
            "seed": seed_value
        })
    }
)

# Create a new anonymizer instance to demonstrate reproducibility
anonymizer2 = AnonymizerEngine()
result5b = anonymizer2.anonymize(
    text=text,
    analyzer_results=analyzer_results,
    operators={
        "DEFAULT": OperatorConfig("pseudonymize", {
            "locale": "en_US",
            "seed": seed_value
        })
    }
)

print("First run:")
print(result5a.text)
print("\nSecond run (should be identical):")
print(result5b.text)
print(f"\nResults are identical: {result5a.text == result5b.text}")
