import http
import os


class TextAnalyticsDal:
    def __init__(self, logger, tolerate_errors=True):
        self.logger = logger
        self.tolerate_errors = tolerate_errors
        self.endpoint = os.environ.get('TEXT_ANALYTICS_ENDPOINT')
        self.key = os.environ.get('TEXT_ANALYTICS_KEY')
        self.api_path = os.environ.get('TEXT_ANALYTICS_API_PATH')
        self.failed_to_load = False

        if not self.endpoint:
            self.failed_to_load = True
            self.logger.error('TextAnalyticsRecognizer cannot'
                              ' work without an endpoint.')
            if not self.tolerate_errors:
                raise ValueError('TextAnalyticsRecognizer cannot'
                                 ' work without an endpoint.')
        if not self.key:
            self.failed_to_load = True
            self.logger.error('TextAnalyticsRecognizer cannot'
                              ' work without a key.')
            if not self.tolerate_errors:
                raise ValueError('TextAnalyticsRecognizer cannot'
                                 ' work without a key.')
        if not self.api_path:
            self.logger.info('Using default api path')
            self.api_path = '/text/analytics/v3.0-preview.1/' \
                            'entities/recognition/pii'

        self.headers = {
            # Request headers
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.key,
        }

    def analyze_pii_data(self, text):
        """
        Analyze the text using TextAnalytics PII service

        :param text: The text to be analyzed
        :return: json string
        """
        if self.failed_to_load:
            return None

        body = {
            "Documents": [
                {
                    "Language": "en",
                    "Id": "0",
                    "Text": text
                },
            ]
        }
        conn = http.client.HTTPSConnection(self.endpoint)
        conn.request("POST", url=self.api_path,
                     body=str(body), headers=self.headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data
