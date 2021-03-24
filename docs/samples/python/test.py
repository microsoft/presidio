from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerConfig
from faker import Faker
from faker.providers import internet
import random
import string



def anonymizeEmail(text_to_anonymize): 
    analyzer_results = analyzer.analyze(text=text_to_anonymize, entities=["EMAIL_ADDRESS"], language='en')

    allowed_chars = string.ascii_letters + string.punctuation

    anonymized_results = anonymizer.anonymize(
        text=text_to_anonymize,
        analyzer_results=analyzer_results,    
        #anonymizers_config={"EMAIL_ADDRESS": AnonymizerConfig("custom", {"new_value": lambda x: fake.safe_email()})}
        anonymizers_config={"EMAIL_ADDRESS": AnonymizerConfig("custom_replace", {"new_value": lambda x: random.choice(allowed_chars)})}
    )

    return anonymized_results

fake = Faker('en_US')
fake.add_provider(internet)

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = 'The user has the following two emails: email1@gmail.com and email2@gmail.com'
print(anonymizeEmail(text).text)