import logging


class AppTracerMock:

    def __init__(self, enable_interpretability=True):

        logger = logging.getLogger('InterpretabilityMock')
        if not logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                '[%(asctime)s][%(name)s][%(levelname)s]%(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            logger.setLevel(logging.INFO)
            logger.propagate = False

        self.logger = logger
        self.last_trace = None
        self.enable_interpretability = enable_interpretability

    def trace(self, request_id, trace_data):
        """
        Writes interpretability trace
        :param request_id: A unique ID, to correlate across calls.
        :param trace_data: A string to write.
        :return:
        """
        if self.enable_interpretability:
            self.last_trace = "[{}][{}]".format(request_id, trace_data)
            self.logger.info("[%s][%s]", request_id, trace_data)

    def get_last_trace(self):
        return self.last_trace
