from collections import defaultdict
import logging
from presidio_anonymizer import OperatorResult
import requests
from timeit import default_timer as timer
from typing import List, Tuple

from services.presidio.presidio_service import PresidioService
from config.config import config

logger = logging.getLogger(__name__)


class HttpPresidioService(PresidioService):
    """ Presidio Service class that uses both Presidio Analyzer and Anonymizer via HTTP """

    def __init__(self):
        self.analyzer_base_url = config.Presidio.analyzer_url
        self.anonymizer_base_url = config.Presidio.anonymizer_url        

    def anonymize_text(self, session_id: str, text: str, language: str, entity_mappings: dict) -> Tuple[str, dict] :
        """ Anonymize the given text using Presidio Analyzer and Anonymizer engines """

        logger.info(f"Anonymize text called with session_id: {session_id}")
        start_time = timer()

        try:
            analyze_url = f"{self.analyzer_base_url}/analyze"
            analyze_payload = {
                "text": text,
                "language": language
            }
            analyze_response = requests.post(analyze_url, json=analyze_payload)
            analyzer_result = analyze_response.json()
            logger.info(f"Analyze took {timer() - start_time:.3f} seconds for session_id: {session_id}")

            analyzer_result_with_id, entities = self.add_id_to_analyzer_result(text, analyzer_result, entity_mappings)
        
            anonymizer_start_time = timer()
            anonymize_url = f"{self.anonymizer_base_url}/anonymize"
            anonymize_payload = {
                "text": text,
                "analyzer_results": analyzer_result_with_id
            }
            anonymize_response = requests.post(anonymize_url, json=anonymize_payload)
            anonymizer_result = anonymize_response.json()            
            logger.info(f"Anonymize took {timer() - anonymizer_start_time:.3f} seconds for session_id: {session_id}")

            anonymizer_text = anonymizer_result["text"]
            anonymizer_results = anonymizer_result["items"]
            new_entity_mappings = self.build_entity_mappgings(entity_mappings, entities, anonymizer_results)

            total_time = timer() - start_time
            logger.info(f"Total processing time: {total_time:.3f} seconds for session_id: {session_id}")            

            return anonymizer_text, new_entity_mappings
        except Exception as e:
            logger.exception(f"Error in anonymize_text for session_id {session_id}")
            raise

    def deanonymize_text(self, session_id: str, text: str, entity_mappings: dict) -> str:
        """ Deanonymize the given text using Presidio Analyzer and Anonymizer engines """

        logger.info(f"Deanonymize text called with session_id: {session_id}")
        start_time = timer()

        deanonymized_text = text
        try:
            for _, entities in entity_mappings.items():
                for entity_value, entity_id in entities.items():
                    deanonymized_text = deanonymized_text.replace(entity_id, entity_value)

            total_time = timer() - start_time
            logger.info(f"Total processing time: {total_time:.3f} seconds for session_id: {session_id}")
            
            return deanonymized_text
        except Exception as e:
            logger.exception(f"Error in deanonymize_text for session_id {session_id}")
            raise

    def build_entity_mappgings(self, entity_mappings: dict, entities: dict, anonymizer_results: List) -> dict:
        """ Build the entity mappings based on the previous mappings and the anonymizer results """

        new_entity_mappings = entity_mappings.copy() if entity_mappings is not None else dict()

        for entity in anonymizer_results:
            entity_text = entity["text"]
            entity_id = entity_text.strip('<>')
            entity_type = entity_id.rsplit('_', 1)[0]
            entity_value = entities[entity_id]

            if entity_type not in new_entity_mappings:
                new_entity_mappings[entity_type] = {}

            new_entity_mappings[entity_type][entity_value] = entity_text

        return new_entity_mappings
    
    def add_id_to_analyzer_result(self, text: str, analyzer_result: List[OperatorResult], entity_mappings: dict) -> Tuple[List[OperatorResult], dict]:
        """ Add an ID to each entity type in the analyzer_result based on the entity_mappings """

        entity_type_counts = {}
        processed_entities = {}
        new_entity_mappings = entity_mappings.copy() if entity_mappings is not None else dict()

        # Initialize counts from the mapping
        for entity_type, entities in new_entity_mappings.items():
            # Extract indices from the IDs in the mapping
            indices = [
                int(id.strip('<>').split('_')[-1]) for id in entities.values()
                if id.strip('<>').startswith(entity_type)
            ]
            entity_type_counts[entity_type] = max(indices) + 1 if indices else 0

        # Now process each item in analyzer_result
        for item in analyzer_result:
            entity_type = item['entity_type']
            start = item['start']
            end = item['end']
            entity_text = text[start:end]

            if entity_type not in entity_type_counts:
                entity_type_counts[entity_type] = 0

            if entity_type not in new_entity_mappings:
                new_entity_mappings[entity_type] = {}

            if entity_text in new_entity_mappings[entity_type]:
                # Reuse the existing ID from entity_mappings (strip angle brackets)
                entity_id = new_entity_mappings[entity_type][entity_text].strip('<>')
            else:
                # Assign a new ID
                count = entity_type_counts[entity_type]
                entity_id = f"{entity_type}_{count}"
                new_entity_mappings[entity_type][entity_text] = f"<{entity_id}>"
                entity_type_counts[entity_type] = count + 1

            # Update the entity_type in the item
            item['entity_type'] = entity_id
            processed_entities[entity_id] = entity_text

        return analyzer_result, processed_entities
    