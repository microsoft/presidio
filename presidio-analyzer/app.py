from presidio_analyzer.presidio_logger import PresidioLogger
from presidio_analyzer.analyzer_engine import AnalyzerEngine
from flask import Flask, request
import json
import os

DEFAULT_PORT = "3000"

WELCOME_MESSAGE = r"""
 _______  _______  _______  _______ _________ ______  _________ _______
(  ____ )(  ____ )(  ____ \(  ____ \\__   __/(  __  \ \__   __/(  ___  )
| (    )|| (    )|| (    \/| (    \/   ) (   | (  \  )   ) (   | (   ) |
| (____)|| (____)|| (__    | (_____    | |   | |   ) |   | |   | |   | |
|  _____)|     __)|  __)   (_____  )   | |   | |   | |   | |   | |   | |
| (      | (\ (   | (            ) |   | |   | |   ) |   | |   | |   | |
| )      | ) \ \__| (____/\/\____) |___) (___| (__/  )___) (___| (___) |
|/       |/   \__/(_______/\_______)\_______/(______/ \_______/(_______)
"""


class Server:

    def __init__(self):
        self.logger = PresidioLogger(os.environ.get("PRESIDIO_LOGGER"))
        self.app = Flask(__name__)
        self.logger.info("Starting analyzer engine")
        self.engine = AnalyzerEngine()
        self.logger.info(WELCOME_MESSAGE)

        @self.app.route('/health')
        def health() -> str:
            """
            Basic health probe.  get ok + 200
            """
            return 'ok'

        @self.app.route("/analyze", methods=["POST"])
        def analyze():
            """
            Executes the analyzer function
            """
            # Parse the request params
            req_data = request.get_json()

            text = req_data.get("text")
            language = req_data.get("language")
            entities = req_data.get("entities")
            correlation_id = req_data.get("correlation_id")
            score_threshold = req_data.get("score_threshold")
            trace = req_data.get("trace")
            try:
                recognizer_result_list = self.engine.analyze(
                    text,
                    language,
                    correlation_id=correlation_id,
                    score_threshold=score_threshold,
                    entities=entities,
                    trace=trace)

                return json.dumps(recognizer_result_list, default=lambda o: o.to_json(),
                                  sort_keys=True, indent=4)
            except Exception as e:
                self.logger.error("A fatal error occurred during execution of AnalyzerEngine.analyze(). {}".format(e))
                return json.dumps({"Error": e}), 500

        @self.app.route("/recognizers", methods=["GET"])
        def recognizers():
            """
            Returns a list of supported recognizers
            """
            language = request.args.get('language')
            try:
                recognizers_list = self.engine.get_recognizers(language)
                names = [o.name for o in recognizers_list]
                return json.dumps(names)
            except Exception as e:
                self.logger.error("A fatal error occurred during execution of AnalyzerEngine.get_recognizers(). {}"
                                  .format(e))
                return json.dumps({"Error": e}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(port=port)
