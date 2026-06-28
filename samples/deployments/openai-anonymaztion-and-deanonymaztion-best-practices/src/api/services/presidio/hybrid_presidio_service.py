import logging
from timeit import default_timer as timer
from typing import List, Tuple
from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine, OperatorConfig, OperatorResult
from presidio_analyzer.nlp_engine import NlpEngineProvider
import requests

from services.presidio.presidio_service import PresidioService
from services.anonymizers.instance_counter_anonymizer import InstanceCounterAnonymizer
from services.anonymizers.instance_counter_deanonymizer import InstanceCounterDeanonymizer
from config.config import config

logger = logging.getLogger(__name__)


class HybridPresidioService(PresidioService):
    """ Presidio Service class that uses Presidio Analyzer via HTTP and Anonymizer as a Python library """
    
    def __init__(self):
        self.analyzer_base_url = config.Presidio.analyzer_url

        self.anonymizer = AnonymizerEngine()
        self.anonymizer.add_anonymizer(InstanceCounterAnonymizer)
        self.deanonymizer = DeanonymizeEngine()
        self.deanonymizer.add_deanonymizer(InstanceCounterDeanonymizer)

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
            analyzer_result_json = analyze_response.json()
            analyzer_result = [RecognizerResult.from_json(item) for item in analyzer_result_json]
            logger.info(f"Analyze took {timer() - start_time:.3f} seconds for session_id: {session_id}")

            anonymizer_start_time = timer()
            anonymizer_entity_mapping = entity_mappings.copy() if entity_mappings is not None else dict()
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_result,
                operators={
                    "DEFAULT": OperatorConfig(
                        "entity_counter", {"entity_mapping": anonymizer_entity_mapping}
                    )
                },
            )
            logger.info(f"Anonymize took {timer() - anonymizer_start_time:.3f} seconds for session_id: {session_id}")

            total_time = timer() - start_time
            logger.info(f"Total processing time: {total_time:.3f} seconds for session_id: {session_id}")

            return anonymized_result.text, anonymizer_entity_mapping
        except Exception as e:
            logger.exception(f"Error in anonymize_text for session_id {session_id}")
            raise

    def deanonymize_text(self, session_id: str, text: str, entity_mappings: dict) -> str:
        """ Deanonymize the given text using Presidio Analyzer and Anonymizer engines """

        logger.info(f"Deanonymize text called with session_id: {session_id}")
        start_time = timer()

        try:
            entities = self.get_entities(entity_mappings, text)

            deanonymized = self.deanonymizer.deanonymize(
                text=text,
                entities=entities,
                operators=
                {"DEFAULT": OperatorConfig("entity_counter_deanonymizer", 
                                        params={"entity_mapping": entity_mappings})}
            )

            total_time = timer() - start_time
            logger.info(f"Total processing time: {total_time:.3f} seconds for session_id: {session_id}")
            
            return deanonymized.text
        except Exception as e:
            logger.exception(f"Error in deanonymize_text for session_id {session_id}")
            raise

    def get_entities(self, entity_mappings: dict, text: str) -> List[OperatorResult]:
        """ Get the entities from the entity mappings """

        entities = []
        for entity_type, entity_mapping in entity_mappings.items():
            for entity_value, entity_id in entity_mapping.items():
                start_index = 0
                while True:
                    start_index = text.find(entity_id, start_index)
                    if start_index == -1:
                        break
                    end_index = start_index + len(entity_id)
                    entities.append(OperatorResult(start_index, end_index, entity_type, entity_value, entity_id))
                    start_index += len(entity_id)
        return entities
