from presidio_anonymizer.domain.analyzer_result import AnalyzerResult


class Transformations(dict):
    def __init__(self, dict):
        if not dict:
            this = {}
        else:
            this = dict

    def get_transformation(self, analyzer_result: AnalyzerResult):
        transformation = self.get(analyzer_result.entity_type)
        if not transformation:
            new_val = f"<{analyzer_result.entity_type}>"
            return {"type": "replace", "new_value": new_val}
        return transformation
