import os
from typing import List, Optional
import logging
import dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from presidio_analyzer import EntityRecognizer, RecognizerResult, AnalysisExplanation
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-streamlit")


class AzureAIServiceWrapper(EntityRecognizer):
    from azure.ai.textanalytics._models import PiiEntityCategory

    TA_SUPPORTED_ENTITIES = [r.value for r in PiiEntityCategory]

    def __init__(
        self,
        supported_entities: Optional[List[str]] = None,
        supported_language: str = "en",
        ta_client: Optional[TextAnalyticsClient] = None,
        ta_key: Optional[str] = None,
        ta_endpoint: Optional[str] = None,
    ):
        """
        Wrapper for the Azure Text Analytics client
        :param ta_client: object of type TextAnalyticsClient
        :param ta_key: Azure cognitive Services for Language key
        :param ta_endpoint: Azure cognitive Services for Language endpoint
        """

        if not supported_entities:
            supported_entities = self.TA_SUPPORTED_ENTITIES

        super().__init__(
            supported_entities=supported_entities,
            supported_language=supported_language,
            name="Azure AI Language PII",
        )

        self.ta_key = ta_key
        self.ta_endpoint = ta_endpoint

        if not ta_client:
            ta_client = self.__authenticate_client(ta_key, ta_endpoint)
        self.ta_client = ta_client

    @staticmethod
    def __authenticate_client(key: str, endpoint: str):
        ta_credential = AzureKeyCredential(key)
        text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, credential=ta_credential
        )
        return text_analytics_client

    def analyze(
        self, text: str, entities: List[str] = None, nlp_artifacts: NlpArtifacts = None
    ) -> List[RecognizerResult]:
        if not entities:
            entities = []
        response = self.ta_client.recognize_pii_entities(
            [text], language=self.supported_language
        )
        results = [doc for doc in response if not doc.is_error]
        recognizer_results = []
        for res in results:
            for entity in res.entities:
                if entity.category not in self.supported_entities:
                    continue
                analysis_explanation = AzureAIServiceWrapper._build_explanation(
                    original_score=entity.confidence_score,
                    entity_type=entity.category,
                )
                recognizer_results.append(
                    RecognizerResult(
                        entity_type=entity.category,
                        start=entity.offset,
                        end=entity.offset + len(entity.text),
                        score=entity.confidence_score,
                        analysis_explanation=analysis_explanation,
                    )
                )

        return recognizer_results

    @staticmethod
    def _build_explanation(
        original_score: float, entity_type: str
    ) -> AnalysisExplanation:
        explanation = AnalysisExplanation(
            recognizer=AzureAIServiceWrapper.__class__.__name__,
            original_score=original_score,
            textual_explanation=f"Identified as {entity_type} by Text Analytics",
        )
        return explanation

    def load(self) -> None:
        pass


if __name__ == "__main__":
    import presidio_helpers

    dotenv.load_dotenv()
    text = """
    Here are a few example sentences we currently support:

    Hello, my name is David Johnson and I live in Maine.
    My credit card number is 4095-2609-9393-4932 and my crypto wallet id is 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ.
    
    On September 18 I visited microsoft.com and sent an email to test@presidio.site,  from the IP 192.168.0.1.
    
    My passport: 191280342 and my phone number: (212) 555-1234.
    
    This is a valid International Bank Account Number: IL150120690000003111111 . Can you please check the status on bank account 954567876544?
    
    Kate's social security number is 078-05-1126.  Her driver license? it is 1234567A.
    """
    analyzer = presidio_helpers.analyzer_engine(
        model_path="Azure Text Analytics PII",
        ta_key=os.environ["TA_KEY"],
        ta_endpoint=os.environ["TA_ENDPOINT"],
    )
    analyzer.analyze(text=text, language="en")
