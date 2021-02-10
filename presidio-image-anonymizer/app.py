"""REST API server for image anonymizer."""
import io
import json
import logging
import os
from typing import Tuple, Union

from PIL import Image
from flask import Flask, request, make_response

from presidio_image_anonymizer import ImageAnonymizerEngine
from presidio_image_anonymizer.entities import ErrorResponse
from presidio_image_anonymizer.entities import InvalidParamException

DEFAULT_PORT = "3000"


class Server:
    """Flask server for image anonymizer."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-image-anonymizer")
        self.app = Flask(__name__)
        self.engine = ImageAnonymizerEngine()

        @self.app.route("/health")
        def health() -> str:
            """Return basic health probe result.  get ok + 200."""
            return "ok"

        @self.app.route("/anonymize", methods=["POST"])
        def anonymize():
            params = self._get_json_data(request.form.get('data'))
            color_fill = self._color_fill_string_to_value(
                params)
            image_file = request.files.get("image")
            im = Image.open(image_file)

            anonymized_image = self.engine.anonymize(im,
                                                     color_fill)

            img_byte_arr = self._image_to_byte_array(anonymized_image, im)
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

    def _get_json_data(self, data: str) -> dict:
        try:
            if not data:
                return {}
            return json.loads(data.replace("'", "\""))
        except Exception as e:
            self.logger.error(
                f"failed to parse json from string '{data}' with error {e}")
            raise InvalidParamException(f"Invalid json format \'{data}\'")

    def _color_fill_string_to_value(self, json_params: dict) -> Union[
        int, Tuple[int, int, int]]:
        filling_str = json_params.get("color_fill")
        try:
            if not filling_str:
                return 0, 0, 0
            filling_str_split = filling_str.split(',')
            if len(filling_str_split) == 1:
                return int(filling_str_split[0])
            return tuple(map(int, filling_str_split))
        except Exception as e:
            self.logger.error(
                f"failed to color fill '{filling_str}' with error {e}")
            raise InvalidParamException(f"Invalid color fill \'{filling_str}\'")

    @staticmethod
    def _image_to_byte_array(anonymized_image, im):
        img_byte_arr = io.BytesIO()
        anonymized_image.save(img_byte_arr,
                              format=im.format)
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr


if __name__ == "__main__":
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = Server()
    server.app.run(host="0.0.0.0", port=port)
