"""REST API server for anonymizer."""
import os

from flask import Flask, request

from presidio_anonymizer.entities import AnonymizerRequest

DEFAULT_PORT = "3000"


class Server:
    """Flask server for anonymizer."""

    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            content = request.get_json()
            if not content:
                return "Invalid request json", 400
            try:
                data = AnonymizerRequest(content)
            except Exception:
                # TODO add logger 2652
                return "Internal server error", 500
            return data, "Hello"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
