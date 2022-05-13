from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from pprint import pprint
import json

text_to_anonymize = "His name is Tom and his phone number is 212-555-5555"

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

analyzer_results = analyzer.analyze(text=text_to_anonymize, language="en")
print("PII Detection:")
print(analyzer_results)


anonymized_results = anonymizer.anonymize(
    text=text_to_anonymize,
    analyzer_results=analyzer_results,
    operators={"DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"})},
)
print("\nPII Anonymization:")
pprint(json.loads(anonymized_results.to_json()))
