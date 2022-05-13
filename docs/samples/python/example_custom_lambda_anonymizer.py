from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
from faker.providers import internet


def reverse_string(x):
    """Return string in reverse order."""
    return x[::-1]


def anonymize_reverse_lambda(analyzer_results, text_to_anonymize):
    """Anonymize using an example lambda."""
    anonymized_results = anonymizer.anonymize(
        text=text_to_anonymize,
        analyzer_results=analyzer_results,
        operators={
            "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: x[::-1]})
        },
    )

    return anonymized_results


def anonymize_faker_lambda(analyzer_results, text_to_anonymize):
    """Anonymize using a faker provider."""

    anonymized_results = anonymizer.anonymize(
        text=text_to_anonymize,
        analyzer_results=analyzer_results,
        operators={
            "EMAIL_ADDRESS": OperatorConfig(
                "custom", {"lambda": lambda x: fake.safe_email()}
            )
        },
    )

    return anonymized_results


if __name__ == "__main__":
    fake = Faker("en_US")
    fake.add_provider(internet)

    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    text = "The user has the following two emails: email1@contoso.com and email2@contoso.com"  # noqa E501
    analyzer_results = analyzer.analyze(
        text=text, entities=["EMAIL_ADDRESS"], language="en"
    )
    print(f"Original Text: {text}")
    print(f"Analyzer result: {analyzer_results}\n")

    print(
        f"Reverse lambda result: {anonymize_reverse_lambda(analyzer_results, text).text}"  # noqa E501
    )
    print(f"Faker lambda result: {anonymize_faker_lambda(analyzer_results, text).text}")
