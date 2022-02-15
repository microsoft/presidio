from typing import Dict

from presidio_analyzer import PatternRecognizer


class AnalyzerRequest:
    """
    Analyzer request data.

    :param req_data: A request dictionary with the following fields:
        text: the text to analyze
        language: the language of the text
        entities: List of PII entities that should be looked for in the text.
        If entities=None then all entities are looked for.
        correlation_id: cross call ID for this request
        score_threshold: A minimum value for which to return an identified entity
        log_decision_process: Should the decision points within the analysis
        be logged
        return_decision_process: Should the decision points within the analysis
        returned as part of the response
    """

    def __init__(self, req_data: Dict):
        self.text = req_data.get("text")
        self.language = req_data.get("language")
        self.entities = req_data.get("entities")
        self.correlation_id = req_data.get("correlation_id")
        self.score_threshold = req_data.get("score_threshold")
        self.return_decision_process = req_data.get("return_decision_process")
        ad_hoc_recognizers = req_data.get("ad_hoc_recognizers")
        self.ad_hoc_recognizers = []
        if ad_hoc_recognizers:
            self.ad_hoc_recognizers = [
                PatternRecognizer.from_dict(rec) for rec in ad_hoc_recognizers
            ]
        self.context = req_data.get("context")
