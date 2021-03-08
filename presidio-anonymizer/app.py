"""REST API server for anonymizer."""
import json
import logging
import os
from logging.config import fileConfig
from pathlib import Path
from typing import Tuple, Union

from flask import Flask, request, jsonify

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.anonymizer_decryptor import AnonymizerDecryptor
from presidio_anonymizer.entities import AnonymizerRequest
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.error_response import ErrorResponse

DEFAULT_PORT = "3000"

LOGGING_CONF_FILE = "logging.ini"

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
    """Flask server for anonymizer."""

    def __init__(self):
        fileConfig(Path(Path(__file__).parent, LOGGING_CONF_FILE))
        self.logger = logging.getLogger("presidio-anonymizer")
        self.logger.setLevel(os.environ.get("LOG_LEVEL", self.logger.level))
        self.app = Flask(__name__)
        self.logger.info("Starting anonymizer engine")
        self.engine = AnonymizerEngine()
        self.decryptor = AnonymizerDecryptor()
        self.logger.info(WELCOME_MESSAGE)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "Presidio Anonymizer service is up"

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            content = request.get_json()
            if not content:
                return ErrorResponse("Invalid request json").to_json(), 400

            anonymizers_config = AnonymizerRequest.get_anonymizer_configs_from_json(
                content
            )
            analyzer_results = AnonymizerRequest.handle_analyzer_results_json(content)
            text = self.engine.anonymize(
                text=content.get("text"),
                analyzer_results=analyzer_results,
                anonymizers_config=anonymizers_config,
            )
            return jsonify(result=text)

        @self.app.route("/decrypt", methods=["POST"])
        def decrypt() -> Union[str, Tuple[str, int]]:
            content = request.get_json()
            if not content:
                return ErrorResponse("Invalid request json").to_json(), 400
            decrypted_text = self.decryptor.decrypt(
                key=content.get("key"), text=content.get("text")
            )
            return jsonify(result=decrypted_text)

        @self.app.route("/anonymizers", methods=["GET"])
        def anonymizers() -> Tuple[str, int]:
            """Return a list of supported anonymizers."""
            return json.dumps(self.engine.get_anonymizers()), 200

        @self.app.errorhandler(InvalidParamException)
        def invalid_param(err):
            self.logger.warning(
                f"failed to anonymize text with validation error: {err.err_msg}"
            )
            return ErrorResponse(err.err_msg).to_json(), 422

        @self.app.errorhandler(Exception)
        def server_error(e):
            self.logger.error(f"A fatal error occurred during execution: {e}")
            return ErrorResponse("Internal server error").to_json(), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
