from typing import List, Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import EncryptResult
from presidio_anonymizer.entities.engine import RecognizerResult, AnonymizerConfig


class AppEntitiesConvertor:
    """Assisting class to convert API json entities to engine entities."""

    @staticmethod
    def analyzer_results_from_json(data: List[Dict]) -> List['RecognizerResult']:
        """
        Go over analyzer results, validate them and convert to List[AnalyzeResult].

        :param data: contains the anonymizers and analyzer_results_json
        """
        if data is None:
            raise InvalidParamException(
                "Invalid input, " "request must contain analyzer results"
            )
        return [RecognizerResult.from_json(analyzer_result) for analyzer_result in data]

    @staticmethod
    def anonymizer_configs_from_json(
            data: Dict
    ) -> Dict[str, 'AnonymizerConfig']:
        """
        Go over the anonymizers and get the relevant create anonymizer config entity.

        :param data: contains the list of configuration
        value - AnonynmizerConfig
        """
        anonymizers = data.get("anonymizers")

        if anonymizers is not None:
            return {key: AnonymizerConfig.from_json(anonymizer_json) for
                    (key, anonymizer_json)
                    in anonymizers.items()}
        return {}

    @staticmethod
    def decrypt_entities_from_json(json: Dict) -> List['EncryptResult']:
        """
        Create DecryptEntity list.

        :param json:
        {
            "text": text,
            "encrypt_results": [{
                "start": 0,
                "end": 10,
                "key": "1111111111111111",
                "entity_type":"PHONE_NUMBER"
            }],
        }
        :return: List[EncryptResult]
        """
        items = []
        decrypt_entity = json.get("encrypt_results")
        if decrypt_entity:
            for result in decrypt_entity:
                items.append(EncryptResult.from_json(result))
        return items
