import uuid
import re
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

# {
#     'ID1': {
#         'PERSON': {
#             'PERSON_1': 'Alex',
#             'PERSON_2': 'Chus'
#         }
#     }
# }
cached_entities = {}

def cache_entities(session_id, text, analyzer_results):
  """
  Cache entities by session id and type for de-anonymization.
  Return a list with the ids of the entities that were cached.
  """
  numered_entities = []
  for entity in analyzer_results:
    if session_id not in cached_entities:
      cached_entities[session_id] = {}

    entity_type = entity.entity_type
    if entity_type not in cached_entities[session_id]:
      cached_entities[session_id][entity_type] = {}
    
    entity_type_dic = cached_entities[session_id][entity_type]
    entity_name = f"{entity_type}_{len(entity_type_dic) + 1}"
    entity_type_dic[entity_name] = text[entity.start:entity.end]
    numered_entities.append(entity_name)

  return numered_entities

def replace_entities_with_numered_entities(numered_entities, anonymizer_results):
  """
  Replace anonymized entities with numbered entities.
  """
  anonymizer_text = anonymizer_results.text
  for item in anonymizer_results.items:
    entity_name = numered_entities.pop()
    anonymizer_text = anonymizer_text[:item.start] + "<" + entity_name + ">" + anonymizer_text[item.end:]

  return anonymizer_text

def anonymize(text, language, session_id=None):
  """
  Anonymize text in the selected language.
  """
  if session_id is None:
    session_id = str(uuid.uuid4())

  # Create configuration containing engine name and models
  configuration = {
      "nlp_engine_name": "spacy",
      "models": [
          {"lang_code": "es", "model_name": "es_core_news_md"},
          {"lang_code": "en", "model_name": "en_core_web_lg"},
      ],
  }

  # Create NLP engine based on configuration
  provider = NlpEngineProvider(nlp_configuration=configuration)
  nlp_engine = provider.create_engine()

  # Pass the created NLP engine and supported languages to the analyzer engine
  analyzer = AnalyzerEngine(
      nlp_engine=nlp_engine, supported_languages=["en", "es"]
  )

  # Analyze in selected language
  analyzer_results = analyzer.analyze(text=text, language=language)
  
  # Cache entities for de-anonymization
  numered_entities = cache_entities(
     session_id=session_id, text=text, analyzer_results=analyzer_results
  )

  # Analyzer results are passed to the anonymizer engine for anonymization
  anonymizer = AnonymizerEngine()

  anonymized_text = anonymizer.anonymize(
    text=text,analyzer_results=analyzer_results
  )

  # Replace entities with numered entities in anonymized text
  return {
    "session_id": session_id,
    "text": replace_entities_with_numered_entities(
      numered_entities, anonymized_text),
  }

def find_anonymized_entities(text):
    """
    Find all substrings that start and end with <> along with their
    start and end indexes.
    """
    pattern = re.compile(r'<([^>]+)>')
    matches = pattern.finditer(text)
    
    results = []
    for match in matches:
        start, end = match.span()
        substring = match.group(1)
        results.insert(0, (substring, start, end))
    
    return results

def find_original_entity(session_id, entity):
    """
    Find the original entity given the anonymized entity.
    """
    if session_id in cached_entities:
      for entity_type in cached_entities[session_id]:
          if entity in cached_entities[session_id][entity_type]:
              return cached_entities[session_id][entity_type][entity]
    return None

def deanonymize(session_id, text):
  """
  Deanonymize text using the cached entities.
  """
  anonymized_entities = find_anonymized_entities(text)
  for entity, start, end in anonymized_entities:
    original_entity = find_original_entity(session_id, entity)
    if original_entity:
      text = text[:start] + original_entity + text[end:]

  return text



# Test the anonymization and de-anonymization in Spanish
text_es = "Mi nombre es Alex y el tuyo Chus"
results_es = anonymize(text=text_es, language="es")
print(f"SPANISH: '{text_es}' -> '{results_es['text']}'")

new_text_es = "O sea que tu nombre es <PERSON_2>. <PERSON_2>, ¿verdad?"
deanonymized_results_es = deanonymize(results_es["session_id"], new_text_es)
print(f"SPANISH DEANONYMIZED: '{new_text_es}' -> '{deanonymized_results_es}'")

# Test the anonymization and de-anonymization in English
session_id = "ID1"
text_en = "My name is Alex and my phone numbers are +34 666 123 456 and +41 77 123 4567"
results_en = anonymize(text=text_en, language="en", session_id=session_id)
print(f"ENGLISH (part 1): '{text_en}' -> '{results_en['text']}'")

text_en = "Your name is Chus and your phone number is +41 55 666 7777"
results_en = anonymize(text=text_en, language="en", session_id=session_id)
print(f"ENGLISH  (part 2): '{text_en}' -> '{results_en['text']}'")

new_text_en = "So my name is <PERSON_1> and your Swiss phone is <PHONE_NUMBER_3>"
deanonymized_results_en = deanonymize(session_id, new_text_en)
print(f"ENGLISH DEANONYMIZED: '{new_text_en}' -> '{deanonymized_results_en}'")
