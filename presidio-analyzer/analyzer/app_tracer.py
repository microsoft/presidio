import logging


class AppTracer:
    """This class provides the ability to log/trace the system's decisions,
    such as which modules were used for detection,
    which logic was utilized, what results were given and potentially why.
    This can be useful for analyzing the detection accuracy of the system."""
    def __init__(self, enabled=True):

        logger = logging.getLogger('Interpretability')
        if not logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s][%(name)s][%(levelname)s]%(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            logger.setLevel(logging.INFO)
            logger.propagate = False

        self.logger = logger
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
