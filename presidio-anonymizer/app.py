"""REST API server for anonymizer."""
import logging
import os

from flask import Flask, request

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerRequest
from presidio_anonymizer.entities import InvalidParamException

DEFAULT_PORT = "3000"


class Server:
    """Flask server for anonymizer."""

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            content = request.get_json()
            if not content:
                return "Invalid request json", 400
            try:
                data = AnonymizerRequest(content)
                text = AnonymizerEngine().anonymize(data)
            except InvalidParamException as e:
                logging.warning(
                    {f"failed to anonymize text with validation error: {e.err_msg}"})
                return e.err_msg, 422
            except Exception as e:
                logging.error({f"failed to anonymize text with error: {e}"})
                return "Internal server error", 500
            return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
