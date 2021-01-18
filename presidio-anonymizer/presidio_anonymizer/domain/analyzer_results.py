from typing import List

from presidio_anonymizer.domain.analyzer_result import AnalyzerResult


class AnalyzerResults:

    def __len__(self):
        return len(self.results)

    def __init__(self):
        self.results = []

    def append_result(self, result: AnalyzerResult):
        self.results.append(result)

    def to_sorted_set(self):
        # uses __gt__ to sort the objects.
        analyzer_results = self._remove_dups()
        return sorted(analyzer_results)

    def _remove_dups(self):
        obj_set = set()
        for result_a in self.results:
            for index in range(len(self.results)):
                other = self.results.__getitem__(index)
                # not the same object
                if not result_a.__eq__(other):
                    # if there is an object containing result_a
                    # or an object with equal indices and higher score pass
                    if other.contains(result_a) or \
                            (result_a.equal_indices(
                                other) and result_a.score < other.score):
                        break
                if index == len(self.results) - 1:
                    obj_set.add(result_a)
        return obj_set
