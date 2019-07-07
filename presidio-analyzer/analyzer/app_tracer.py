import logging


class AppTracer:
    """This class handles app traces"""
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
        Writes interpretability trace
        :param request_id: A unique ID, to correlate across calls.
        :param trace_data: A string to write.
        :return:
        """
        if self.enabled:
            self.logger.info("[%s][%s]", request_id, trace_data)
