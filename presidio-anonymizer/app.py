"""REST API server for anonymizer."""
import json
import logging
import os
from typing import Tuple

from flask import Flask, request

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerRequest
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.error_response import ErrorResponse

DEFAULT_PORT = "3000"


class Server:
    """Flask server for anonymizer."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.app = Flask(__name__)

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            content = request.get_json()
            if not content:
                return ErrorResponse("Invalid request json"), 400
            try:
                engine = AnonymizerEngine()
                data = AnonymizerRequest(content, engine.anonymizers())
                text = engine.anonymize(data)
            except InvalidParamException as e:
                self.logger.warning(
                    f"failed to anonymize text with validation error: {e.err_msg}")
                return e.err_msg, 422
            except Exception as e:
                self.logger.error(f"failed to anonymize text with error: {e}")
                return ErrorResponse("Internal server error"), 500
            return text

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result.  get ok + 200."""
            return "ok"

        @self.app.route("/anonymizers", methods=["GET"])
        def anonymizers() -> Tuple[str, int]:
            """Return a list of supported anonymizers."""
            try:
                return json.dumps(AnonymizerEngine().anonymizers()), 200
            except Exception as e:
                self.logger.error(
                    "A fatal error occurred "
                    "during execution of "
                    "anonymizers. {}".format(e)
                )
                return ErrorResponse(e.args[0]).to_json(), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
