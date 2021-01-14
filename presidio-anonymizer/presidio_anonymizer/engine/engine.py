# TODO this needs to be implemented currently a stab.
# TODO replace analyze_results with domain results
# Notice the document Omri created, it impacts the implementation
class Engine:
    def __init__(self,
                 text: str,
                 analyze_results: list[str]):
        self.analyze_results = analyze_results
        self.text = text
        self.end_point = len(text)

    def run(self):
        # TODO a loop that goes through the analyzer results from END to START! reverse.
        # TODO for each result, replace the old value with the new value
        # Make sure we handle partial intersections using the endpoint param
        pass
