from typing import Dict


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
        trace: Should tracing of the response occur or not. Tracing is used
        for results interpretability reasons.
    """

    def __init__(self, req_data: Dict):
        self.text = req_data.get("text")
        self.language = req_data.get("language")
        self.entities = req_data.get("entities")
        self.correlation_id = req_data.get("correlation_id")
        self.score_threshold = req_data.get("score_threshold")
        self.trace = req_data.get("trace")
        self.remove_interpretability_response = req_data.get(
            "remove_interpretability_response"
        )
