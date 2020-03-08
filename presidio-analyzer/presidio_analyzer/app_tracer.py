from presidio_analyzer import PresidioLogger


class AppTracer:
    """This class provides the ability to log/trace the system's decisions,
    such as which modules were used for detection,
    which logic was utilized, what results were given and potentially why.
    This can be useful for analyzing the detection accuracy of the system."""
    def __init__(self, enabled=True):

        self.logger = PresidioLogger('Interpretability')
        self.logger.set_level("INFO")
        self.enabled = enabled

    def trace(self, request_id, trace_data):
        """
        Writes a value associated with a decision
        for a specific request into the trace,
        for further inspection if needed.
        :param request_id: A unique ID, to correlate across calls.
        :param trace_data: A string to write.
        :return:
        """
        if self.enabled:
            self.logger.info("[%s][%s]", request_id, trace_data)
