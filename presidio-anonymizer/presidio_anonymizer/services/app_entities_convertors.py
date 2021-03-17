from typing import List, Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import RecognizerResult, AnonymizeConfig
from presidio_anonymizer.entities.engine import EncryptResult


class AppEntitiesConvertor:
    """Assisting class to convert API json entities to engine entities."""

    @staticmethod
    def analyzer_results_from_json(data: List[Dict]) -> List['RecognizerResult']:
        """
        Go over analyzer results, validate them and convert to List[AnalyzeResult].

        :param data: contains the anonymizers and analyzer_results_json
        """
        analyzer_results = []
        if data is None:
            raise InvalidParamException(
                "Invalid input, " "request must contain analyzer results"
            )
        for analyzer_result in data:
            analyzer_result = RecognizerResult.from_json(analyzer_result)
            analyzer_results.append(analyzer_result)
        return analyzer_results

    @staticmethod
    def anonymizer_configs_from_json(
            data: Dict
    ) -> Dict[str, 'AnonymizeConfig']:
        """
        Go over the anonymizers and get the relevant create anonymizer config entity.

        :param data: contains the list of configuration
        value - AnonynmizerConfig
        """
        anonymizers_config = {}
        anonymizers = data.get("anonymizers")
        if anonymizers is not None:
            for key, anonymizer_json in anonymizers.items():
                anonymizer_config = AnonymizeConfig.from_json(anonymizer_json)
                anonymizers_config[key] = anonymizer_config
        return anonymizers_config

    @staticmethod
    def decrypt_entities_from_json(json: Dict) -> List['EncryptResult']:
        """
        Create DecryptEntity list.

        :param json e.g.:
        {
            "text": text,
            "items": [{
                "start": 0,
                "end": len(text),
                "key": "1111111111111111",
            }],
        }
        :return: DecryptRequest
        """
        items = []
        decrypt_entity = json.get("items")
        if decrypt_entity:
            for result in decrypt_entity:
                items.append(EncryptResult.from_json(result))
        return items
