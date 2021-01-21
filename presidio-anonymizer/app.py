import os

from flask import Flask, request

from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from presidio_anonymizer.entities.anonymizer_request import AnonymizerRequest
from presidio_anonymizer.entities.invalid_exception import InvalidParamException

DEFAULT_PORT = "3000"


class Server:
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
                return e.err, 400
            except Exception:
                # TODO add logger 2652
                return "Internal server error", 500
            return text


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(port=port)
