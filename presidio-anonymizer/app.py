"""REST API server for anonymizer."""
import logging
import os
from logging.config import fileConfig
from pathlib import Path
from typing import Tuple

from flask import Flask, request, jsonify, Response
from werkzeug.exceptions import BadRequest, HTTPException

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.deanonymize_engine import DeanonymizeEngine
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.services.app_entities_convertors import AppEntitiesConvertor

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
        self.anonymize = AnonymizerEngine()
        self.deanonymize = DeanonymizeEngine()
        self.logger.info(WELCOME_MESSAGE)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result."""
            return "Presidio Anonymizer service is up"

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            content = request.get_json()
            if not content:
                raise BadRequest("Invalid request json")

            anonymizers_config = AppEntitiesConvertor.operators_config_from_json(
                content.get("anonymizers")
            )
            analyzer_results = AppEntitiesConvertor.analyzer_results_from_json(
                content.get("analyzer_results"))
            anoymizer_result = self.anonymize.anonymize(
                text=content.get("text"),
                analyzer_results=analyzer_results,
                operators=anonymizers_config,
            )
            return Response(anoymizer_result.to_json(), mimetype="application/json")

        @self.app.route("/deanonymize", methods=["POST"])
        def deanonymize():
            content = request.get_json()
            if not content:
                raise BadRequest("Invalid request json")
            text = content.get("text")
            deanonymize_entities = AppEntitiesConvertor.deanonymize_entities_from_json(
                content)
            deanonymize_config = AppEntitiesConvertor.operators_config_from_json(
                content.get("deanonymizers"))
            decrypt_response = self.deanonymize.deanonymize(
                text=text, entities=deanonymize_entities, operators=deanonymize_config
            )
            return Response(decrypt_response.to_json(), mimetype="application/json")

        @self.app.route("/anonymizers", methods=["GET"])
        def anonymizers() -> Tuple[str, int]:
            """Return a list of supported anonymizers."""
            return jsonify(self.anonymize.get_anonymizers())

        @self.app.route("/deanonymizers", methods=["GET"])
        def deanonymizers() -> Tuple[str, int]:
            """Return a list of supported deanonymizers."""
            return jsonify(self.deanonymize.get_deanonymizers())

        @self.app.errorhandler(InvalidParamException)
        def invalid_param(err):
            self.logger.warning(
                f"Request failed with parameter validation error: {err.err_msg}"
            )
            return jsonify(error=err.err_msg), 422

        @self.app.errorhandler(HTTPException)
        def http_exception(e):
            return jsonify(error=e.description), e.code

        @self.app.errorhandler(Exception)
        def server_error(e):
            self.logger.error(f"A fatal error occurred during execution: {e}")
            return jsonify(error="Internal server error"), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
