"""Manage getting the correct transformation from the list and returning default."""
from presidio_anonymizer.domain.analyzer_result import AnalyzerResult
from presidio_anonymizer.anonymizers import Replace


class Transformations(dict):
    """
    Get dictionary of transformations.

    If the desired transformation does not exist, it will be replaced with default.
    """

    def get_transformation(self, analyzer_result: AnalyzerResult):
        """
        Get the right transformation from the list.

        When transformation does not exist, we fall back to default.
        :param analyzer_result: the result we are going to do the transformation on
        :return: transformation
        """
        transformation = self.get(analyzer_result.entity_type)
        if not transformation:
            transformation = self.get("default")
            if not transformation:
                new_val = f"<{analyzer_result.entity_type}>"
                return {"type": "replace", "new_value": new_val, "anonymizer": Replace}
        return transformation
