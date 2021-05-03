from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities.engine.operator_config import OperatorConfig
from faker import Faker
from faker.providers import internet

def reverse_string(x):
  return x[::-1]

def anonymize_reverse_lambda(analyzer_results, text_to_anonymize):         
    anonymized_results = anonymizer.anonymize(
        text=text_to_anonymize,
        analyzer_results=analyzer_results,            
        operators={"EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: x[::-1]})}        
    )

    return anonymized_results

def anonymize_faker_lambda(analyzer_results, text_to_anonymize):      
    anonymized_results = anonymizer.anonymize(
        text=text_to_anonymize,
        analyzer_results=analyzer_results,    
        operators={"EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: fake.safe_email()})}
    )

    return anonymized_results

fake = Faker('en_US')
fake.add_provider(internet)

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = 'The user has the following two emails: email1@contoso.com and email2@contoso.com'
analyzer_results = analyzer.analyze(text=text, entities=["EMAIL_ADDRESS"], language='en')
print("Origina Text: ", text)
print("Analyzer result:", analyzer_results, '\n')

print("Reverse lambda result: ",anonymize_reverse_lambda(analyzer_results, text).text, '\n')
print("Faker lambda result: ",anonymize_faker_lambda(analyzer_results, text).text, '\n')