from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerConfig
from faker import Faker
from faker.providers import internet

def reverse_string(x):
  return x[::-1]

def anonymize_reverse_lambda(text_to_anonymize): 
    analyzer_results = analyzer.analyze(text=text_to_anonymize, entities=["EMAIL_ADDRESS"], language='en')

    print(analyzer_results)    

    anonymized_results = anonymizer.anonymize(
        text=text_to_anonymize,
        analyzer_results=analyzer_results,            
        anonymizers_config={"EMAIL_ADDRESS": AnonymizerConfig("custom", {"new_value": lambda x: reverse_string(x)})}        
    )

    return anonymized_results

def anonymize_faker_lambda(text_to_anonymize): 
    analyzer_results = analyzer.analyze(text=text_to_anonymize, entities=["EMAIL_ADDRESS"], language='en')

    print(analyzer_results)    

    anonymized_results = anonymizer.anonymize(
        text=text_to_anonymize,
        analyzer_results=analyzer_results,    
        anonymizers_config={"EMAIL_ADDRESS": AnonymizerConfig("custom", {"new_value": lambda x: fake.safe_email()})}
    )

    return anonymized_results

fake = Faker('en_US')
fake.add_provider(internet)

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = 'The user has the following two emails: email1@gmail.com and email2@gmail.com'
print("Reverse lambda result: " + anonymize_reverse_lambda(text).text + "\n")
print("Faker lambda result" + anonymize_faker_lambda(text).text + "\n")