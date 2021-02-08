import logging


class AppTracer:
    """
    Allow logging/tracing the system's decisions.

    Relevant in cases where we want to know which modules were used for detection,
    which logic was utilized, what results were given and potentially why.
    This can be useful for analyzing the detection accuracy of the system.
    :param enabled: Whether tracing should be activated.
    """

    def __init__(self, enabled: bool = True):
        self.logger = logging.getLogger("decision_process")
        self.enabled = enabled

    def trace(self, request_id: str, trace_data: str) -> None:
        """
        Write a value associated with a decision for a specific request into the trace.

        Tracing for further inspection if needed.
        :param request_id: A unique ID, to correlate across calls.
        :param trace_data: A string to write to the log.
        """
        if self.enabled:
            self.logger.info("[%s][%s]", request_id, trace_data)
