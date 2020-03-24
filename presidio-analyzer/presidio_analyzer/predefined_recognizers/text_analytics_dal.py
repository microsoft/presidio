import http
import os


class TextAnalyticsDal:
    def __init__(self, logger, tolerate_errors=True):
        self.logger = logger
        self.tolerate_errors = tolerate_errors
        self.endpoint = os.environ.get('TEXT_ANALYTICS_ENDPOINT')
        self.key = os.environ.get('TEXT_ANALYTICS_KEY')

        if not self.endpoint:
            self.logger.error('TextAnalyticsRecognizer cannot'
                              ' work without an endpoint.')
            if not self.tolerate_errors:
                raise ValueError('TextAnalyticsRecognizer cannot'
                                 ' work without an endpoint.')
        if not self.key:
            self.logger.error('TextAnalyticsRecognizer cannot'
                              ' work without a key.')
            if not self.tolerate_errors:
                raise ValueError('TextAnalyticsRecognizer cannot'
                                 ' work without a key.')

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
        conn.request("POST", url='/text/analytics/v3.0-preview.1/'
                                 'entities/recognition/pii',
                     body=str(body), headers=self.headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data
