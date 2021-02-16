"""REST API server for image anonymizer."""
import logging
import os

from PIL import Image
from flask import Flask, request, make_response
from flasgger import Swagger
from presidio_image_anonymizer import ImageAnonymizerEngine
from presidio_image_anonymizer.entities import ErrorResponse
from presidio_image_anonymizer.entities import InvalidParamException
from presidio_image_anonymizer.entities.api_request_convertor import (
    get_json_data,
    image_to_byte_array,
    color_fill_string_to_value,
)

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
    """Flask server for image anonymizer."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-image-anonymizer")
        self.app = Flask(__name__)
        self.swagger = Swagger(
            self.app, template={"info": {"title": "Presidio Image Anonymizer API"}}
        )
        self.logger.info("Starting image anonymizer engine")
        self.engine = ImageAnonymizerEngine()
        self.logger.info(WELCOME_MESSAGE)

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result.

            ---
            responses:
              200:
                description: OK
                content:
                  text/plain:
                    schema:
                      type: string
            """
            return "Presidio Image Anonymizer service is up"

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            """Return an anonymized image."""
            params = get_json_data(request.form.get("data"))
            color_fill = color_fill_string_to_value(params)
            image_file = request.files.get("image")
            im = Image.open(image_file)

            anonymized_image = self.engine.anonymize(im, color_fill)

            img_byte_arr = image_to_byte_array(anonymized_image, im.format)
            return make_response(img_byte_arr)

        @self.app.errorhandler(InvalidParamException)
        def invalid_param(err):
            self.logger.warning(
                f"failed to anonymize image with validation error: {err.err_msg}"
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
