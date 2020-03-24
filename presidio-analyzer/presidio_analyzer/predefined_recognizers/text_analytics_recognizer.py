import json
from presidio_analyzer import RemoteRecognizer, RecognizerResult

from presidio_analyzer.predefined_recognizers.text_analytics_dal \
    import TextAnalyticsDal

SUPPORTED_ENTITIES = ["DATE_TIME", "EMAIL_ADDRESS", "IP_ADDRESS",
                      "PERSON", "PHONE_NUMBER", "LOCATION", "NRP"]
DEFAULT_EXPLANATION = "Identified as {} by Text Analytics"


class TextAnalyticsRecognizer(RemoteRecognizer):
    """
    Use Azure Text Analytics service to detect PII entities.
    """

    def __init__(self, text_analytics_dal=None):
        super().__init__(supported_entities=SUPPORTED_ENTITIES,
                         supported_language='en')

        if not text_analytics_dal:
            text_analytics_dal = TextAnalyticsDal(self.logger)
        self.dal = text_analytics_dal

    def load(self):
        pass

    def get_supported_entities(self):
        self.logger.debug("get_supported_entities was called")
        return SUPPORTED_ENTITIES

    def analyze(self, text, entities, nlp_artifacts=None):
        """
        This is the core method for analyzing text, assuming entities are
        the subset of the supported entities types.

        :param text: The text to be analyzed
        :param entities: The list of entities to be detected
        :param nlp_artifacts: Value of type NlpArtifacts.
        A group of attributes which are the result of
                              some NLP process over the matching text
        :return: list of RecognizerResult
        :rtype: [RecognizerResult]
        """
        self.logger.debug("analyze was called")
        try:
            data = self.dal.analyze_pii_data(text)
            return self.convert_to_analyze_response(data)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Failed to execute request to "
                              "Text Analytics. {}", e)
        return None

    def convert_to_analyze_response(self, json_str):
        result = []
        svc_response = json.loads(json_str)
        self.logger.debug(svc_response)
        if not svc_response['documents']:
            if svc_response['errors']:
                self.logger.error('Text Analytics returned error: {}'
                                  .format(str(svc_response['errors'])))
                return result

        for entity in svc_response['documents'][0]['entities']:
            recognizer_result = \
                RecognizerResult(TextAnalyticsRecognizer.
                                 __convert_to_presidio_type(entity['type']),
                                 entity['offset'],
                                 entity['offset'] + entity['length'],
                                 entity['score'],
                                 DEFAULT_EXPLANATION.format(entity['type']))
            result.append(recognizer_result)
        return result

    @staticmethod
    def __convert_to_presidio_type(ta_type):
        return_val = ta_type
        if ta_type == "DateTime":
            return_val = "DATE_TIME"
        if ta_type == "Email":
            return_val = "EMAIL_ADDRESS"
        if ta_type == "Person":
            return_val = "PERSON"
        if ta_type == "Organization":
            return_val = "NRP"
        if ta_type == "PhoneNumber":
            return_val = "PHONE_NUMBER"
        if ta_type == "EU GPS Coordinates":
            return_val = "LOCATION"
        if ta_type == "IP":
            return_val = "IP_ADDRESS"

        return return_val
