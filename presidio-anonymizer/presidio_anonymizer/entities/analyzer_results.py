"""List wrapper of AnalyzerResult which sort the list using AnalyzerResult.__gt__."""
from presidio_anonymizer.entities import AnalyzerResult


class AnalyzerResults(list):
    """
    A class which provides operations over the analyzer result list..

     It includes removal of unused results and sort by indices order.
     Additional information about the rational of this class:
    - One PII - uses a given or default transformation to anonymize and replace the PII
    text entity.
    - Full overlap of PIIs - When one text have several PIIs, the PII with the higher
    score will be taken.
    Between PIIs with similar scores, the selection will be arbitrary.
    - One PII is contained in another - anonymizer will use the PII with larger text.
    - Partial intersection - both will be returned concatenated.
    """

    def to_sorted_set(self, reverse=False) -> set[AnalyzerResult]:
        """
        Create a sorted set from the list.

        _remove_conflicts method - removes results which impact the same text and
        should be ignored.
        using the logic:
        - One PII - uses a given or default transformation to anonymize and
        replace the PII text entity.
        - Full overlap of PIIs - When one text have several PIIs,
        the PII with the higher score will be taken.
        Between PIIs with similar scores, the selection will be arbitrary.
        - One PII is contained in another - anonymizer will use the PII
        with larger text.
        - Partial intersection - both will be returned concatenated.
        sort - Use __gt__ of AnalyzerResult to compare and sort
        :return: set
        """
        analyzer_results = self._remove_conflicts()
        return sorted(analyzer_results, reverse=reverse)

    def _remove_conflicts(self):
        """
        Iterate the list and create a set from it.

        Only insert results which are:
        1. Indices are not contained in other result.
        2. Have the same indices as other results but with larger score.
        :return: set
        """
        obj_set = set()
        for result_a in self:
            other_elements = AnalyzerResults(self)
            other_elements.remove(result_a)
            if not any([result_a.same_or_contained(other_element) for other_element in
                        other_elements]):
                obj_set.add(result_a)
        return obj_set
