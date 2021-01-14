# TODO this needs to be implemented currently a stab.
# TODO replace analyze_results with domain results
# Notice the document Omri created, it impacts the implementation
class Engine:
    def __init__(self,
                 text: str,
                 # TODO change to domain object
                 transformations: list[str],
                 # TODO change to domain object
                 analyze_results: list[str]):
        self.transformations = transformations
        self.analyze_results = analyze_results
        self.text = text
        self._end_point = len(text)

    def run(self):
        # TODO a loop that goes through the analyzer results from END to START! reverse.
        # TODO for each result, replace the old value with the new value
        # Make sure we handle partial intersections using the endpoint param
        # TODO dictionary with the transformations and fields
        # To map field to its transformation
        pass
