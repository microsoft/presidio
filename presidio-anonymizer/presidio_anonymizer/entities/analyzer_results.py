"""A List of AnalyzerResult which sort the list using AnalyzerResult.__gt__."""
import logging
from typing import List

from presidio_anonymizer.entities import AnalyzerResult


class AnalyzerResults(list):
    """
    A class which provides operations over the analyzer result list..

     It includes removal of unused results and sort by indices order.
     Additional information about the rational of this class:
    - One PII - uses a given or default anonymizer to anonymize and replace the PII
    text entity.
    - Full overlap of PIIs - When one text have several PIIs, the PII with the higher
    score will be taken.
    Between PIIs with similar scores, the selection will be arbitrary.
    - One PII is contained in another - anonymizer will use the PII with larger text.
    - Partial intersection - both will be returned concatenated.
    """

    logger = logging.getLogger("presidio-anonymizer")

    def to_sorted_unique_results(self, reverse=False) -> List[AnalyzerResult]:
        """
        Create a sorted list with unique results from the list.

        _remove_conflicts method - removes results which impact the same text and
        should be ignored.
        using the logic:
        - One PII - uses a given or default anonymizer to anonymize and
        replace the PII text entity.
        - Full overlap of PIIs - When one text have several PIIs,
        the PII with the higher score will be taken.
        Between PIIs with similar scores, the selection will be arbitrary.
        - One PII is contained in another - anonymizer will use the PII
        with larger text.
        - Partial intersection - both will be returned concatenated.
        sort - Use __gt__ of AnalyzerResult to compare and sort
        :return: List
        """
        self.logger.debug("removing conflicts and sorting analyzer results list")
        analyzer_results = self._remove_conflicts()
        return sorted(analyzer_results, reverse=reverse)

    def _remove_conflicts(self):
        """
        Iterate the list and create a sorted unique results list from it.

        Only insert results which are:
        1. Indices are not contained in other result.
        2. Have the same indices as other results but with larger score.
        :return: List
        """
        unique_elements = []
        # This list contains all elements which we need to check a single result
        # against. If a result is dropped, it can also be dropped from this list
        # since it is intersecting with another result and we selected the other one.
        other_elements = AnalyzerResults(self)
        for result_a in self:
            other_elements.remove(result_a)
            if not any([result_a.has_conflict(other_element) for other_element in
                        other_elements]):
                other_elements.append(result_a)
                unique_elements.append(result_a)
            else:
                self.logger.debug(
                    f"removing element {result_a} from results list due to conflict")
        return unique_elements
