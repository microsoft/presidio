"""Wrapper to the list of AnalyzerResult which manipulates the list."""
from typing import List


class AnalyzerResults(List):
    """
    Receives the analyzer result list and manipulates it.

     The manipulation contains removal of unused results and sort by indices order.
     According to the logic of:
    - One PII - uses a given or default transformation to anonymize and replace the PII
    text entity.
    - Full overlap of PIIs - When one text have several PIIs, the PII with the higher
    score will be taken.
    Between PIIs with similar scores, the selection will be arbitrary.
    - One PII is contained in another - anonymizer will use the PII with larger text.
    - Partial intersection - both will be returned concatenated.
    """
    def to_sorted_set(self):
        """
        Manipulate the list.

        remove_dups - removes results which impact the same text and should be ignored.
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
        # uses __gt__ to sort the objects.
        analyzer_results = self._remove_dups()
        return sorted(analyzer_results)

    def _remove_dups(self):
        obj_set = set()
        for result_a in self:
            for index in range(len(self)):
                other = self.__getitem__(index)
                # not the same object
                if not result_a.__eq__(other):
                    # if there is an object containing result_a
                    # or an object with equal indices and higher score pass
                    if other.contains(result_a) or \
                            (result_a.equal_indices(
                                other) and result_a.score < other.score):
                        break
                if index == len(self) - 1:
                    obj_set.add(result_a)
        return obj_set
