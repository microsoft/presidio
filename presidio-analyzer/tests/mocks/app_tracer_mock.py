import logging

from presidio_analyzer.app_tracer import AppTracer


class AppTracerMock(AppTracer):
    def __init__(self, enable_decision_process=True):
        logger = logging.getLogger("DecisionProcessMock")
        if not logger.handlers:
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s][%(name)s][%(levelname)s]%(message)s"
            )
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            logger.setLevel(logging.INFO)
            logger.propagate = False

        self.logger = logger
        self.last_trace = None
        self.enable_decision_process = enable_decision_process
        self.msg_counter = 0

    def trace(self, request_id, trace_data):
        """
        Writes the decision process trace.

        :param request_id: A unique ID, to correlate across calls.
        :param trace_data: A string to write.
        :return:
        """
        if self.enable_decision_process:
            self.last_trace = "[{}][{}]".format(request_id, trace_data)
            self.logger.info("[%s][%s]", request_id, trace_data)
            self.msg_counter = self.msg_counter + 1

    def get_last_trace(self):
        return self.last_trace

    def get_msg_counter(self):
        return self.msg_counter
