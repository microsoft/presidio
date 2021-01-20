class AnalyzerRequest:
    """
    Analyzer request data
    """

    def __init__(self, req_data):
        self.text = req_data.get("text")
        self.language = req_data.get("language")
        self.entities = req_data.get("entities")
        self.correlation_id = req_data.get("correlation_id")
        self.score_threshold = req_data.get("score_threshold")
        self.trace = req_data.get("trace")
